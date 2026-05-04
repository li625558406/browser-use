# D:/AI/ai-scout/browser-use/backend/api/tasks.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_session
from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.get("", response_model=ApiResponse[list[TaskResponse]])
async def list_tasks(
	session: Annotated[AsyncSession, Depends(get_session)],
	is_enabled: bool | None = None,
) -> ApiResponse[list[TaskResponse]]:
	"""获取任务列表"""
	query = select(Task)

	if is_enabled is not None:
		query = query.where(Task.is_enabled == is_enabled)

	query = query.order_by(Task.created_at.desc())

	result = await session.execute(query)
	tasks = result.scalars().all()

	return ApiResponse.success(data=[TaskResponse.model_validate(task) for task in tasks])


@router.post("", response_model=ApiResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
async def create_task(
	task_data: TaskCreate,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskResponse]:
	"""创建任务"""
	# 检查依赖任务是否存在
	if task_data.depends_on is not None:
		dep_task = await session.get(Task, task_data.depends_on)
		if not dep_task:
			return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="依赖任务不存在")

	# 创建新任务
	new_task = Task(
		name=task_data.name,
		description=task_data.description,
		target_url=task_data.target_url,
		prompt_id=task_data.prompt_id,
		llm_config_id=task_data.llm_config_id,
		schedule_type=task_data.schedule.type,
		schedule_config=task_data.schedule.model_dump(exclude_none=True),
		browser_mode=task_data.browser_mode,
		profile_name=task_data.profile_name,
		depends_on=task_data.depends_on,
	)

	session.add(new_task)
	await session.commit()
	await session.refresh(new_task)

	return ApiResponse.success(data=TaskResponse.model_validate(new_task), message="任务创建成功")


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(
	task_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskResponse]:
	"""获取任务详情"""
	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.put("/{task_id}", response_model=ApiResponse[TaskResponse])
async def update_task(
	task_id: int,
	task_data: TaskUpdate,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskResponse]:
	"""更新任务"""
	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	# 检查依赖任务是否存在
	if task_data.depends_on is not None:
		if task_data.depends_on == task_id:
			return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="任务不能依赖自己")

		dep_task = await session.get(Task, task_data.depends_on)
		if not dep_task:
			return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="依赖任务不存在")

	# 更新字段
	if task_data.name is not None:
		task.name = task_data.name
	if task_data.description is not None:
		task.description = task_data.description
	if task_data.target_url is not None:
		task.target_url = task_data.target_url
	if task_data.prompt_id is not None:
		task.prompt_id = task_data.prompt_id
	if task_data.llm_config_id is not None:
		task.llm_config_id = task_data.llm_config_id
	if task_data.schedule is not None:
		task.schedule_type = task_data.schedule.type
		task.schedule_config = task_data.schedule.model_dump(exclude_none=True)
	if task_data.browser_mode is not None:
		task.browser_mode = task_data.browser_mode
	if task_data.profile_name is not None:
		task.profile_name = task_data.profile_name
	if task_data.is_enabled is not None:
		task.is_enabled = task_data.is_enabled
	if task_data.depends_on is not None:
		task.depends_on = task_data.depends_on

	await session.commit()
	await session.refresh(task)

	return ApiResponse.success(data=TaskResponse.model_validate(task), message="任务更新成功")


@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(
	task_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[None]:
	"""删除任务"""
	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	# 检查是否有其他任务依赖此任务
	result = await session.execute(select(Task).where(Task.depends_on == task_id))
	dependent_tasks = result.scalars().all()

	if dependent_tasks:
		return ApiResponse.error(
			code=ErrorCode.INVALID_PARAMS,
			message=f"无法删除：有 {len(dependent_tasks)} 个任务依赖此任务",
		)

	await session.delete(task)
	await session.commit()

	return ApiResponse.success(message="任务删除成功")


@router.post("/{task_id}/toggle", response_model=ApiResponse[TaskResponse])
async def toggle_task(
	task_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[TaskResponse]:
	"""切换任务启用状态"""
	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	task.is_enabled = not task.is_enabled
	await session.commit()
	await session.refresh(task)

	status_text = "启用" if task.is_enabled else "禁用"
	return ApiResponse.success(data=TaskResponse.model_validate(task), message=f"任务已{status_text}")


@router.post("/{task_id}/run", response_model=ApiResponse[dict])
async def run_task(
	task_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[dict]:
	"""手动运行任务"""
	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	if not task.is_enabled:
		return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="任务已禁用，无法运行")

	# TODO: 实现任务执行逻辑
	# 这里需要调用 browser-use 的 Agent 来执行任务
	# 目前返回一个占位响应

	return ApiResponse.success(
		data={"task_id": task_id, "status": "queued"},
		message="任务已加入执行队列",
	)
