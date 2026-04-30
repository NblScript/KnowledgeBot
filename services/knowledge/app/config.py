"""Knowledge Service 配置管理模块 - 使用 Pydantic Settings"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Knowledge Service 应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 应用配置
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    app_secret_key: str = "your-secret-key-change-in-production"
    
    # 数据库配置 - PostgreSQL with schema
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "knowledgebot"
    postgres_password: str = "knowledgebot123"
    postgres_db: str = "knowledgebot"
    postgres_schema: str = "knowledgebot_knowledge"
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    
    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    
    # MinIO 配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "knowledgebot"
    minio_secure: bool = False
    
    # Embedding 配置 (调用 embedding service)
    embedding_provider: Literal["openai", "local", "siliconflow", "qwen", "mock"] = "mock"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    
    # 文档处理配置
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: str = "pdf,docx,md,txt,html"
    
    @property
    def database_url_async(self) -> str:
        """异步数据库连接 URL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库连接 URL (for Alembic)"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
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


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
