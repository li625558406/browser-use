# D:/AI/ai-scout/browser-use/backend/database.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings
from backend.utils.logger import logger


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


async def _ensure_columns():
	"""确保新列存在于现有表中（SQLite 兼容）"""
	async with engine.connect() as conn:
		def _check_and_add(sync_conn):
			inspector = inspect(sync_conn)

			# 检查 tasks 表
			table = "tasks"
			if inspector.has_table(table):
				existing = [col['name'] for col in inspector.get_columns(table)]
				new_columns = {
					'max_items': 'INTEGER',
					'requires_login': 'BOOLEAN DEFAULT 1',
				}
				for col_name, col_type in new_columns.items():
					if col_name not in existing:
						sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
						logger.info(f"Added column '{col_name}' to table '{table}'")
						sync_conn.commit()

		await conn.run_sync(_check_and_add)


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

	# 确保新列存在
	await _ensure_columns()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	"""获取数据库会话（依赖注入）"""
	async with async_session_maker() as session:
		yield session
