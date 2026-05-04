# D:/AI/ai-scout/browser-use/backend/models/prompt.py

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Prompt(Base):
	"""Prompt 模板模型"""

	__tablename__ = "prompts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	variables: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
	version: Mapped[int] = mapped_column(Integer, default=1)

	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	# 关系
	tasks = relationship("Task", back_populates="prompt", foreign_keys="Task.prompt_id")

	def __repr__(self) -> str:
		return f"<Prompt(id={self.id}, name='{self.name}', category='{self.category}')>"
