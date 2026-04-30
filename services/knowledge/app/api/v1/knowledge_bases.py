"""知识库路由"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models import Chunk, Document, KnowledgeBase
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from app.database import milvus_client

router = APIRouter()


@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_base(
    data: KnowledgeBaseCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建知识库"""
    kb_id = str(uuid.uuid4())
    
    kb = KnowledgeBase(
        id=kb_id,
        name=data.name,
        description=data.description,
        embedding_model=data.embedding_model,
        llm_model=data.llm_model,
        status="active",
    )
    
    session.add(kb)
    await session.commit()
    await session.refresh(kb)
    
    # 创建 Milvus Collection
    milvus_client.create_collection(kb_id, embedding_dim=1024)
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        llm_model=kb.llm_model,
        embedding_dim=kb.embedding_dim,
        status=kb.status,
        document_count=0,
        chunk_count=0,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.get("/", response_model=PaginatedResponse[KnowledgeBaseListResponse])
async def list_knowledge_bases(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: str | None = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session),
):
    """获取知识库列表"""
    # 构建查询
    query = select(KnowledgeBase)
    count_query = select(func.count(KnowledgeBase.id))
    
    if status_filter:
        query = query.where(KnowledgeBase.status == status_filter)
        count_query = count_query.where(KnowledgeBase.status == status_filter)
    
    # 排序和分页
    query = query.order_by(KnowledgeBase.created_at.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await session.execute(query)
    kbs = result.scalars().all()
    
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # 构建响应
    items = []
    for kb in kbs:
        # 统计文档和分块数量
        doc_count_result = await session.execute(
            select(func.count(Document.id)).where(Document.kb_id == kb.id)
        )
        doc_count = doc_count_result.scalar() or 0
        
        chunk_count_result = await session.execute(
            select(func.count(Chunk.id)).where(Chunk.kb_id == kb.id)
        )
        chunk_count = chunk_count_result.scalar() or 0
        
        items.append(KnowledgeBaseListResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            status=kb.status,
            document_count=doc_count,
            chunk_count=chunk_count,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
        ))
    
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


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取知识库详情"""
    result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found",
        )
    
    # 统计文档和分块数量
    doc_count_result = await session.execute(
        select(func.count(Document.id)).where(Document.kb_id == kb.id)
    )
    doc_count = doc_count_result.scalar() or 0
    
    chunk_count_result = await session.execute(
        select(func.count(Chunk.id)).where(Chunk.kb_id == kb.id)
    )
    chunk_count = chunk_count_result.scalar() or 0
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        llm_model=kb.llm_model,
        embedding_dim=kb.embedding_dim,
        status=kb.status,
        document_count=doc_count,
        chunk_count=chunk_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    data: KnowledgeBaseUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新知识库"""
    result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kb, key, value)
    
    await session.commit()
    await session.refresh(kb)
    
    # 统计文档和分块数量
    doc_count_result = await session.execute(
        select(func.count(Document.id)).where(Document.kb_id == kb.id)
    )
    doc_count = doc_count_result.scalar() or 0
    
    chunk_count_result = await session.execute(
        select(func.count(Chunk.id)).where(Chunk.kb_id == kb.id)
    )
    chunk_count = chunk_count_result.scalar() or 0
    
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        llm_model=kb.llm_model,
        embedding_dim=kb.embedding_dim,
        status=kb.status,
        document_count=doc_count,
        chunk_count=chunk_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除知识库"""
    result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found",
        )
    
    # 删除 Milvus Collection
    milvus_client.drop_collection(kb_id)
    
    # 删除数据库记录（级联删除文档、分块）
    await session.delete(kb)
    await session.commit()
    
    return None