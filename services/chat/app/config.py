"""Chat Service 配置管理"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
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
    app_port: int = 8004
    app_secret_key: str = "your-secret-key-change-in-production"
    
    # 数据库配置 - Chat Service 使用独立的 schema
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "knowledgebot"
    postgres_password: str = "knowledgebot123"
    postgres_db: str = "knowledgebot"
    postgres_schema: str = "chat"  # 独立 schema
    
    # Embedding Service 配置
    embedding_service_url: str = "http://embedding:8003"
    
    # LLM 配置
    llm_provider: Literal["openai", "siliconflow", "qwen", "zhipu", "mock"] = "mock"
    llm_model: str = "gpt-4o-mini"
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7
    
    # OpenAI API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 通义千问 API
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 智谱 API
    zhipu_api_key: str = ""
    
    # SiliconFlow API
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    
    # RAG 配置
    default_top_k: int = 5
    default_score_threshold: float = 0.5
    max_history_messages: int = 10
    
    @property
    def database_url_async(self) -> str:
        """异步数据库连接 URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库连接 URL (for Alembic)"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
