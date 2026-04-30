"""配置管理模块 - 使用 Pydantic Settings"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
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
    app_port: int = 8000
    app_secret_key: str = "your-secret-key-change-in-production"
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/knowledgebot.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "knowledgebot"
    postgres_password: str = "knowledgebot123"
    postgres_db: str = "knowledgebot"
    
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
    
    # Embedding 配置
    embedding_provider: Literal["openai", "local", "siliconflow", "qwen", "mock"] = "mock"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    embedding_device: str = "cpu"  # for local: cpu, cuda, mps
    
    # SiliconFlow API
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    
    # OpenAI API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 通义千问 API
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # LLM 配置
    llm_provider: Literal["openai", "siliconflow", "qwen", "mock"] = "mock"
    llm_model: str = "gpt-4o-mini"
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7
    
    # 智谱 API (保留兼容)
    zhipu_api_key: str = ""
    
    # Celery 配置
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    
    # 文档处理配置
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: str = "pdf,docx,md,txt,html"
    
    # 检索配置
    default_top_k: int = 5
    default_score_threshold: float = 0.5
    
    @property
    def database_url_async(self) -> str:
        """异步数据库连接 URL"""
        if self.database_url.startswith("sqlite"):
            return self.database_url
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库连接 URL (for Alembic)"""
        if self.database_url.startswith("sqlite"):
            return self.database_url.replace("+aiosqlite", "")
        return f"postgresql://{self.postgres_user}:***@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def set_celery_broker(cls, v: str, info) -> str:
        if v:
            return v
        host = info.data.get("redis_host", "localhost")
        port = info.data.get("redis_port", 6379)
        return f"redis://{host}:{port}/0"
    
    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def set_celery_backend(cls, v: str, info) -> str:
        if v:
            return v
        host = info.data.get("redis_host", "localhost")
        port = info.data.get("redis_port", 6379)
        return f"redis://{host}:{port}/0"
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """允许的文件扩展名列表"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
