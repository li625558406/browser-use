# D:/AI/ai-scout/browser-use/backend/models/task.py

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Task(Base):
	"""任务模型"""

	__tablename__ = "tasks"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	target_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

	# 外键关联
	prompt_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("prompts.id"), nullable=True)
	llm_config_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("llm_configs.id"), nullable=True)

	# 调度配置
	schedule_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=False)  # once/daily/weekly/custom
	schedule_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

	# 浏览器配置
	browser_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=False)  # connect/profile
	profile_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

	# 数据控制
	max_items: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

	# 登录配置
	requires_login: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否需要登录

	# 状态
	is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

	# 任务依赖
	depends_on: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)

	# 时间戳
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	# 关系
	prompt = relationship("Prompt", back_populates="tasks", foreign_keys=[prompt_id])
	llm_config = relationship("LLMConfig", back_populates="tasks")
	executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")

	# 自引用（任务依赖）
	depends_on_task = relationship("Task", remote_side=[id], foreign_keys=[depends_on])
	dependent_tasks = relationship("Task", foreign_keys=[depends_on], overlaps="depends_on_task")

	def __repr__(self) -> str:
		return f"<Task(id={self.id}, name='{self.name}', enabled={self.is_enabled})>"
