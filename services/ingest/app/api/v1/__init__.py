"""API v1 路由"""

from fastapi import APIRouter

from app.api.v1.tasks import router as tasks_router

router = APIRouter()

# 注册子路由
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])