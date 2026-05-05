# D:/AI/ai-scout/browser-use/backend/services/task_executor.py

import asyncio
import json
import logging
import os
import shutil
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from browser_use.agent.service import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession

from backend.database import async_session_maker
from backend.models.execution import TaskExecution
from backend.models.task import Task
from backend.utils.logger import logger
from backend.services.browser_service import BrowserService
from backend.services.domain_registry import is_domain_logged_in, mark_domain_logged_in


class TaskExecutor:
	"""任务执行器 - 负责执行单个任务"""

	def __init__(self, task: Task):
		self.task = task
		self.execution: TaskExecution | None = None
		self.browser_session: BrowserSession | None = None
		self._stopped = False
		self._session: AsyncSession | None = None
		self._chrome_process: subprocess.Popen | None = None
		self._waiting_for_login = False  # 是否等待用户登录
		self._agent = None  # 保存 agent 实例以便恢复执行
		self._task_prompt = None  # 保存任务提示
		self._llm_config = None  # 保存 LLM 配置
		self._step_logs: list[dict] = []  # 收集执行步骤日志

	async def _get_session(self) -> AsyncSession:
		"""获取独立的数据库 session"""
		if self._session is None:
			self._session = async_session_maker()
		return self._session

	async def _close_session(self):
		"""关闭数据库 session"""
		if self._session:
			await self._session.close()
			self._session = None

	async def execute(self) -> TaskExecution:
		"""执行任务并返回执行记录"""
		session = await self._get_session()

		# 创建执行记录
		self.execution = TaskExecution(
			task_id=self.task.id,
			status="running",
			started_at=datetime.now(),
		)
		session.add(self.execution)
		await session.commit()
		await session.refresh(self.execution)

		logger.info(f"开始执行任务: {self.task.name} (执行ID: {self.execution.id})")

		try:
			# 获取任务配置
			prompt_content = await self._get_prompt_content()
			llm_config = await self._get_llm_config()

			if not prompt_content:
				raise ValueError("未找到 Prompt 模板")

			if not llm_config:
				raise ValueError("未找到 LLM 配置")

			# 构建完整的任务提示
			task_prompt = self._build_task_prompt(prompt_content)

			# 初始化浏览器会话
			await self._init_browser_session()

			# 如果有目标 URL，检查登录状态
			if self.task.target_url:
				domain = self._extract_domain(self.task.target_url)
				logger.info(f"检查域名 '{domain}' 的登录状态...")

				# 检查是否需要登录
				if not self.task.requires_login:
					logger.info(f"任务设置为不需要登录，直接执行任务")
					await self._run_agent(task_prompt, llm_config)
				elif is_domain_logged_in(domain):
					# 域名已登录过，跳过等待登录步骤
					logger.info(f"域名 '{domain}' 已登录过，跳过等待登录步骤，直接执行任务")
					await self._run_agent(task_prompt, llm_config)
				else:
					# 首次访问此域名，等待用户登录
					# 先导航到 URL，让用户看到页面并登录
					logger.info(f"域名 '{domain}' 首次访问，导航到页面并等待用户登录...")
					await self._navigate_to_url(self.task.target_url)

					await self._set_execution_status("waiting_for_login")
					self._waiting_for_login = True
					self._task_prompt = task_prompt
					self._llm_config = llm_config
					logger.info(f"等待用户登录网站: {self.task.target_url}")
					return self.execution

			# 没有 URL，直接执行
			logger.info("无目标 URL，直接执行任务")
			await self._run_agent(task_prompt, llm_config)

		except Exception as e:
			logger.error(f"任务执行失败: {self.task.name}, 错误: {e}", exc_info=True)
			await self._complete_execution(
				status="failed",
				error_message=traceback.format_exc(),
			)
			raise

		finally:
			# 清理浏览器资源
			await self._cleanup()
			# 关闭数据库 session
			await self._close_session()

		return self.execution

	async def _get_prompt_content(self) -> str | None:
		"""获取 Prompt 模板内容"""
		if not self.task.prompt_id:
			return None

		from backend.models.prompt import Prompt

		session = await self._get_session()
		prompt = await session.get(Prompt, self.task.prompt_id)
		return prompt.content if prompt else None

	async def _get_llm_config(self):
		"""获取 LLM 配置"""
		if not self.task.llm_config_id:
			return None

		from backend.models.llm_config import LLMConfig

		session = await self._get_session()
		config = await session.get(LLMConfig, self.task.llm_config_id)
		return config

	def _build_task_prompt(self, prompt_content: str) -> str:
		"""构建完整的任务提示"""
		# 替换变量
		prompt = prompt_content
		if self.task.target_url:
			prompt = prompt.replace("{{url}}", self.task.target_url)

		# 如果需要目标数据，可以从任务描述中提取
		if self.task.description:
			prompt = prompt.replace("{{target_data}}", self.task.description)

		# 替换最大采集数量（如果没有设置则使用默认值 100）
		max_items = self.task.max_items if self.task.max_items is not None else 100
		prompt = prompt.replace("{{max_items}}", str(max_items))

		return prompt

	async def _run_agent(self, task_prompt: str, llm_config):
		"""运行 Agent 执行任务"""
		# 创建 LLM
		llm = self._create_llm(llm_config)
		self._step_logs = []
		self._stopped = False

		# 停止回调 - 检查是否需要停止
		async def should_stop() -> bool:
			"""Callback checked by agent on each step."""
			return self._stopped

		# 步骤回调 - 收集执行步骤
		def on_new_step(state_summary, agent_output, step_index):
			try:
				step_info = {
					"step": step_index + 1,
					"goal": agent_output.next_goal or "",
					"url": getattr(state_summary, 'url', ''),
					"title": getattr(state_summary, 'title', ''),
					"actions": [],
				}
				for action in agent_output.action:
					action_type = getattr(action, 'action_type', str(type(action).__name__))
					if hasattr(action, 'model_dump'):
						params = str(action.model_dump(exclude_none=True))
					else:
						params = str(action)
					step_info["actions"].append({
						"type": action_type,
						"params": params,
					})
				self._step_logs.append(step_info)
				logger.info(f"Step {step_index + 1}: {agent_output.next_goal}")
			except Exception as e:
				logger.warning(f"Failed to capture step log: {e}")

		# 创建并运行 Agent
		# Ollama 本地模型响应较慢，增加超时时间
		llm_timeout = 300 if llm_config.provider == "ollama" else 90

		agent = Agent(
			task=task_prompt,
			llm=llm,
			browser_session=self.browser_session,
			register_should_stop_callback=should_stop,
			register_new_step_callback=on_new_step,
			llm_timeout=llm_timeout,
		)
		self._agent = agent

		# 执行任务
		logger.info(f"Agent 开始执行任务: {task_prompt[:100]}...")
		try:
			history = await agent.run(max_steps=100)
		except InterruptedError:
			# Agent 被停止
			logger.info(f"任务被用户手动停止: {self.task.name}")
			log_content = json.dumps(self._step_logs, ensure_ascii=False, indent=2) if self._step_logs else None
			await self._complete_execution(status="stopped", output=log_content)
			return

		# 获取最终结果
		# 检查 Agent 是否真正成功完成
		# 如果 step_logs 为空或结果只是 fallback 文本，说明 Agent 早期失败
		final_result = history.final_result()
		is_successful = history.is_successful()
		has_steps = len(self._step_logs) > 0

		# 判断任务是否真正成功
		if not has_steps or not is_successful:
			# Agent 早期失败或没有完成任何步骤
			error_msg = final_result or "Agent 执行失败：连续操作失败，未完成任何有效步骤"
			logger.error(f"任务执行失败: {self.task.name}, 错误: {error_msg}")
			log_content = json.dumps(self._step_logs, ensure_ascii=False, indent=2) if self._step_logs else None
			await self._complete_execution(status="failed", output=log_content, error_message=error_msg)
			return

		# Agent 成功完成
		result_text = final_result or "任务执行完成"
		log_content = json.dumps(self._step_logs, ensure_ascii=False, indent=2)
		full_log = f"=== 最终结果 ===\n{result_text}\n\n=== 执行步骤 ===\n{log_content}"

		# 保存成功状态到数据库
		await self._complete_execution(status="success", output=full_log)

		if self.task.target_url:
			domain = self._extract_domain(self.task.target_url)
			mark_domain_logged_in(domain)

		logger.info(f"任务执行成功: {self.task.name}")

	async def _init_browser_session(self):
		"""Initialize browser session - always use CDP mode with temporary Chrome."""
		# Clean up any existing browser session first
		if self.browser_session:
			try:
				await self.browser_session.stop()
				logger.info("Cleaned up existing browser session")
			except Exception as e:
				logger.warning(f"Error cleaning up existing session: {e}")
			self.browser_session = None

		# 使用固定端口 9222
		port = 9222

		# 启动临时 Chrome（CDP 模式）
		await self._start_temp_chrome(port)

		# 连接到 CDP 端口
		cdp_url = f"http://localhost:{port}"
		profile = BrowserProfile(
			cdp_url=cdp_url,
			is_local=False,
		)
		self.browser_session = BrowserSession(
			browser_profile=profile,
		)
		logger.info(f"已创建 BrowserSession，连接到 Chrome CDP: {cdp_url}")

		# 启动浏览器会话（仅 CDP 连接）
		await self.browser_session.start()
		logger.info("BrowserSession started successfully")

		# Wait for browser to be fully ready with a timeout
		# The key thing we need is agent_focus_target_id to be set
		max_retries = 30  # 15 seconds total
		for i in range(max_retries):
			if self.browser_session.agent_focus_target_id:
				logger.info(f"Browser ready, agent focus on tab {self.browser_session.agent_focus_target_id[-8:]}")
				break
			
			# After 2 seconds, try to manually trigger focus if we have targets but no focus
			if i == 4 and not self.browser_session.agent_focus_target_id:
				if self.browser_session.session_manager:
					targets = self.browser_session.session_manager.get_all_page_targets()
					if targets:
						logger.info(f"Found {len(targets)} target(s) but no focus, setting focus to first target")
						# Manually dispatch focus event
						from browser_use.browser.events import AgentFocusChangedEvent
						try:
							await self.browser_session.event_bus.dispatch(AgentFocusChangedEvent(
								target_id=targets[0].target_id,
								url=targets[0].url
							))
							logger.info(f"Manually dispatched focus event to {targets[0].target_id[-8:]}")
						except Exception as e:
							logger.warning(f"Failed to dispatch focus event: {e}")
			
			await asyncio.sleep(0.5)
		else:
			logger.warning("agent_focus_target_id not set after 15 seconds, but continuing")

	async def _start_temp_chrome(self, port: int):
		"""Start Chrome with domain-based persistent profile."""
		import httpx

		# 提取域名用于配置目录
		domain = "default"
		if self.task.target_url:
			domain = self._extract_domain(self.task.target_url)

		profile_dir = self._get_profile_dir(domain)
		# 转换为绝对路径
		profile_dir = profile_dir.resolve()
		logger.info(f"使用域名配置目录: {profile_dir}")

		# Check if CDP is already available
		result = await BrowserService.test_connection(port)
		if result:
			logger.info(f"Chrome CDP already available on port {port}")
			return

		# Check for existing Chrome processes that might be blocking the port
		try:
			import psutil
			for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
				try:
					if proc.info['name'] and 'chrome' in proc.info['name'].lower():
						cmdline = proc.info['cmdline']
						if cmdline and f'--remote-debugging-port={port}' in ' '.join(cmdline):
							logger.warning(f"发现已有Chrome进程使用端口 {port} (PID: {proc.info['pid']})")
							logger.info("尝试使用现有的Chrome实例...")
							# Don't start new Chrome, just use existing one
							return
				except (psutil.NoSuchProcess, psutil.AccessDenied):
					continue
		except ImportError:
			logger.warning("psutil未安装，无法检查现有Chrome进程")
		except Exception as e:
			logger.warning(f"检查Chrome进程时出错: {e}")

		# Find Chrome executable
		chrome_path = self._get_chrome_path()
		logger.info(f"Chrome 可执行文件路径: {chrome_path}")

		# Build Chrome args with persistent profile
		args = [
			chrome_path,
			f"--remote-debugging-port={port}",
			f"--user-data-dir={profile_dir}",
			"--no-first-run",
			"--no-default-browser-check",
			"--disable-background-networking",
			"--disable-background-timer-throttling",
			"--disable-backgrounding-occluded-windows",
			"--disable-breakpad",
			"--disable-client-side-phishing-detection",
			"--disable-default-apps",
			"--disable-dev-shm-usage",
			"--disable-extensions",
			"--disable-features=TranslateUI",
			"--disable-hang-monitor",
			"--disable-ipc-flooding-protection",
			"--disable-popup-blocking",
			"--disable-prompt-on-repost",
			"--disable-renderer-backgrounding",
			"--disable-sync",
			"--force-color-profile=srgb",
			"--metrics-recording-only",
			"--enable-automation",
			"--password-store=basic",
			"--use-mock-keychain",
			"--about-blank",  # Start with blank page instead of welcome screen
		]

		logger.info(f"启动Chrome (配置: {domain}): {' '.join(args)}")

		# Start Chrome with stderr capture for debugging
		self._chrome_process = subprocess.Popen(
			args,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.PIPE,
			close_fds=True
		)
		logger.info(f"Chrome已启动 (PID: {self._chrome_process.pid})，等待CDP可用...")

		# Wait for CDP
		await self._wait_for_cdp(port)

	@staticmethod
	def _extract_domain(url: str) -> str:
		"""从 URL 中提取域名用于配置目录命名"""
		parsed = urlparse(url)
		domain = parsed.netloc
		if ':' in domain:
			domain = domain.split(':')[0]
		return domain

	def _get_profile_dir(self, domain: str) -> Path:
		"""获取域名对应的 Chrome 配置目录"""
		profile_dir = Path('data') / 'chrome_profiles' / domain
		profile_dir.mkdir(parents=True, exist_ok=True)
		return profile_dir

	def _get_chrome_user_data_dir(self) -> Path:
		"""获取 Chrome 用户数据目录"""
		import os

		# Windows
		if os.name == "nt":
			return Path(os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data"))
		# macOS
		elif os.name == "posix" and os.uname().sysname == "Darwin":
			return Path(os.path.expanduser("~/Library/Application Support/Google/Chrome"))
		# Linux
		else:
			return Path(os.path.expanduser("~/.config/google-chrome"))

	def _create_llm(self, llm_config):
		"""创建 LLM 实例"""
		provider = llm_config.provider

		# 通用参数
		llm_kwargs = {
			"model": llm_config.model,
			"temperature": llm_config.temperature,
			"max_tokens": llm_config.max_tokens,
		}

		# 添加可选参数
		if llm_config.api_key:
			llm_kwargs["api_key"] = llm_config.api_key
		if llm_config.base_url:
			llm_kwargs["base_url"] = llm_config.base_url

		# 根据提供商创建相应的 LLM 实例
		if provider == "deepseek":
			from browser_use.llm.deepseek.chat import ChatDeepSeek

			return ChatDeepSeek(**llm_kwargs)

		elif provider == "openai":
			from browser_use.llm.openai.chat import ChatOpenAI

			return ChatOpenAI(**llm_kwargs)

		elif provider == "anthropic":
			from browser_use.llm.anthropic.chat import ChatAnthropic

			return ChatAnthropic(**llm_kwargs)

		elif provider == "ollama":
			from browser_use.llm.ollama.chat import ChatOllama

			# Ollama 只支持 model 和 host 参数
			ollama_kwargs = {
				"model": llm_kwargs["model"],
			}
			# Ollama 使用 host 而不是 base_url，且不需要 /v1 后缀
			if llm_config.base_url:
				host = llm_config.base_url.rstrip("/")
				# 移除 /v1 后缀（Ollama 的 OpenAI 兼容端点会加这个，但原生客户端不需要）
				if host.endswith("/v1"):
					host = host[:-3]
				ollama_kwargs["host"] = host

			return ChatOllama(**ollama_kwargs)

		elif provider == "openai_compatible":
			# 使用 OpenAI 类，但自定义 base_url
			from browser_use.llm.openai.chat import ChatOpenAI

			return ChatOpenAI(**llm_kwargs)

		else:
			raise ValueError(f"不支持的 LLM 提供商: {provider}")

	async def _complete_execution(
		self,
		status: str,
		output: str | None = None,
		error_message: str | None = None,
	):
		"""完成执行记录"""
		if self.execution and self.execution.id:
			session = await self._get_session()
			# Reload from database to avoid session issues
			from backend.models.execution import TaskExecution
			execution = await session.get(TaskExecution, self.execution.id)
			if execution:
				execution.status = status
				execution.completed_at = datetime.now()
				execution.log_content = output

				if error_message:
					execution.error_message = error_message

				await session.commit()
				# Update our reference
				self.execution.status = status
				self.execution.completed_at = execution.completed_at
		elif self.execution:
			# No ID yet (shouldn't happen in normal flow)
			session = await self._get_session()
			self.execution.status = status
			self.execution.completed_at = datetime.now()
			self.execution.log_content = output

			if error_message:
				self.execution.error_message = error_message

			await session.commit()

	async def _cleanup(self):
		"""Clean up resources - keep Chrome running for user to view results."""
		# Close browser session (CDP connection only, not the browser)
		if self.browser_session:
			try:
				await self.browser_session.stop()
				logger.info("Browser session closed (Chrome remains open)")
			except Exception as e:
				logger.error(f"Error closing browser session: {e}")

		# Don't close Chrome - let it stay open for user to see results
		if self._chrome_process:
			poll_result = self._chrome_process.poll()
			if poll_result is None:
				logger.info(f"Chrome (PID: {self._chrome_process.pid}) remains running for manual use")
			self._chrome_process = None

	async def stop(self):
		"""停止任务执行"""
		self._stopped = True

		# 立即停止 agent
		if self._agent:
			self._agent.stop()

		# 停止浏览器会话
		if self.browser_session:
			try:
				await self.browser_session.stop()
			except Exception as e:
				logger.error(f"停止浏览器时出错: {e}")

	async def _set_execution_status(self, status: str):
		"""设置执行状态"""
		if self.execution and self.execution.id:
			session = await self._get_session()
			# Reload from database instead of refreshing existing instance
			from backend.models.execution import TaskExecution
			execution = await session.get(TaskExecution, self.execution.id)
			if execution:
				execution.status = status
				await session.commit()
				# Update our reference
				self.execution.status = status
		elif self.execution:
			# No ID yet, just set directly (shouldn't happen in normal flow)
			session = await self._get_session()
			self.execution.status = status
			await session.commit()

	async def _navigate_to_url(self, url: str):
		"""导航到指定 URL"""
		if not self.browser_session:
			raise RuntimeError("浏览器会话未初始化")

		# Wait for CDP client to be ready
		max_wait = 5
		for i in range(max_wait):
			if hasattr(self.browser_session, 'cdp_client') and self.browser_session.cdp_client is not None:
				break
			logger.info(f"等待 CDP 客户端初始化... ({i+1}/{max_wait})")
			await asyncio.sleep(1)
		else:
			raise RuntimeError("CDP 客户端初始化超时")

		# 使用 CDP 直接导航
		try:
			# Get the current target (tab)
			target_id = self.browser_session.cdp_client.target_id
			await self.browser_session.cdp_client.send.Page.navigate(url=url)
			logger.info(f"已通过 CDP 导航到: {url}")
		except Exception as e:
			logger.error(f"CDP 导航失败: {e}，尝试使用事件方式...")
			# Fallback to event-based navigation
			from browser_use.browser.events import NavigateToUrlEvent
			event = self.browser_session.event_bus.dispatch(NavigateToUrlEvent(url=url))
			await event

		# 等待页面加载
		await asyncio.sleep(2)

		logger.info(f"已导航到: {url}")

	async def _wait_for_cdp(self, port: int, max_wait: int = 15):
		"""Wait for CDP to be available."""
		import httpx

		for elapsed in range(0, max_wait, 1):
			await asyncio.sleep(1)

			# Check if process is still running
			if self._chrome_process:
				poll_result = self._chrome_process.poll()
				if poll_result is not None:
					# Read stderr to get Chrome error message
					stderr_output = ""
					if self._chrome_process.stderr:
						try:
							stderr_output = self._chrome_process.stderr.read().decode('utf-8', errors='ignore')
						except Exception:
							pass

					logger.error(f"Chrome进程已退出 (退出码: {poll_result})")
					if stderr_output:
						logger.error(f"Chrome 错误输出: {stderr_output}")
					raise RuntimeError(f"Chrome启动后立即退出 (退出码: {poll_result})")

			# Try to connect to CDP
			try:
				async with httpx.AsyncClient() as client:
					response = await client.get(f"http://localhost:{port}/json", timeout=1.0)
					if response.status_code == 200:
						logger.info(f"Chrome CDP 可用 (耗时 {elapsed + 1} 秒)")
						return
			except Exception:
				pass

			logger.info(f"等待 CDP 端口 {port}... ({elapsed + 1}/{max_wait}s)")

		raise RuntimeError(f"Chrome启动后CDP端口 {port} 不可用（等待了 {max_wait} 秒）")

	def _get_chrome_path(self) -> str:
		"""Get Chrome executable path."""
		possible_paths = [
			r"C:\Program Files\Google\Chrome\Application\chrome.exe",
			r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
			os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
		]

		for path in possible_paths:
			if os.path.exists(path):
				return path

		chrome_path = shutil.which("chrome.exe")
		if chrome_path:
			return chrome_path

		raise FileNotFoundError("无法找到Chrome可执行文件，请确保Chrome已安装")

	async def resume_execution(self):
		"""继续执行任务（用户登录后调用）"""
		if not self._waiting_for_login:
			raise RuntimeError("当前不在等待登录状态")

		if not self._task_prompt or not self._llm_config:
			raise RuntimeError("任务配置未保存，无法继续执行")

		# 检查浏览器会话是否仍然有效
		if not self.browser_session:
			logger.info("浏览器会话已关闭，重新初始化...")
			await self._init_browser_session()

		self._waiting_for_login = False

		# 重新加载 execution 以确保它在当前 session 中
		session = await self._get_session()
		from backend.models.execution import TaskExecution
		if self.execution and self.execution.id:
			execution = await session.get(TaskExecution, self.execution.id)
			if execution:
				self.execution = execution
		await self._set_execution_status("running")

		logger.info(f"用户已确认登录，继续执行任务: {self.task.name}")

		try:
			await self._run_agent(self._task_prompt, self._llm_config)
		except Exception as e:
			logger.error(f"任务执行失败: {self.task.name}, 错误: {e}", exc_info=True)
			await self._complete_execution(
				status="failed",
				error_message=traceback.format_exc(),
			)
			raise
		finally:
			# 清理浏览器资源
			await self._cleanup()
			# 关闭数据库 session
			await self._close_session()

