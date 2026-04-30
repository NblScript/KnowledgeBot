"""Auth Service 配置"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Auth Service 配置"""
    
    # 应用配置
    app_name: str = "KnowledgeBot Auth Service"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    
    # 数据库配置
    database_url: str = "postgresql+asyncpg://knowledgebot:knowledgebot123@localhost:5432/knowledgebot"
    database_schema: str = "auth"
    
    # JWT 配置
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1小时
    refresh_token_expire_days: int = 7     # 7天
    
    # Redis 配置 (用于 Token 黑名单)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # 密码配置
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = False
    
    # 租户配置
    tenant_enabled: bool = True
    default_tenant_slug: str = "default"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """获取配置（缓存）"""
    return Settings()


settings = get_settings()