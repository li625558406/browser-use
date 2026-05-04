# D:/AI/ai-scout/browser-use/backend/schemas/browser_config.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BrowserConfigCreate(BaseModel):
	"""创建浏览器配置请求"""
	name: str = Field(..., min_length=1, max_length=100)
	mode: str = Field(..., pattern="^(connect|profile|standalone)$")
	profile_path: Optional[str] = None
	headless: bool = True
	proxy_url: Optional[str] = None
	cdp_port: Optional[int] = Field(None, ge=1, le=65535)


class BrowserConfigResponse(BaseModel):
	"""浏览器配置响应"""
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	mode: str
	profile_path: Optional[str]
	headless: bool
	proxy_url: Optional[str]
	cdp_port: Optional[int]
	created_at: datetime


class ChromeProfileInfo(BaseModel):
	"""Chrome Profile 信息"""
	name: str
	path: str
	avatar: Optional[str] = None


class BrowserStatusResponse(BaseModel):
	"""浏览器状态响应"""
	is_connected: bool
	cdp_url: Optional[str] = None
	profiles: list[ChromeProfileInfo]
