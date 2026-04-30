"""测试 Embedding 服务"""

import pytest

from app.services.embedding_service import EmbeddingService, MockEmbedding


@pytest.fixture
def embedding_service():
    """测试 Embedding 服务"""
    return EmbeddingService(provider="mock")


@pytest.mark.asyncio
async def test_embed_single(embedding_service):
    """测试单个文本向量化"""
    text = "Hello, world!"
    embedding = await embedding_service.embed_single(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == embedding_service.embedding_dim
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_embed_texts(embedding_service):
    """测试批量文本向量化"""
    texts = ["Hello", "World", "Test"]
    embeddings = await embedding_service.embed_texts(texts)
    
    assert len(embeddings) == 3
    for emb in embeddings:
        assert isinstance(emb, list)
        assert len(emb) == embedding_service.embedding_dim


def test_model_name(embedding_service):
    """测试模型名称"""
    assert embedding_service.model_name == "mock-embedding"


def test_embedding_dim(embedding_service):
    """测试向量维度"""
    assert embedding_service.embedding_dim > 0


def test_mock_embedding():
    """测试 Mock Embedding"""
    mock = MockEmbedding(embedding_dim=512)
    assert mock.embedding_dim == 512
    assert mock.model_name == "mock-embedding"
