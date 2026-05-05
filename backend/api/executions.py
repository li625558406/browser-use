# D:/AI/ai-scout/browser-use/backend/api/executions.py

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_session
from backend.models.execution import TaskExecution
from backend.schemas.execution import TaskExecutionResponse
from backend.utils.logger import logger

router = APIRouter()

# 数据导出目录
EXPORT_DIR = "data/exports"


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

	# 手动构建响应，包含 task_name 和 log_content
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
				log_content=execution.log_content,
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
			log_content=execution.log_content,
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


@router.get("/{execution_id}/export", response_class=FileResponse)
async def export_execution_data(
	execution_id: int,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> FileResponse:
	"""导出执行记录数据为 Markdown 文件"""
	execution = await session.get(TaskExecution, execution_id)

	if not execution:
		raise HTTPException(status_code=404, detail="执行记录不存在")

	# 加载关联的任务
	await session.refresh(execution, attribute_names=["task"])

	task_name = execution.task.name if execution.task else f"task_{execution.task_id}"

	# 确保导出目录存在
	os.makedirs(EXPORT_DIR, exist_ok=True)

	# 生成文件名
	timestamp = execution.started_at.strftime("%Y%m%d_%H%M%S") if execution.started_at else "unknown"
	filename = f"{task_name}_{timestamp}_success.md" if execution.status == "success" else f"{task_name}_{timestamp}.md"
	filepath = os.path.join(EXPORT_DIR, filename)

	# 生成 Markdown 内容
	content = f"# {task_name} - 执行记录\n\n"
	content += f"**执行ID**: {execution.id}\n"
	content += f"**状态**: {execution.status}\n"
	content += f"**开始时间**: {execution.started_at}\n"
	if execution.completed_at:
		content += f"**完成时间**: {execution.completed_at}\n"

	# 计算耗时
	if execution.started_at and execution.completed_at:
		duration = (execution.completed_at - execution.started_at).total_seconds()
		content += f"**耗时**: {duration:.1f} 秒\n"

	content += "\n---\n\n"

	# 添加日志内容
	if execution.log_content:
		content += "## 执行结果\n\n"
		content += execution.log_content
	else:
		content += "*无执行日志*\n"

	# 添加错误信息
	if execution.error_message:
		content += "\n---\n\n"
		content += "## 错误信息\n\n"
		content += f"```\n{execution.error_message}\n```\n"

	# 写入文件
	with open(filepath, "w", encoding="utf-8") as f:
		f.write(content)

	logger.info(f"导出执行记录 {execution.id} 到 {filepath}")

	return FileResponse(
		path=filepath,
		filename=filename,
		media_type="text/markdown"
	)


@router.get("/exports/list", response_model=ApiResponse[list[dict]])
async def list_export_files() -> ApiResponse[list[dict]]:
	"""获取导出文件列表"""
	exports = []

	if os.path.exists(EXPORT_DIR):
		for filename in os.listdir(EXPORT_DIR):
			if filename.endswith(".md"):
				filepath = os.path.join(EXPORT_DIR, filename)
				stat = os.stat(filepath)

				# 解析文件名获取信息
				exports.append({
					"name": filename,
					"size": f"{stat.st_size / 1024:.1f} KB",
					"date": stat.st_mtime,
					"path": filepath
				})

	# 按修改时间倒序排列
	exports.sort(key=lambda x: x["date"], reverse=True)

	return ApiResponse.success(data=exports)


@router.get("/exports/{filename}", response_class=FileResponse)
async def download_export_file(filename: str) -> FileResponse:
	"""下载导出文件"""
	# 安全检查：确保文件名不包含路径遍历
	if "/" in filename or "\\" in filename:
		raise HTTPException(status_code=400, detail="无效的文件名")

	filepath = os.path.join(EXPORT_DIR, filename)

	if not os.path.exists(filepath):
		raise HTTPException(status_code=404, detail="文件不存在")

	return FileResponse(
		path=filepath,
		filename=filename,
		media_type="text/markdown"
	)
