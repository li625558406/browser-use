# D:/AI/ai-scout/browser-use/backend/api/__init__.py

from fastapi import APIRouter

from backend.api import browser, executions, llm, prompts, tasks

api_router = APIRouter()

# 导入子路由
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(llm.router, prefix="/llm-configs", tags=["llm"])
api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
