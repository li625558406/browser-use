# D:/AI/ai-scout/browser-use/backend/services/task_executor.py

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from browser_use.agent.service import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession

from backend.database import async_session_maker
from backend.models.execution import TaskExecution
from backend.models.task import Task
from backend.utils.logger import logger

logger = logging.getLogger(__name__)


class TaskExecutor:
	"""任务执行器 - 负责执行单个任务"""

	def __init__(self, task: Task):
		self.task = task
		self.execution: TaskExecution | None = None
		self.browser_session: BrowserSession | None = None
		self._stopped = False
		self._session: AsyncSession | None = None

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

			# 创建 LLM
			llm = self._create_llm(llm_config)

			# 创建并运行 Agent
			agent = Agent(
				task=task_prompt,
				llm=llm,
				browser_session=self.browser_session,
			)

			# 执行任务
			logger.info(f"Agent 开始执行任务: {task_prompt[:100]}...")
			history = await agent.run(max_steps=100)

			# 获取最终结果
			final_result = history.final_result() or "任务执行完成"

			# 任务执行成功
			await self._complete_execution(status="success", output=str(final_result))

			logger.info(f"任务执行成功: {self.task.name}")

		except Exception as e:
			logger.error(f"任务执行失败: {self.task.name}, 错误: {e}", exc_info=True)
			await self._complete_execution(
				status="failed",
				error_message=str(e),
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

		return prompt

	async def _init_browser_session(self):
		"""初始化浏览器会话"""
		if self.task.browser_mode == "connect":
			# CDP 连接模式
			cdp_url = "http://localhost:9222"  # 默认 CDP 端口
			self.browser_session = BrowserSession(
				cdp_url=cdp_url,
			)
			logger.info(f"使用 CDP 连接模式: {cdp_url}")

		else:
			# Chrome 配置模式
			profile = BrowserProfile()

			if self.task.profile_name:
				# 设置用户数据目录
				profile.user_data_dir = str(self._get_chrome_user_data_dir())
				# BrowserProfile 使用 profile_directory 而不是 profile_name
				# Chrome 的配置目录名称: "Default", "Profile 1", "Profile 2", etc.
				if self.task.profile_name == "Default":
					profile.profile_directory = "Default"
				elif self.task.profile_name.startswith("Profile"):
					profile.profile_directory = self.task.profile_name
				else:
					# 如果用户输入的是 "Profile 1"，需要转换为 "Profile 1"
					profile.profile_directory = self.task.profile_name

			self.browser_session = BrowserSession(
				browser_profile=profile,
				headless=False,
			)
			logger.info(f"使用 Chrome 配置模式: {self.task.profile_name}")

		# 启动浏览器
		await self.browser_session.start()

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

			# Ollama 可能需要调整 base_url
			if llm_config.base_url:
				llm_kwargs["base_url"] = llm_config.base_url

			return ChatOllama(**llm_kwargs)

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
		if self.execution:
			session = await self._get_session()
			self.execution.status = status
			self.execution.completed_at = datetime.now()
			self.execution.log_content = output

			if error_message:
				self.execution.error_message = error_message

			await session.commit()

	async def _cleanup(self):
		"""清理资源"""
		if self.browser_session:
			try:
				await self.browser_session.stop()
				logger.info("浏览器已关闭")
			except Exception as e:
				logger.error(f"关闭浏览器时出错: {e}")

	async def stop(self):
		"""停止任务执行"""
		self._stopped = True
		if self.browser_session:
			try:
				await self.browser_session.stop()
			except Exception as e:
				logger.error(f"停止浏览器时出错: {e}")
