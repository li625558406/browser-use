# D:/AI/ai-scout/browser-use/backend/schemas/llm_config.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LLMConfigCreate(BaseModel):
    """创建 LLM 配置请求"""
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., pattern="^(deepseek|openai|anthropic|ollama|openai_compatible)$")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4096, ge=1, le=128000)
    is_default: bool = False


class LLMConfigUpdate(BaseModel):
    """更新 LLM 配置请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, pattern="^(deepseek|openai|anthropic|ollama|openai_compatible)$")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_default: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    """LLM 配置响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    api_key: Optional[str]  # 返回时只显示前几位
    base_url: Optional[str]
    model: str
    temperature: float
    max_tokens: int
    is_default: bool
    created_at: datetime
    updated_at: datetime


class LLMConfigTestRequest(BaseModel):
    """测试 LLM 配置请求"""
    provider: str
    api_key: Optional[str]
    base_url: Optional[str]
    model: str
