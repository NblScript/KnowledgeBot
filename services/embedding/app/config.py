"""Embedding Service 配置管理"""

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
    
    # 服务配置
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8003
    app_name: str = "embedding-service"
    
    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    
    # Embedding 配置
    embedding_provider: Literal["openai", "siliconflow", "qwen", "mock"] = "mock"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    embedding_batch_size: int = 100
    
    # SiliconFlow API
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    
    # OpenAI API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 通义千问 API
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 日志级别
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()