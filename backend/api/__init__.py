# D:/AI/ai-scout/browser-use/backend/api/__init__.py

from fastapi import APIRouter

from backend.api import llm

api_router = APIRouter()

# 导入子路由（稍后添加）
# from backend.api import tasks, prompts, data, executions, browser
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(llm.router, prefix="/llm-configs", tags=["llm"])
# api_router.include_router(data.router, prefix="/data", tags=["data"])
# api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
# api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
