"""Ingest Service 主入口"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_router
from app.config import settings
from app.celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"Starting {settings.app_name} on port {settings.app_port}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"Task queue: {settings.celery_task_queue}")
    
    yield
    
    # 关闭时
    print(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Ingest Service",
        description="文档摄入服务 - 异步处理文档解析、分块、向量化",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册 API 路由
    app.include_router(api_router, prefix="/v1")
    
    # 根路径健康检查
    @app.get("/")
    async def root():
        return {
            "service": settings.app_name,
            "version": "1.0.0",
            "status": "running",
            "queue": settings.celery_task_queue,
        }
    
    # 健康检查
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "ingest",
            "port": settings.app_port,
        }
    
    # Celery 状态检查
    @app.get("/health/celery")
    async def celery_health():
        """检查 Celery 连接"""
        try:
            # 检查 Redis 连接
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                return {
                    "status": "healthy",
                    "workers": len(stats),
                    "details": stats,
                }
            else:
                return {
                    "status": "warning",
                    "message": "No Celery workers available",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )