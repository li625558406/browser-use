# D:/AI/ai-scout/browser-use/backend/api/tasks.py

import asyncio

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_session, get_db
from backend.models.execution import TaskExecution
from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from backend.services.task_executor import TaskExecutor
from backend.utils.logger import logger

router = APIRouter()

# 存储正在运行的任务
_running_tasks: dict[int, asyncio.Task] = {}
# 存储活跃的 executor 实例（用于 resume）
_executors: dict[int, 'TaskExecutor'] = {}


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
		browser_mode="connect",  # 默认使用 CDP 模式
		profile_name=None,  # CDP 模式不使用 profile
		is_enabled=True,
		max_items=task_data.max_items,
		requires_login=task_data.requires_login if task_data.requires_login is not None else True,
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
	# browser_mode 和 profile_name 不再允许前端修改，始终使用 CDP 模式
	if task_data.max_items is not None:
		task.max_items = task_data.max_items
	if task_data.requires_login is not None:
		task.requires_login = task_data.requires_login
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

	# 检查任务是否已在运行
	if task_id in _running_tasks:
		return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="任务正在运行中")

	# 创建异步任务执行
	async def execute_task():
		executor = None
		try:
			# TaskExecutor 会创建自己的 session
			executor = TaskExecutor(task)
			# 存储 executor 以便 resume 使用
			_executors[task_id] = executor
			execution = await executor.execute()
			logger.info(f"任务 {task.name} 执行完成，状态: {execution.status}")

			# 只有在任务真正完成（不是等待登录）时才移除 executor
			if execution.status != "waiting_for_login":
				_executors.pop(task_id, None)
				_running_tasks.pop(task_id, None)
		except Exception as e:
			logger.error(f"任务 {task.name} 执行失败: {e}", exc_info=True)
			# 发生异常时也要清理
			_executors.pop(task_id, None)
			_running_tasks.pop(task_id, None)

	# 在后台执行任务
	background_task = asyncio.create_task(execute_task())
	_running_tasks[task_id] = background_task

	return ApiResponse.success(
		data={"task_id": task_id, "status": "running"},
		message="任务已开始执行",
	)


@router.post("/{task_id}/resume")
async def resume_task_execution(task_id: int, session: AsyncSession = Depends(get_db)):
	"""继续执行任务（用户登录后）"""
	logger.info(f"收到继续执行请求，task_id={task_id}")

	task = await session.get(Task, task_id)

	if not task:
		return ApiResponse.error(code=ErrorCode.NOT_FOUND, message="任务不存在")

	# 检查是否有活跃的 executor
	logger.info(f"检查 executor 字典，task_id in _executors={task_id in _executors}")
	if task_id not in _executors:
		return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="执行器未找到，请先运行任务")

	executor = _executors[task_id]
	logger.info(f"获取到 executor: {executor}")

	# 检查是否是等待登录状态
	execution_result = await session.execute(
		select(TaskExecution)
		.where(TaskExecution.task_id == task_id)
		.order_by(TaskExecution.id.desc())
		.limit(1)
	)
	current_execution = execution_result.scalar_one_or_none()

	logger.info(f"当前执行状态: {current_execution.status if current_execution else None}")

	if not current_execution or current_execution.status != "waiting_for_login":
		return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="当前不在等待登录状态")

	try:
		logger.info(f"调用 executor.resume_execution()...")
		await executor.resume_execution()
		logger.info(f"executor.resume_execution() 完成")
		return ApiResponse.success(message="任务继续执行")
	except Exception as e:
		logger.error(f"继续执行任务失败: {e}", exc_info=True)
		return ApiResponse.error(code=ErrorCode.INTERNAL_ERROR, message=f"继续执行失败: {str(e)}")


@router.post("/{task_id}/stop")
async def stop_task(task_id: int):
	"""停止正在运行的任务"""
	if task_id not in _executors:
		return ApiResponse.error(code=ErrorCode.INVALID_PARAMS, message="任务未在运行中")

	executor = _executors[task_id]
	await executor.stop()

	# 清理跟踪
	_running_tasks.pop(task_id, None)
	_executors.pop(task_id, None)

	return ApiResponse.success(message="任务已停止")


@router.post("/clear-domain-login")
async def clear_domain_login(domain: str):
	"""清除指定域名的登录状态"""
	from backend.services.domain_registry import remove_domain
	remove_domain(domain)
	return ApiResponse.success(message=f"已清除域名 '{domain}' 的登录状态")

