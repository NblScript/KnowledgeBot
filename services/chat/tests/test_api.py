"""对话 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查"""
    response = await client.get("/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chat-service"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "chat-service"


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient, sample_conversation_data: dict):
    """测试创建对话"""
    response = await client.post(
        "/v1/chat/conversations",
        json=sample_conversation_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_conversation_data["title"]
    assert data["kb_id"] == sample_conversation_data["kb_id"]


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient, sample_conversation_data: dict):
    """测试获取对话列表"""
    # 先创建一个对话
    await client.post("/v1/chat/conversations", json=sample_conversation_data)
    
    # 获取列表
    response = await client.get("/v1/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_get_conversation(client: AsyncClient, sample_conversation_data: dict):
    """测试获取对话详情"""
    # 先创建对话
    create_response = await client.post(
        "/v1/chat/conversations",
        json=sample_conversation_data,
    )
    conv_id = create_response.json()["id"]
    
    # 获取详情
    response = await client.get(f"/v1/chat/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert data["title"] == sample_conversation_data["title"]


@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient, sample_conversation_data: dict):
    """测试删除对话"""
    # 先创建对话
    create_response = await client.post(
        "/v1/chat/conversations",
        json=sample_conversation_data,
    )
    conv_id = create_response.json()["id"]
    
    # 删除对话
    response = await client.delete(f"/v1/chat/conversations/{conv_id}")
    assert response.status_code == 204
    
    # 验证已删除
    get_response = await client.get(f"/v1/chat/conversations/{conv_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_conversation(client: AsyncClient):
    """测试获取不存在的对话"""
    response = await client.get("/v1/chat/conversations/nonexistent-id")
    assert response.status_code == 404
