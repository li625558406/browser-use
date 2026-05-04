# D:/AI/ai-scout/browser-use/backend/services/browser_service.py

from typing import List

from browser_use import Browser
from browser_use.browser.profile import BrowserProfile

from backend.models.browser_config import BrowserConfig
from backend.utils.chrome import get_available_profiles
from backend.utils.logger import logger


class BrowserService:
	"""浏览器服务"""

	@staticmethod
	def get_profiles() -> List[dict]:
		"""获取可用的 Chrome Profile 列表"""
		return get_available_profiles()

	@staticmethod
	async def create_browser(config: BrowserConfig) -> Browser:
		"""根据配置创建浏览器实例"""
		profile = BrowserProfile()

		# 配置 Profile
		if config.mode == "profile" and config.profile_path:
			profile.user_data_dir = config.profile_path

		# 配置 CDP
		if config.mode == "connect" and config.cdp_port:
			# 连接现有 Chrome
			pass  # browser-use 支持通过 CDP URL 连接

		# Headless 模式
		if config.headless:
			# browser-use 默认使用 headless
			pass

		# 代理
		if config.proxy_url:
			profile.proxy = config.proxy_url

		browser = Browser(
			browser_profile=profile,
		)

		return browser

	@staticmethod
	async def test_connection(cdp_port: int = 9242) -> bool:
		"""测试 Chrome CDP 连接"""
		try:
			import httpx

			response = await httpx.AsyncClient().get(f"http://localhost:{cdp_port}/json/version")
			return response.status_code == 200
		except Exception as e:
			logger.warning(f"Failed to connect to Chrome CDP: {e}")
			return False
