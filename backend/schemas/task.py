# D:/AI/ai-scout/browser-use/backend/schemas/task.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleConfig(BaseModel):
	"""调度配置"""
	type: str = Field(..., description="once/daily/weekly/custom")
	time: Optional[str] = Field(None, description="HH:MM 格式的时间")
	day_of_week: Optional[int] = Field(None, description="0-6, 0=周一")
	interval: Optional[int] = Field(None, description="间隔（分钟/小时/天）")
	cron: Optional[str] = Field(None, description="Cron 表达式")


class TaskCreate(BaseModel):
	"""创建任务请求"""
	name: str = Field(..., min_length=1, max_length=200)
	description: Optional[str] = None
	target_url: Optional[str] = None
	prompt_id: Optional[int] = None
	llm_config_id: Optional[int] = None
	schedule: ScheduleConfig
	max_items: Optional[int] = Field(None, ge=1, le=10000, description="最大采集数量")
	requires_login: Optional[bool] = Field(True, description="是否需要登录")
	# browser_mode 和 profile_name 不再由前端指定，默认使用 CDP 模式
	depends_on: Optional[int] = None


class TaskUpdate(BaseModel):
	"""更新任务请求"""
	name: Optional[str] = Field(None, min_length=1, max_length=200)
	description: Optional[str] = None
	target_url: Optional[str] = None
	prompt_id: Optional[int] = None
	llm_config_id: Optional[int] = None
	schedule: Optional[ScheduleConfig] = None
	is_enabled: Optional[bool] = None
	max_items: Optional[int] = None
	requires_login: Optional[bool] = None
	depends_on: Optional[int] = None


class TaskResponse(BaseModel):
	"""任务响应"""
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	description: Optional[str]
	target_url: Optional[str]
	prompt_id: Optional[int]
	llm_config_id: Optional[int]
	schedule_type: str
	schedule_config: Optional[dict]
	browser_mode: Optional[str]
	profile_name: Optional[str]
	is_enabled: bool
	max_items: Optional[int]
	requires_login: bool
	depends_on: Optional[int]
	created_at: datetime
	updated_at: datetime
