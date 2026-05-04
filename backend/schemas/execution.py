# D:/AI/ai-scout/browser-use/backend/schemas/execution.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskExecutionResponse(BaseModel):
	"""任务执行响应"""
	model_config = ConfigDict(from_attributes=True)

	id: int
	task_id: int
	task_name: str  # 添加任务名称
	status: str
	started_at: Optional[datetime]
	completed_at: Optional[datetime]
	error_message: Optional[str]
	screenshot_path: Optional[str]


class ExecutionDataResponse(BaseModel):
	"""采集数据响应"""
	model_config = ConfigDict(from_attributes=True)

	id: int
	execution_id: int
	data_type: Optional[str]
	content: Optional[str]
	source_url: Optional[str]
