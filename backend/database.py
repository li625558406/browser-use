# D:/AI/ai-scout/browser-use/backend/database.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings


class Base(DeclarativeBase):
	"""ORM 基类"""
	pass


# 创建异步引擎
# SQLite 需要使用 aiosqlite
database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
	database_url,
	echo=settings.log_level == "DEBUG",
	connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
	engine,
	class_=AsyncSession,
	expire_on_commit=False,
)


async def init_db() -> None:
	"""初始化数据库"""
	# 确保数据目录存在
	settings.data_dir.mkdir(parents=True, exist_ok=True)

	# 导入所有模型以确保它们被注册
	try:
		from backend.models import task, prompt, llm_config, execution, browser_config
	except ImportError:
		# 模型尚未创建，跳过
		pass

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	"""获取数据库会话（依赖注入）"""
	async with async_session_maker() as session:
		yield session
