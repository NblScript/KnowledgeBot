"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from app.api.v1 import router as api_router
from app.config import settings
from app.database import init_db, engine, Base
from libs.common.exceptions import AppException
from libs.common.responses import error_response


# Redis 连接池
redis_pool = None


async def get_redis() -> redis.Redis:
    """获取 Redis 连接"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
    return redis.Redis(connection_pool=redis_pool)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时
    await init_db()
    
    # 初始化 Redis
    app.state.redis = await get_redis()
    
    yield
    
    # 关闭时
    if redis_pool:
        await redis_pool.disconnect()
    await engine.dispose()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.app_name,
        description="JWT 认证、用户管理、租户支持",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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
    
    # 全局异常处理
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=get_status_code(exc.code),
            content=error_response(exc.code, exc.message, exc.details)
        )
    
    # 健康检查
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "auth"}
    
    return app


def get_status_code(code: str) -> int:
    """根据错误代码获取 HTTP 状态码"""
    status_map = {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 422,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "CONFLICT": 409,
        "INTERNAL_ERROR": 500,
        "SERVICE_UNAVAILABLE": 503,
    }
    return status_map.get(code, 400)


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )