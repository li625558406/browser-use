# D:/AI/ai-scout/browser-use/backend/dependencies.py

from typing import AsyncGenerator

from backend.database import async_session_maker, get_session as _get_session


async def get_session() -> AsyncGenerator:
	"""获取数据库会话（FastAPI 依赖）"""
	async for session in _get_session():
		yield session


async def get_db():
	"""获取数据库（别名）"""
	async for session in _get_session():
		yield session
