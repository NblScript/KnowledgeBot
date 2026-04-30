"""Embedding Service 主入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_router
from app.config import settings
from app.services.milvus_client import get_milvus_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时连接 Milvus
    milvus_client = get_milvus_client()
    try:
        milvus_client.connect()
        print(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")
    except Exception as e:
        print(f"Warning: Failed to connect to Milvus: {e}")
    
    yield
    
    # 关闭时断开连接
    try:
        milvus_client.disconnect()
        print("Disconnected from Milvus")
    except Exception:
        pass


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Embedding Service",
        description="向量嵌入服务 - 支持 OpenAI/Qwen/SiliconFlow",
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
            "service": "embedding-service",
            "version": "1.0.0",
            "status": "running",
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