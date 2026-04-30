"""Pytest 配置"""

import asyncio
import pytest
from typing import Generator

import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock 配置"""
    from app.config import Settings
    
    settings = Settings(
        app_env="development",
        app_debug=True,
        app_port=8005,
        redis_host="localhost",
        redis_port=6379,
        knowledge_service_url="http://localhost:8002",
        embedding_service_url="http://localhost:8003",
        chunk_size=500,
        chunk_overlap=50,
    )
    return settings