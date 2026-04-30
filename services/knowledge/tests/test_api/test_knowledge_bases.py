"""知识库 API 测试"""

import pytest
from httpx import AsyncClient

from app.models import KnowledgeBase
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_knowledge_base(client: AsyncClient):
    """测试创建知识库"""
    response = await client.post(
        "/v1/knowledge-bases/",
        json={
            "name": "Test KB",
            "description": "Test knowledge base",
            "embedding_model": "bge-m3",
            "llm_model": "glm-4",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test KB"
    assert data["description"] == "Test knowledge base"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_knowledge_bases(client: AsyncClient, db_session: AsyncSession):
    """测试获取知识库列表"""
    # 创建测试数据
    kb = KnowledgeBase(
        id="test-kb-id",
        name="Test KB",
        description="Test description",
        status="active",
    )
    db_session.add(kb)
    await db_session.commit()
    
    response = await client.get("/v1/knowledge-bases/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_get_knowledge_base(client: AsyncClient, db_session: AsyncSession):
    """测试获取知识库详情"""
    # 创建测试数据
    kb = KnowledgeBase(
        id="test-kb-detail-id",
        name="Test KB Detail",
        description="Test description",
        status="active",
    )
    db_session.add(kb)
    await db_session.commit()
    
    response = await client.get(f"/v1/knowledge-bases/{kb.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test KB Detail"


@pytest.mark.asyncio
async def test_update_knowledge_base(client: AsyncClient, db_session: AsyncSession):
    """测试更新知识库"""
    # 创建测试数据
    kb = KnowledgeBase(
        id="test-kb-update-id",
        name="Test KB Update",
        description="Original description",
        status="active",
    )
    db_session.add(kb)
    await db_session.commit()
    
    response = await client.put(
        f"/v1/knowledge-bases/{kb.id}",
        json={"description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_knowledge_base(client: AsyncClient, db_session: AsyncSession):
    """测试删除知识库"""
    # 创建测试数据
    kb = KnowledgeBase(
        id="test-kb-delete-id",
        name="Test KB Delete",
        description="Test description",
        status="active",
    )
    db_session.add(kb)
    await db_session.commit()
    
    response = await client.delete(f"/v1/knowledge-bases/{kb.id}")
    assert response.status_code == 204