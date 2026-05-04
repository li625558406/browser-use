# D:/AI/ai-scout/browser-use/backend/models/browser_config.py

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class BrowserConfig(Base):
	"""浏览器配置模型"""

	__tablename__ = "browser_configs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(100), nullable=False)
	mode: Mapped[str] = mapped_column(String(20), nullable=False)  # connect/profile/standalone
	profile_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	headless: Mapped[bool] = mapped_column(Boolean, default=True)
	proxy_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	cdp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	def __repr__(self) -> str:
		return f"<BrowserConfig(id={self.id}, name='{self.name}', mode='{self.mode}')>"
