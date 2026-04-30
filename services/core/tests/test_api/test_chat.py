"""RAG 对话 API 测试"""

import uuid
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_completion_new_conversation(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试新对话 RAG 问答"""
    kb_id = sample_knowledge_base
    
    # Mock embedding 和 LLM 服务
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "这是一个测试问题"}
                ],
                "top_k": 5,
                "score_threshold": 0.5,
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "conversation_id" in data
        assert "choices" in data
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert "content" in data["choices"][0]["message"]
        assert "sources" in data
        assert "usage" in data


@pytest.mark.asyncio
async def test_chat_completion_kb_not_found(client: AsyncClient):
    """测试使用不存在的知识库"""
    fake_kb_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post(
        "/v1/chat/completions",
        json={
            "kb_id": fake_kb_id,
            "messages": [
                {"role": "user", "content": "Test question"}
            ],
        },
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_completion_existing_conversation(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试继续对话"""
    kb_id = sample_knowledge_base
    
    # 先创建一个对话
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        first_response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "第一个问题"}
                ],
            },
        )
        
        assert first_response.status_code == 200
        conversation_id = first_response.json()["conversation_id"]
        
        # 继续对话
        second_response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "conversation_id": conversation_id,
                "messages": [
                    {"role": "user", "content": "第二个问题"}
                ],
            },
        )
        
        assert second_response.status_code == 200
        data = second_response.json()
        assert data["conversation_id"] == conversation_id


@pytest.mark.asyncio
async def test_chat_completion_invalid_conversation(client: AsyncClient, sample_knowledge_base: str):
    """测试使用不存在的对话 ID"""
    kb_id = sample_knowledge_base
    fake_conv_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post(
        "/v1/chat/completions",
        json={
            "kb_id": kb_id,
            "conversation_id": fake_conv_id,
            "messages": [
                {"role": "user", "content": "Test question"}
            ],
        },
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_completion_with_custom_params(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试自定义参数的对话"""
    kb_id = sample_knowledge_base
    
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "测试问题"}
                ],
                "top_k": 10,
                "score_threshold": 0.7,
                "temperature": 0.5,
                "max_tokens": 500,
            },
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_chat_completion_empty_messages(client: AsyncClient, sample_knowledge_base: str):
    """测试空消息列表"""
    kb_id = sample_knowledge_base
    
    response = await client.post(
        "/v1/chat/completions",
        json={
            "kb_id": kb_id,
            "messages": [],
        },
    )
    
    # 应该返回验证错误
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient, sample_knowledge_base: str):
    """测试获取对话列表"""
    kb_id = sample_knowledge_base
    
    response = await client.get("/v1/chat/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data


@pytest.mark.asyncio
async def test_list_conversations_by_kb(client: AsyncClient, sample_knowledge_base: str):
    """测试按知识库过滤对话列表"""
    kb_id = sample_knowledge_base
    
    response = await client.get(
        "/v1/chat/conversations",
        params={"kb_id": kb_id},
    )
    
    assert response.status_code == 200
    data = response.json()
    # 如果有数据，都应该属于该知识库
    for conv in data["data"]:
        assert conv["kb_id"] == kb_id


@pytest.mark.asyncio
async def test_list_conversations_pagination(client: AsyncClient):
    """测试对话列表分页"""
    response = await client.get(
        "/v1/chat/conversations",
        params={"page": 1, "page_size": 10},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 10


@pytest.mark.asyncio
async def test_get_conversation_detail(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试获取对话详情"""
    kb_id = sample_knowledge_base
    
    # 先创建一个对话
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        create_response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "创建对话测试"}
                ],
            },
        )
        
        assert create_response.status_code == 200
        conv_id = create_response.json()["conversation_id"]
    
    # 获取对话详情
    response = await client.get(f"/v1/chat/conversations/{conv_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert "messages" in data
    assert len(data["messages"]) >= 2  # 至少有用户消息和助手消息


@pytest.mark.asyncio
async def test_get_conversation_not_found(client: AsyncClient):
    """测试获取不存在的对话"""
    fake_conv_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/v1/chat/conversations/{fake_conv_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试删除对话"""
    kb_id = sample_knowledge_base
    
    # 先创建一个对话
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        create_response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "删除对话测试"}
                ],
            },
        )
        
        assert create_response.status_code == 200
        conv_id = create_response.json()["conversation_id"]
    
    # 删除对话
    response = await client.delete(f"/v1/chat/conversations/{conv_id}")
    
    assert response.status_code == 204
    
    # 验证已删除
    get_response = await client.get(f"/v1/chat/conversations/{conv_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation_not_found(client: AsyncClient):
    """测试删除不存在的对话"""
    fake_conv_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.delete(f"/v1/chat/conversations/{fake_conv_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_sources_included(
    client: AsyncClient,
    sample_knowledge_base: str,
    mock_embedding_service,
    mock_llm_service,
    mock_milvus_client,
):
    """测试对话响应包含来源引用"""
    kb_id = sample_knowledge_base
    
    # 设置 mock 返回特定数据
    mock_milvus_client.search.return_value = [
        {
            "chunk_id": "chunk-123",
            "doc_id": "doc-456",
            "kb_id": kb_id,
            "content": "相关内容片段",
            "score": 0.9,
            "metadata": {"page": 1, "doc_name": "Test Document"},
        },
    ]
    
    with patch("app.services.retrieval_service.get_embedder", return_value=mock_embedding_service), \
         patch("app.llm.llm_service.get_llm", return_value=mock_llm_service), \
         patch("app.services.retrieval_service.milvus_client", mock_milvus_client):
        
        response = await client.post(
            "/v1/chat/completions",
            json={
                "kb_id": kb_id,
                "messages": [
                    {"role": "user", "content": "查找相关内容"}
                ],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查来源引用
        sources = data["sources"]
        assert len(sources) > 0
        assert sources[0]["chunk_id"] == "chunk-123"
        assert sources[0]["score"] >= 0.5