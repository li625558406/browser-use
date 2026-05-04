# D:/AI/ai-scout/browser-use/backend/api/executions.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_session
from backend.models.execution import TaskExecution
from backend.schemas.execution import TaskExecutionResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[list[TaskExecutionResponse]])
async def list_executions(
    session: Annotated[AsyncSession, Depends(get_session)],
    task_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
) -> ApiResponse[list[TaskExecutionResponse]]:
	"""获取执行记录列表"""
	query = select(TaskExecution)

	if task_id is not None:
		query = query.where(TaskExecution.task_id == task_id)

	if status is not None:
		query = query.where(TaskExecution.status == status)

	query = query.order_by(TaskExecution.started_at.desc()).limit(limit)

	result = await session.execute(query)
	executions = result.scalars().all()

	return ApiResponse.success(data=[TaskExecutionResponse.model_validate(e) for e in executions])


@router.get("/{execution_id}", response_model=ApiResponse[TaskExecutionResponse])
async def get_execution(
	execution_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskExecutionResponse]:
	"""获取执行记录详情"""
	execution = await session.get(TaskExecution, execution_id)

	if not execution:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="执行记录不存在")

	return ApiResponse.success(data=TaskExecutionResponse.model_validate(execution))


@router.delete("/{execution_id}", response_model=ApiResponse[None])
async def delete_execution(
	execution_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[None]:
	"""删除执行记录"""
	execution = await session.get(TaskExecution, execution_id)

	if not execution:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="执行记录不存在")

	await session.delete(execution)
	await session.commit()

	return ApiResponse.success(message="执行记录已删除")
