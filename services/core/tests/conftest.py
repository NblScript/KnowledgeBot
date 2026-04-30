"""测试配置"""

import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 在导入任何 app 模块之前设置测试环境变量
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["APP_DEBUG"] = "false"
os.environ["EMBEDDING_PROVIDER"] = "mock"
os.environ["EMBEDDING_DIM"] = "1024"
os.environ["LLM_PROVIDER"] = "mock"

# 在导入 Base 之前，先 mock 掉 JSONB
import sqlalchemy.dialects.postgresql
sqlalchemy.dialects.postgresql.JSONB = JSON

# Mock Milvus 连接
mock_milvus = MagicMock()
mock_milvus.connect = MagicMock()
mock_milvus.disconnect = MagicMock()
mock_milvus.search = MagicMock(return_value=[])
mock_milvus.insert_vectors = MagicMock(return_value=[1, 2, 3])
mock_milvus.delete_by_doc_id = MagicMock()
mock_milvus.delete_by_kb_id = MagicMock()
mock_milvus.get_collection = MagicMock(return_value=MagicMock())
mock_milvus.create_collection = MagicMock(return_value=MagicMock())
mock_milvus.drop_collection = MagicMock()

# Patch Milvus before importing app
patcher = patch("app.database.milvus_client", mock_milvus)
patcher.start()


from app.main import app
from app.database import get_db
from app.api.deps import get_session


# 测试数据库 URL (内存 SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# 测试引擎
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)


# 需要导入 Base 来创建表
from app.database import Base


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """数据库会话 fixture"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_session_maker() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP 客户端 fixture"""
    async def override_get_db():
        yield db_session
    
    async def override_get_session():
        yield db_session
    
    # 覆盖依赖
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_embedding_service():
    """Mock Embedding 服务"""
    mock = MagicMock()
    # 返回固定维度的模拟向量 (1024 维)
    mock.embed = AsyncMock(return_value=[[0.1] * 1024 for _ in range(3)])
    mock.embed_single = AsyncMock(return_value=[0.1] * 1024)
    return mock


@pytest.fixture
def mock_llm_service():
    """Mock LLM 服务"""
    mock = MagicMock()
    mock.generate = AsyncMock(return_value="这是一个模拟的回答。基于您提供的上下文，我找到了相关信息。")
    mock.generate_stream = AsyncMock()
    # 模拟流式输出
    async def mock_stream(*args, **kwargs):
        for chunk in ["这是", "一个", "模拟的", "回答。"]:
            yield chunk
    mock.generate_stream = mock_stream
    return mock


@pytest.fixture
def mock_milvus_client():
    """Mock Milvus 客户端"""
    mock = MagicMock()
    mock.connect = MagicMock()
    mock.disconnect = MagicMock()
    mock.search = MagicMock(return_value=[
        {
            "chunk_id": "test-chunk-1",
            "doc_id": "test-doc-1",
            "kb_id": "test-kb-1",
            "content": "这是测试内容，用于验证检索功能。",
            "score": 0.85,
            "metadata": {"page": 1},
        },
        {
            "chunk_id": "test-chunk-2",
            "doc_id": "test-doc-1",
            "kb_id": "test-kb-1",
            "content": "另一段测试内容。",
            "score": 0.75,
            "metadata": {"page": 2},
        },
    ])
    mock.insert_vectors = MagicMock(return_value=[1, 2, 3])
    mock.delete_by_doc_id = MagicMock()
    mock.delete_by_kb_id = MagicMock()
    mock.get_collection = MagicMock(return_value=MagicMock())
    mock.create_collection = MagicMock(return_value=MagicMock())
    mock.drop_collection = MagicMock()
    return mock


@pytest.fixture
async def sample_knowledge_base(client: AsyncClient) -> str:
    """创建示例知识库并返回 ID"""
    response = await client.post(
        "/v1/knowledge-bases/",
        json={
            "name": "Test KB",
            "description": "Test knowledge base for documents",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]
