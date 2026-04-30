"""系统路由"""

from fastapi import APIRouter

from app.config import settings
from app.schemas.common import ErrorResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "chat-service",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
    }
