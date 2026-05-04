# D:/AI/ai-scout/browser-use/backend/config.py

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_encryption_key() -> str:
	"""获取或生成加密密钥"""
	key = os.getenv("ENCRYPTION_KEY")
	if not key:
		from cryptography.fernet import Fernet
		key = Fernet.generate_key().decode()
		print(f"Generated new encryption key: {key}")
		print("Please add this to your .env file as ENCRYPTION_KEY")
	return key


class Settings(BaseSettings):
	"""应用配置"""

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)

	# 加密
	encryption_key: str = Field(default_factory=get_encryption_key)

	# 数据库
	database_url: str = "sqlite:///data/database.db"

	# 后端
	backend_host: str = "0.0.0.0"
	backend_port: int = 8000

	# Chrome
	chrome_profile_path: str = ""
	chrome_cdp_port: int = 9242

	# 日志
	log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
	log_dir: str = "logs"

	# 调度器
	scheduler_max_workers: int = 3

	@property
	def data_dir(self) -> Path:
		return Path("data")

	@property
	def exports_dir(self) -> Path:
		return self.data_dir / "exports"

	@property
	def logs_dir(self) -> Path:
		return Path(self.log_dir)


settings = Settings()
