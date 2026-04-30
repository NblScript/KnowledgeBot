"""配置基类"""

from functools import lru_cache

from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    """配置基类"""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class GlobalSettings(BaseSettings):
    """全局配置"""
    
    # 应用
    app_name: str = "KnowledgeBot"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"
    
    # 日志
    log_level: str = "INFO"
    log_format: str = "json"  # json or text


@lru_cache
def get_settings() -> GlobalSettings:
    """获取全局配置（缓存）"""
    return GlobalSettings()
