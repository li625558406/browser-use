# D:/AI/ai-scout/browser-use/backend/api/prompts.py

from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.database import get_session
from backend.models.prompt import Prompt
from backend.schemas.prompt import PromptCreate, PromptResponse, PromptUpdate

router = APIRouter()


@router.get("", response_model=ApiResponse[list[PromptResponse]])
async def list_prompts(
	category: str | None = Query(None, description="按类别筛选"),
	skip: int = Query(0, ge=0, description="跳过的记录数"),
	limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
	session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[PromptResponse]]:
	"""获取 Prompt 列表"""
	query = select(Prompt)

	if category:
		query = query.where(Prompt.category == category)

	query = query.order_by(Prompt.created_at.desc()).offset(skip).limit(limit)

	result = await session.execute(query)
	prompts = result.scalars().all()

	return ApiResponse.success(data=[PromptResponse.model_validate(p) for p in prompts])


@router.post("", response_model=ApiResponse[PromptResponse])
async def create_prompt(
	prompt_data: PromptCreate,
	session: AsyncSession = Depends(get_session),
) -> ApiResponse[PromptResponse]:
	"""创建新的 Prompt"""
	# 检查同名 Prompt 是否已存在
	existing = await session.execute(
		select(Prompt).where(Prompt.name == prompt_data.name)
	)
	if existing.scalar_one_or_none():
		raise HTTPException(
			status_code=400,
			detail=f"Prompt with name '{prompt_data.name}' already exists",
		)

	# 创建新 Prompt
	prompt = Prompt(**prompt_data.model_dump())

	session.add(prompt)
	await session.commit()
	await session.refresh(prompt)

	return ApiResponse.success(data=PromptResponse.model_validate(prompt), message="Prompt created successfully")


@router.get("/{prompt_id}", response_model=ApiResponse[PromptResponse])
async def get_prompt(
	prompt_id: int,
	session: AsyncSession = Depends(get_session),
) -> ApiResponse[PromptResponse]:
	"""获取单个 Prompt 详情"""
	result = await session.execute(select(Prompt).where(Prompt.id == prompt_id))
	prompt = result.scalar_one_or_none()

	if not prompt:
		raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

	return ApiResponse.success(data=PromptResponse.model_validate(prompt))


@router.put("/{prompt_id}", response_model=ApiResponse[PromptResponse])
async def update_prompt(
	prompt_id: int,
	prompt_data: PromptUpdate,
	session: AsyncSession = Depends(get_session),
) -> ApiResponse[PromptResponse]:
	"""更新 Prompt"""
	result = await session.execute(select(Prompt).where(Prompt.id == prompt_id))
	prompt = result.scalar_one_or_none()

	if not prompt:
		raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

	# 检查名称冲突（如果名称被修改）
	if prompt_data.name and prompt_data.name != prompt.name:
		existing = await session.execute(
			select(Prompt).where(Prompt.name == prompt_data.name)
		)
		if existing.scalar_one_or_none():
			raise HTTPException(
				status_code=400,
				detail=f"Prompt with name '{prompt_data.name}' already exists",
			)

	# 更新字段
	update_data = prompt_data.model_dump(exclude_unset=True)
	for field, value in update_data.items():
		setattr(prompt, field, value)

	# 递增版本号
	prompt.version += 1

	await session.commit()
	await session.refresh(prompt)

	return ApiResponse.success(data=PromptResponse.model_validate(prompt), message="Prompt updated successfully")


@router.delete("/{prompt_id}", response_model=ApiResponse[None])
async def delete_prompt(
	prompt_id: int,
	session: AsyncSession = Depends(get_session),
) -> ApiResponse[None]:
	"""删除 Prompt"""
	result = await session.execute(select(Prompt).where(Prompt.id == prompt_id))
	prompt = result.scalar_one_or_none()

	if not prompt:
		raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

	await session.delete(prompt)
	await session.commit()

	return ApiResponse.success(message="Prompt deleted successfully")
