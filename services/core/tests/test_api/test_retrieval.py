"""向量检索 API 测试"""

from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def reset_milvus_mock():
    """每个测试前重置 Milvus mock"""
    from tests.conftest import mock_milvus
    # 保存原始返回值
    original_return = [
        {
            "chunk_id": "test-chunk-1",
            "doc_id": "test-doc-1",
            "kb_id": "test-kb-1",
            "content": "这是测试内容，用于验证检索功能。",
            "score": 0.85,
            "metadata": {"page": 1},
        },
    ]
    # 测试前重置
    mock_milvus.search.reset_mock(return_value=True, side_effect=True)
    mock_milvus.search.return_value = original_return
    
    yield
    
    # 测试后清理 - 确保 side_effect 被清除
    mock_milvus.search.reset_mock(return_value=True, side_effect=True)
    mock_milvus.search.return_value = original_return


@pytest.mark.asyncio
async def test_search(client: AsyncClient, sample_knowledge_base: str):
    """测试向量检索"""
    kb_id = sample_knowledge_base
    
    # milvus_client is mocked globally in conftest
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "这是测试查询",
            "top_k": 5,
            "score_threshold": 0.5,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
    assert data["query"] == "这是测试查询"


@pytest.mark.asyncio
async def test_search_kb_not_found(client: AsyncClient):
    """测试在不存在的知识库中检索"""
    fake_kb_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": fake_kb_id,
            "query": "测试查询",
        },
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_with_custom_params(client: AsyncClient, sample_knowledge_base: str):
    """测试自定义参数检索"""
    kb_id = sample_knowledge_base
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "自定义参数查询",
            "top_k": 20,
            "score_threshold": 0.7,
        },
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_filters(client: AsyncClient, sample_knowledge_base: str):
    """测试带过滤条件的检索"""
    kb_id = sample_knowledge_base
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "过滤条件查询",
            "top_k": 10,
            "score_threshold": 0.3,
            "filters": {
                "doc_ids": ["doc-1", "doc-2"],
            },
        },
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_empty_query(client: AsyncClient, sample_knowledge_base: str):
    """测试空查询"""
    kb_id = sample_knowledge_base
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "",
        },
    )
    
    # 空查询应该返回验证错误
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_results_structure(client: AsyncClient, sample_knowledge_base: str):
    """测试检索结果结构"""
    kb_id = sample_knowledge_base
    
    # 配置 mock 返回特定结构的结果
    from tests.conftest import mock_milvus
    
    # 更新 mock 的 search 返回值
    mock_milvus.search.return_value = [
        {
            "chunk_id": "chunk-001",
            "doc_id": "doc-001",
            "kb_id": kb_id,
            "content": "这是测试内容片段",
            "score": 0.92,
            "metadata": {"page": 1, "section": "intro"},
        },
        {
            "chunk_id": "chunk-002",
            "doc_id": "doc-001",
            "kb_id": kb_id,
            "content": "另一个测试内容",
            "score": 0.85,
            "metadata": {"page": 2},
        },
    ]
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "结构测试",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 验证结果结构
    results = data["results"]
    if len(results) > 0:
        result = results[0]
        assert "chunk_id" in result
        assert "doc_id" in result
        assert "doc_name" in result
        assert "content" in result
        assert "score" in result
        assert "metadata" in result
    
    # 重置 mock
    mock_milvus.search.return_value = [
        {
            "chunk_id": "test-chunk-1",
            "doc_id": "test-doc-1",
            "kb_id": "test-kb-1",
            "content": "这是测试内容，用于验证检索功能。",
            "score": 0.85,
            "metadata": {"page": 1},
        },
    ]


@pytest.mark.asyncio
async def test_search_top_k_limit(client: AsyncClient, sample_knowledge_base: str):
    """测试 top_k 参数限制"""
    kb_id = sample_knowledge_base
    
    # 测试超出限制的 top_k
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "测试",
            "top_k": 100,  # 最大 50
        },
    )
    
    # 应该返回验证错误
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_score_threshold_range(client: AsyncClient, sample_knowledge_base: str):
    """测试 score_threshold 参数范围"""
    kb_id = sample_knowledge_base
    
    # 测试超出范围的 score_threshold
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "测试",
            "score_threshold": 1.5,  # 最大 1.0
        },
    )
    
    # 应该返回验证错误
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient, sample_knowledge_base: str):
    """测试无结果的检索"""
    kb_id = sample_knowledge_base
    
    # 配置 mock 返回空结果
    from tests.conftest import mock_milvus
    mock_milvus.search.return_value = []
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "不会匹配任何内容的查询",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0
    
    # 重置 mock
    mock_milvus.search.return_value = [
        {
            "chunk_id": "test-chunk-1",
            "doc_id": "test-doc-1",
            "kb_id": "test-kb-1",
            "content": "这是测试内容。",
            "score": 0.85,
            "metadata": {"page": 1},
        },
    ]


@pytest.mark.asyncio
async def test_search_milvus_error(client: AsyncClient, sample_knowledge_base: str):
    """测试 Milvus 错误处理"""
    kb_id = sample_knowledge_base
    
    # 配置 mock 抛出异常
    from tests.conftest import mock_milvus
    mock_milvus.search.side_effect = Exception("Milvus connection error")
    
    response = await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "测试查询",
        },
    )
    
    # 应该返回错误响应 (500 或其他错误状态)
    assert response.status_code in [500, 400, 503]
    
    # 重置 mock - 关键！
    mock_milvus.search.side_effect = None


@pytest.mark.asyncio
async def test_search_milvus_search_params(client: AsyncClient, sample_knowledge_base: str):
    """测试 Milvus 检索参数"""
    kb_id = sample_knowledge_base
    
    from tests.conftest import mock_milvus
    
    await client.post(
        "/v1/retrieval/search",
        json={
            "kb_id": kb_id,
            "query": "参数测试",
            "top_k": 15,
            "score_threshold": 0.6,
        },
    )
    
    # 验证 Milvus search 被调用
    mock_milvus.search.assert_called()
    
    # 获取调用参数
    call_kwargs = mock_milvus.search.call_args[1]
    assert call_kwargs["kb_id"] == kb_id
    assert call_kwargs["top_k"] == 15
    assert call_kwargs["score_threshold"] == 0.6