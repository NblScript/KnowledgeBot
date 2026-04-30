"""文档路由"""

import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.config import settings
from app.models import Chunk, Document, KnowledgeBase
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.document import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentResponse,
    ProcessDocumentResponse,
)

router = APIRouter()


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


@router.post(
    "/{kb_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    auto_process: bool = Query(False, description="自动触发处理"),
    session: AsyncSession = Depends(get_session),
):
    """上传文档到知识库"""
    # 检查知识库是否存在
    kb_result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found",
        )
    
    # 检查文件类型
    file_ext = get_file_extension(file.filename or "")
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_ext} not allowed. Allowed types: {settings.allowed_extensions}",
        )
    
    # 检查文件大小
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.max_file_size // 1024 // 1024}MB",
        )
    
    # 计算文件哈希
    file_hash = hashlib.sha256(content).hexdigest()
    
    # 检查重复文件
    existing_result = await session.execute(
        select(Document).where(
            Document.kb_id == kb_id,
            Document.file_hash == file_hash,
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already exists in this knowledge base",
        )
    
    # 创建文档记录
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        kb_id=kb_id,
        file_name=file.filename or "unknown",
        file_path=f"{kb_id}/{doc_id}/{file.filename}",
        file_size=len(content),
        file_type=file_ext,
        file_hash=file_hash,
        status="pending",
    )
    
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    
    # TODO: 存储 MinIO
    # TODO: 触发 Celery 处理任务
    
    return DocumentResponse.model_validate(doc)


@router.get("/{kb_id}/documents", response_model=PaginatedResponse[DocumentListResponse])
async def list_documents(
    kb_id: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: str | None = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session),
):
    """获取知识库的文档列表"""
    # 检查知识库是否存在
    kb_result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    if not kb_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found",
        )
    
    # 构建查询
    query = select(Document).where(Document.kb_id == kb_id)
    count_query = select(func.count(Document.id)).where(Document.kb_id == kb_id)
    
    if status_filter:
        query = query.where(Document.status == status_filter)
        count_query = count_query.where(Document.status == status_filter)
    
    # 排序和分页
    query = query.order_by(Document.created_at.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await session.execute(query)
    docs = result.scalars().all()
    
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    items = [
        DocumentListResponse(
            id=doc.id,
            file_name=doc.file_name,
            file_type=doc.file_type,
            file_size=doc.file_size,
            status=doc.status,
            chunk_count=doc.chunk_count,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
        for doc in docs
    ]
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(
    doc_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取文档详情"""
    result = await session.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
    
    # 获取分块列表
    chunks_result = await session.execute(
        select(Chunk)
        .where(Chunk.doc_id == doc_id)
        .order_by(Chunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()
    
    return DocumentDetailResponse(
        id=doc.id,
        kb_id=doc.kb_id,
        file_name=doc.file_name,
        file_path=doc.file_path,
        file_size=doc.file_size,
        file_type=doc.file_type,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunks=[
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "token_count": chunk.token_count,
            }
            for chunk in chunks
        ],
    )


@router.post("/{doc_id}/process", response_model=ProcessDocumentResponse)
async def process_document(
    doc_id: str,
    session: AsyncSession = Depends(get_session),
):
    """触发文档处理"""
    result = await session.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
    
    if doc.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already being processed",
        )
    
    # TODO: 触发 Celery 任务
    
    return ProcessDocumentResponse(
        task_id=str(uuid.uuid4()),
        status="processing",
        message="Document processing started",
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除文档"""
    result = await session.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
    
    # 删除 Milvus 中的向量
    from app.database import milvus_client
    milvus_client.delete_by_doc_id(doc.kb_id, doc_id)
    
    # 删除数据库记录（级联删除分块）
    await session.delete(doc)
    await session.commit()
    
    return None
