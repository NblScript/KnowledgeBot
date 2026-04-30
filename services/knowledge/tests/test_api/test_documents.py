"""文档 API 测试"""

import pytest
from httpx import AsyncClient

from app.models import KnowledgeBase, Document
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, db_session: AsyncSession):
    """测试获取文档列表"""
    # 创建知识库
    kb = KnowledgeBase(
        id="test-kb-docs-id",
        name="Test KB",
        status="active",
    )
    db_session.add(kb)
    
    # 创建文档
    doc = Document(
        id="test-doc-id",
        kb_id="test-kb-docs-id",
        file_name="test.pdf",
        file_type="pdf",
        file_size=1024,
        status="completed",
    )
    db_session.add(doc)
    await db_session.commit()
    
    response = await client.get(f"/v1/knowledge-bases/{kb.id}/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_get_document(client: AsyncClient, db_session: AsyncSession):
    """测试获取文档详情"""
    # 创建知识库
    kb = KnowledgeBase(
        id="test-kb-doc-detail-id",
        name="Test KB",
        status="active",
    )
    db_session.add(kb)
    
    # 创建文档
    doc = Document(
        id="test-doc-detail-id",
        kb_id="test-kb-doc-detail-id",
        file_name="test.pdf",
        file_type="pdf",
        file_size=1024,
        status="completed",
    )
    db_session.add(doc)
    await db_session.commit()
    
    response = await client.get(f"/v1/documents/{doc.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.pdf"


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, db_session: AsyncSession):
    """测试删除文档"""
    # 创建知识库
    kb = KnowledgeBase(
        id="test-kb-doc-delete-id",
        name="Test KB",
        status="active",
    )
    db_session.add(kb)
    
    # 创建文档
    doc = Document(
        id="test-doc-delete-id",
        kb_id="test-kb-doc-delete-id",
        file_name="test.pdf",
        file_type="pdf",
        file_size=1024,
        status="completed",
    )
    db_session.add(doc)
    await db_session.commit()
    
    response = await client.delete(f"/v1/documents/{doc.id}")
    assert response.status_code == 204