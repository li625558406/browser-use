# D:/AI/ai-scout/browser-use/backend/schemas/prompt.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
	"""创建 Prompt 请求"""
	name: str = Field(..., min_length=1, max_length=200)
	description: Optional[str] = None
	content: str = Field(..., min_length=1)
	category: Optional[str] = None
	variables: Optional[list[str]] = Field(default_factory=list)


class PromptUpdate(BaseModel):
	"""更新 Prompt 请求"""
	name: Optional[str] = Field(None, min_length=1, max_length=200)
	description: Optional[str] = None
	content: Optional[str] = Field(None, min_length=1)
	category: Optional[str] = None
	variables: Optional[list[str]] = None


class PromptResponse(BaseModel):
	"""Prompt 响应"""
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	description: Optional[str]
	content: str
	category: Optional[str]
	variables: Optional[list]
	version: int
	created_at: datetime
	updated_at: datetime
