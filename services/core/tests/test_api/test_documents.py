"""文档 API 测试"""

import io
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient, sample_knowledge_base: str):
    """测试文档上传"""
    kb_id = sample_knowledge_base
    
    # 创建一个测试文件
    file_content = b"This is a test document content for knowledge base."
    file_like = io.BytesIO(file_content)
    
    response = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("test_document.txt", file_like, "text/plain")},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "test_document.txt"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_document_kb_not_found(client: AsyncClient):
    """测试上传到不存在的知识库"""
    fake_kb_id = "00000000-0000-0000-0000-000000000000"
    file_content = b"Test content"
    file_like = io.BytesIO(file_content)
    
    response = await client.post(
        f"/v1/knowledge-bases/{fake_kb_id}/documents",
        files={"file": ("test.txt", file_like, "text/plain")},
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_document_invalid_type(client: AsyncClient, sample_knowledge_base: str):
    """测试上传不支持的文件类型"""
    kb_id = sample_knowledge_base
    
    file_content = b"Test content"
    file_like = io.BytesIO(file_content)
    
    response = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("test.xyz", file_like, "application/octet-stream")},
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, sample_knowledge_base: str):
    """测试获取文档列表"""
    kb_id = sample_knowledge_base
    
    # 先上传一个文档
    file_content = b"Test document for list test."
    file_like = io.BytesIO(file_content)
    
    await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("list_test.txt", file_like, "text/plain")},
    )
    
    # 获取列表
    response = await client.get(f"/v1/knowledge-bases/{kb_id}/documents")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_list_documents_with_pagination(client: AsyncClient, sample_knowledge_base: str):
    """测试分页获取文档列表"""
    kb_id = sample_knowledge_base
    
    # 上传多个文档
    for i in range(3):
        file_content = f"Document {i} content".encode()
        file_like = io.BytesIO(file_content)
        await client.post(
            f"/v1/knowledge-bases/{kb_id}/documents",
            files={"file": (f"doc_{i}.txt", file_like, "text/plain")},
        )
    
    # 测试分页
    response = await client.get(
        f"/v1/knowledge-bases/{kb_id}/documents",
        params={"page": 1, "page_size": 2},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2


@pytest.mark.asyncio
async def test_list_documents_kb_not_found(client: AsyncClient):
    """测试获取不存在知识库的文档列表"""
    fake_kb_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/v1/knowledge-bases/{fake_kb_id}/documents")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_document_detail(client: AsyncClient, sample_knowledge_base: str):
    """测试获取文档详情"""
    kb_id = sample_knowledge_base
    
    # 先上传一个文档
    file_content = b"Test document for detail test."
    file_like = io.BytesIO(file_content)
    
    upload_response = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("detail_test.txt", file_like, "text/plain")},
    )
    assert upload_response.status_code == 201
    doc_id = upload_response.json()["id"]
    
    # 获取详情
    response = await client.get(f"/v1/documents/{doc_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["file_name"] == "detail_test.txt"
    assert "chunks" in data


@pytest.mark.asyncio
async def test_get_document_not_found(client: AsyncClient):
    """测试获取不存在的文档"""
    fake_doc_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/v1/documents/{fake_doc_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_trigger_document_process(client: AsyncClient, sample_knowledge_base: str):
    """测试触发文档处理"""
    kb_id = sample_knowledge_base
    
    # 先上传一个文档
    file_content = b"Test document for process test."
    file_like = io.BytesIO(file_content)
    
    upload_response = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("process_test.txt", file_like, "text/plain")},
    )
    assert upload_response.status_code == 201
    doc_id = upload_response.json()["id"]
    
    # 触发处理
    response = await client.post(f"/v1/documents/{doc_id}/process")
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_process_document_not_found(client: AsyncClient):
    """测试处理不存在的文档"""
    fake_doc_id = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post(f"/v1/documents/{fake_doc_id}/process")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, sample_knowledge_base: str):
    """测试删除文档"""
    kb_id = sample_knowledge_base
    
    # 先上传一个文档
    file_content = b"Test document for delete."
    file_like = io.BytesIO(file_content)
    
    upload_response = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("delete_test.txt", file_like, "text/plain")},
    )
    assert upload_response.status_code == 201
    doc_id = upload_response.json()["id"]
    
    # 删除文档 (milvus_client is mocked globally in conftest)
    response = await client.delete(f"/v1/documents/{doc_id}")
    
    assert response.status_code == 204
    
    # 验证已删除
    get_response = await client.get(f"/v1/documents/{doc_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_documents_by_status(client: AsyncClient, sample_knowledge_base: str):
    """测试按状态过滤文档"""
    kb_id = sample_knowledge_base
    
    # 上传文档
    file_content = b"Test document for filter."
    file_like = io.BytesIO(file_content)
    
    await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("filter_test.txt", file_like, "text/plain")},
    )
    
    # 按状态过滤
    response = await client.get(
        f"/v1/knowledge-bases/{kb_id}/documents",
        params={"status": "pending"},
    )
    
    assert response.status_code == 200
    data = response.json()
    # 所有返回的文档都应该是 pending 状态
    for doc in data["data"]:
        assert doc["status"] == "pending"


@pytest.mark.asyncio
async def test_duplicate_document_upload(client: AsyncClient, sample_knowledge_base: str):
    """测试上传重复文档"""
    kb_id = sample_knowledge_base
    
    # 上传第一个文档
    file_content = b"Test duplicate content"
    file_like = io.BytesIO(file_content)
    
    response1 = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("duplicate.txt", file_like, "text/plain")},
    )
    assert response1.status_code == 201
    
    # 尝试上传相同内容的文档
    file_like2 = io.BytesIO(file_content)
    response2 = await client.post(
        f"/v1/knowledge-bases/{kb_id}/documents",
        files={"file": ("duplicate.txt", file_like2, "text/plain")},
    )
    
    # 应该返回冲突错误
    assert response2.status_code == 409