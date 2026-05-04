# D:/AI/ai-scout/browser-use/backend/api/response.py

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
	"""统一 API 响应格式"""

	code: int = 0
	message: str = "success"
	data: T | None = None

	@classmethod
	def success(cls, data: T | None = None, message: str = "success") -> "ApiResponse[T]":
		return cls(code=0, message=message, data=data)

	@classmethod
	def error(cls, code: int, message: str, data: T | None = None) -> "ApiResponse[T]":
		return cls(code=code, message=message, data=data)


# 常用错误码
class ErrorCode:
	SUCCESS = 0
	INVALID_PARAMS = 1001
	NOT_FOUND = 1002
	ALREADY_EXISTS = 1003
	INTERNAL_ERROR = 5000
