# D:/AI/ai-scout/browser-use/backend/models/execution.py

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class TaskExecution(Base):
	"""任务执行记录模型"""

	__tablename__ = "task_executions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
	status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending/running/success/failed
	started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
	completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
	error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	log_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	screenshot_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

	# 关系
	task = relationship("Task", back_populates="executions")
	data_records = relationship("ExecutionData", back_populates="execution", cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"<TaskExecution(id={self.id}, task_id={self.task_id}, status='{self.status}')>"


class ExecutionData(Base):
	"""采集数据模型"""

	__tablename__ = "execution_data"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	execution_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_executions.id"), nullable=False)
	data_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

	# 关系
	execution = relationship("TaskExecution", back_populates="data_records")

	def __repr__(self) -> str:
		return f"<ExecutionData(id={self.id}, execution_id={self.execution_id}, type='{self.data_type}')>"
