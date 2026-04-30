"""测试 Embedding API"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


def test_health_check(client):
    """测试健康检查"""
    response = client.get("/v1/embeddings/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "embedding-service"


def test_root(client):
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "embedding-service"


def test_embed_texts(client):
    """测试批量向量化"""
    response = client.post(
        "/v1/embeddings/texts",
        json={"texts": ["Hello, world!", "Test embedding"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert "embedding" in data["data"][0]
    assert data["model"] is not None


@patch("app.api.v1.embeddings.get_milvus_client")
def test_create_collection(mock_milvus, client):
    """测试创建集合"""
    # Mock Milvus 客户端
    mock_collection = MagicMock()
    mock_collection.name = "kb_test_collection"
    mock_milvus.return_value.create_collection.return_value = mock_collection
    
    response = client.post(
        "/v1/embeddings/collections",
        json={"collection_id": "test-collection", "embedding_dim": 1536},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["collection_id"] == "test-collection"


@patch("app.api.v1.embeddings.get_milvus_client")
def test_get_collection_not_found(mock_milvus, client):
    """测试获取不存在的集合"""
    import uuid
    random_id = str(uuid.uuid4())
    
    # Mock Milvus 客户端返回不存在
    mock_milvus.return_value.has_collection.return_value = False
    
    response = client.get(f"/v1/embeddings/collections/{random_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False


@patch("app.api.v1.embeddings.get_milvus_client")
def test_delete_collection_not_found(mock_milvus, client):
    """测试删除不存在的集合"""
    import uuid
    random_id = str(uuid.uuid4())
    
    # Mock Milvus 客户端返回不存在
    mock_milvus.return_value.has_collection.return_value = False
    
    response = client.delete(f"/v1/embeddings/collections/{random_id}")
    assert response.status_code == 404