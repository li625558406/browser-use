# D:/AI/ai-scout/browser-use/backend/api/executions.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
	# 使用 join 来获取任务信息
	query = select(TaskExecution).options(selectinload(TaskExecution.task))

	if task_id is not None:
		query = query.where(TaskExecution.task_id == task_id)

	if status is not None:
		query = query.where(TaskExecution.status == status)

	query = query.order_by(TaskExecution.started_at.desc()).limit(limit)

	result = await session.execute(query)
	executions = result.scalars().all()

	# 手动构建响应，包含 task_name
	response_data = []
	for execution in executions:
		response_data.append(
			TaskExecutionResponse(
				id=execution.id,
				task_id=execution.task_id,
				task_name=execution.task.name if execution.task else "未知任务",
				status=execution.status,
				started_at=execution.started_at,
				completed_at=execution.completed_at,
				error_message=execution.error_message,
				screenshot_path=execution.screenshot_path,
			)
		)

	return ApiResponse.success(data=response_data)


@router.get("/{execution_id}", response_model=ApiResponse[TaskExecutionResponse])
async def get_execution(
	execution_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskExecutionResponse]:
	"""获取执行记录详情"""
	execution = await session.get(TaskExecution, execution_id)

	if not execution:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="执行记录不存在")

	# 加载关联的任务
	await session.refresh(execution, attribute_names=["task"])

	return ApiResponse.success(
		data=TaskExecutionResponse(
			id=execution.id,
			task_id=execution.task_id,
			task_name=execution.task.name if execution.task else "未知任务",
			status=execution.status,
			started_at=execution.started_at,
			completed_at=execution.completed_at,
			error_message=execution.error_message,
			screenshot_path=execution.screenshot_path,
		)
	)


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
