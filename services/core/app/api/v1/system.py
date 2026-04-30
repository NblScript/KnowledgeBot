"""系统路由"""

from fastapi import APIRouter

from app.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    services = {
        "database": "ok",
        "milvus": "ok",
        "redis": "ok",
        "minio": "ok",
    }
    
    # TODO: 实际检查各服务状态
    
    return HealthResponse(
        status="healthy",
        services=services,
    )


@router.get("/v1/system/info")
async def get_system_info():
    """获取系统信息"""
    return {
        "version": "0.1.0",
        "embedding_models": ["bge-m3", "text-embedding-3-small"],
        "llm_models": ["glm-4", "qwen2.5-turbo", "gpt-4o-mini"],
        "supported_file_types": settings.allowed_extensions_list,
    }
