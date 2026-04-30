"""Pytest 配置"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    from app.database import Base
    
    # 创建测试引擎
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    from app.api.deps import get_session
    from app.main import app
    
    # 覆盖依赖
    async def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # 清理覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_conversation_data() -> dict[str, Any]:
    """示例对话数据"""
    return {
        "kb_id": "test-kb-id",
        "title": "Test Conversation",
    }


@pytest.fixture
def sample_chat_request() -> dict[str, Any]:
    """示例聊天请求"""
    return {
        "kb_id": "test-kb-id",
        "messages": [{"role": "user", "content": "What is RAG?"}],
        "top_k": 5,
        "score_threshold": 0.5,
        "temperature": 0.7,
        "max_tokens": 2000,
    }
