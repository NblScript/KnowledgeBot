"""Ingest Service 配置管理"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 服务配置
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8005
    app_name: str = "ingest-service"
    
    # Redis 配置 (Celery broker & backend)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 1
    
    # MinIO 配置 (文件存储)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "knowledgebot"
    minio_secure: bool = False
    
    # 文档处理配置
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: str = "pdf,docx,md,txt,html"
    
    # Knowledge Service 配置
    knowledge_service_url: str = "http://knowledge:8002"
    
    # Embedding Service 配置
    embedding_service_url: str = "http://embedding:8003"
    embedding_batch_size: int = 100
    
    # Celery 配置
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    celery_task_queue: str = "processing"
    
    # HTTP 客户端配置
    http_timeout: int = 30
    
    # 日志级别
    log_level: str = "INFO"
    
    @property
    def redis_url(self) -> str:
        """Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """允许的文件扩展名列表"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    def get_celery_broker_url(self) -> str:
        """获取 Celery broker URL"""
        return self.celery_broker_url or self.redis_url
    
    def get_celery_backend_url(self) -> str:
        """获取 Celery result backend URL"""
        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()