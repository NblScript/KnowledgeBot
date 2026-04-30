"""知识库 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_knowledge_base(client: AsyncClient):
    """测试创建知识库"""
    response = await client.post(
        "/v1/knowledge-bases/",
        json={
            "name": "Test KB",
            "description": "Test knowledge base",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test KB"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_knowledge_bases(client: AsyncClient):
    """测试获取知识库列表"""
    # 先创建一个知识库
    await client.post(
        "/v1/knowledge-bases/",
        json={"name": "Test KB 1"},
    )
    
    response = await client.get("/v1/knowledge-bases/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_get_knowledge_base(client: AsyncClient):
    """测试获取知识库详情"""
    # 创建知识库
    create_response = await client.post(
        "/v1/knowledge-bases/",
        json={"name": "Test KB Detail"},
    )
    kb_id = create_response.json()["id"]
    
    # 获取详情
    response = await client.get(f"/v1/knowledge-bases/{kb_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == kb_id
    assert data["name"] == "Test KB Detail"


@pytest.mark.asyncio
async def test_update_knowledge_base(client: AsyncClient):
    """测试更新知识库"""
    # 创建知识库
    create_response = await client.post(
        "/v1/knowledge-bases/",
        json={"name": "Test KB Update"},
    )
    kb_id = create_response.json()["id"]
    
    # 更新
    response = await client.put(
        f"/v1/knowledge-bases/{kb_id}",
        json={"name": "Updated KB"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated KB"


@pytest.mark.asyncio
async def test_delete_knowledge_base(client: AsyncClient):
    """测试删除知识库"""
    # 创建知识库
    create_response = await client.post(
        "/v1/knowledge-bases/",
        json={"name": "Test KB Delete"},
    )
    kb_id = create_response.json()["id"]
    
    # 删除
    response = await client.delete(f"/v1/knowledge-bases/{kb_id}")
    
    assert response.status_code == 204
    
    # 验证已删除
    get_response = await client.get(f"/v1/knowledge-bases/{kb_id}")
    assert get_response.status_code == 404