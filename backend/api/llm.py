# D:/AI/ai-scout/browser-use/backend/api/llm.py

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_db
from backend.models.llm_config import LLMConfig
from backend.schemas.llm_config import (
	LLMConfigCreate,
	LLMConfigResponse,
	LLMConfigTestRequest,
	LLMConfigUpdate,
)

router = APIRouter()


def mask_api_key(api_key: str | None) -> str | None:
	"""遮盖 API Key，只显示前 4 位和后 4 位"""
	if not api_key:
		return None
	if len(api_key) <= 8:
		return "****"
	return f"{api_key[:4]}...{api_key[-4:]}"


async def mask_config(config: LLMConfig) -> dict[str, Any]:
	"""将 LLMConfig 模型转换为响应字典，并遮盖敏感信息"""
	return {
		"id": config.id,
		"name": config.name,
		"provider": config.provider,
		"api_key": mask_api_key(config.api_key),
		"base_url": config.base_url,
		"model": config.model,
		"temperature": config.temperature,
		"max_tokens": config.max_tokens,
		"is_default": config.is_default,
		"created_at": config.created_at,
		"updated_at": config.updated_at,
	}


@router.get("", response_model=ApiResponse[list[LLMConfigResponse]])
async def list_llm_configs(db: AsyncSession = Depends(get_db)) -> ApiResponse[list[LLMConfigResponse]]:
	"""获取所有 LLM 配置列表"""
	result = await db.execute(select(LLMConfig).order_by(LLMConfig.is_default.desc(), LLMConfig.created_at.desc()))
	configs = result.scalars().all()

	masked_configs = [await mask_config(config) for config in configs]
	return ApiResponse.success(data=masked_configs)


@router.post("", response_model=ApiResponse[LLMConfigResponse], status_code=status.HTTP_201_CREATED)
async def create_llm_config(
	create_data: LLMConfigCreate, db: AsyncSession = Depends(get_db)
) -> ApiResponse[LLMConfigResponse]:
	"""创建新的 LLM 配置"""
	# 检查名称是否已存在
	existing = await db.execute(select(LLMConfig).where(LLMConfig.name == create_data.name))
	if existing.scalar_one_or_none():
		return ApiResponse.error(code=ErrorCode.ALREADY_EXISTS, message="配置名称已存在")

	# 如果设置为默认，需要取消其他配置的默认状态
	if create_data.is_default:
		await db.execute(update_stmt := delete(LLMConfig).where(LLMConfig.is_default == True))
		# 使用 update 语句将所有 is_default 设为 False
		from sqlalchemy import update
		await db.execute(update(LLMConfig).values(is_default=False))

	# 创建新配置
	new_config = LLMConfig(**create_data.model_dump())
	db.add(new_config)
	await db.commit()
	await db.refresh(new_config)

	return ApiResponse.success(data=await mask_config(new_config), message="创建成功")


@router.get("/{config_id}", response_model=ApiResponse[LLMConfigResponse])
async def get_llm_config(config_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[LLMConfigResponse]:
	"""获取指定 ID 的 LLM 配置详情"""
	result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
	config = result.scalar_one_or_none()

	if not config:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="配置不存在")

	return ApiResponse.success(data=await mask_config(config))


@router.put("/{config_id}", response_model=ApiResponse[LLMConfigResponse])
async def update_llm_config(
	config_id: int, update_data: LLMConfigUpdate, db: AsyncSession = Depends(get_db)
) -> ApiResponse[LLMConfigResponse]:
	"""更新指定 ID 的 LLM 配置"""
	result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
	config = result.scalar_one_or_none()

	if not config:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="配置不存在")

	# 检查名称是否与其他配置冲突
	if update_data.name and update_data.name != config.name:
		existing = await db.execute(select(LLMConfig).where(LLMConfig.name == update_data.name))
		if existing.scalar_one_or_none():
			return ApiResponse.error(code=ErrorCode.ALREADY_EXISTS, message="配置名称已存在")

	# 如果设置为默认，需要取消其他配置的默认状态
	if update_data.is_default is True and not config.is_default:
		from sqlalchemy import update
		await db.execute(update(LLMConfig).values(is_default=False))

	# 更新配置
	for field, value in update_data.model_dump(exclude_unset=True).items():
		setattr(config, field, value)

	await db.commit()
	await db.refresh(config)

	return ApiResponse.success(data=await mask_config(config), message="更新成功")


@router.delete("/{config_id}", response_model=ApiResponse[None])
async def delete_llm_config(config_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[None]:
	"""删除指定 ID 的 LLM 配置"""
	result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
	config = result.scalar_one_or_none()

	if not config:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="配置不存在")

	await db.delete(config)
	await db.commit()

	return ApiResponse.success(message="删除成功")


@router.post("/{config_id}/set-default", response_model=ApiResponse[LLMConfigResponse])
async def set_default_llm_config(config_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[LLMConfigResponse]:
	"""将指定配置设置为默认"""
	result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
	config = result.scalar_one_or_none()

	if not config:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="配置不存在")

	# 取消所有配置的默认状态
	from sqlalchemy import update
	await db.execute(update(LLMConfig).values(is_default=False))

	# 设置当前配置为默认
	config.is_default = True
	await db.commit()
	await db.refresh(config)

	return ApiResponse.success(data=await mask_config(config), message="已设置为默认配置")


@router.post("/{config_id}/test", response_model=ApiResponse[dict[str, Any]])
async def test_llm_config(config_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[dict[str, Any]]:
	"""测试 LLM 配置的连接"""
	result = await db.execute(select(LLMConfig).where(LLMConfig.id == config_id))
	config = result.scalar_one_or_none()

	if not config:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="配置不存在")

	# 构造测试请求
	test_request = LLMConfigTestRequest(
		provider=config.provider,
		api_key=config.api_key,
		base_url=config.base_url,
		model=config.model,
	)

	# 执行测试连接
	test_result = await test_llm_connection(test_request)

	if test_result["success"]:
		return ApiResponse.success(
			data={
				"provider": config.provider,
				"model": config.model,
				"latency_ms": test_result.get("latency_ms"),
			},
			message="连接测试成功",
		)
	else:
		return ApiResponse.error(code=ErrorCode.INTERNAL_ERROR, message=test_result.get("error", "连接测试失败"))


async def test_llm_connection(test_request: LLMConfigTestRequest) -> dict[str, Any]:
	"""测试 LLM 连接"""
	import time

	from openai import AsyncOpenAI

	try:
		# 构造客户端参数
		client_params: dict[str, Any] = {
			"api_key": test_request.api_key or "test",
			"timeout": 10.0,
			"max_retries": 1,
		}

		# 根据提供商设置 base_url
		if test_request.provider == "deepseek":
			client_params["base_url"] = test_request.base_url or "https://api.deepseek.com"
		elif test_request.provider == "openai":
			client_params["base_url"] = test_request.base_url
		elif test_request.provider == "anthropic":
			# Anthropic 不使用 OpenAI 客户端
			return {
				"success": False,
				"error": "Anthropic 提供商暂不支持测试连接",
			}
		elif test_request.provider == "ollama":
			client_params["base_url"] = test_request.base_url or "http://localhost:11434/v1"
		elif test_request.provider == "openai_compatible":
			if not test_request.base_url:
				return {
					"success": False,
					"error": "OpenAI 兼容接口需要提供 base_url",
				}
			client_params["base_url"] = test_request.base_url

		# 创建客户端并测试
		client = AsyncOpenAI(**client_params)

		start_time = time.time()
		response = await client.chat.completions.create(
			model=test_request.model,
			messages=[{"role": "user", "content": "Hi"}],
			max_tokens=10,
		)
		latency = (time.time() - start_time) * 1000

		await client.close()

		return {
			"success": True,
			"latency_ms": round(latency, 2),
		}

	except Exception as e:
		return {
			"success": False,
			"error": str(e),
		}
