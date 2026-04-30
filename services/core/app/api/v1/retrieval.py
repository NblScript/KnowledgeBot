"""检索路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models import Document, KnowledgeBase
from app.schemas.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResult
from app.database import milvus_client

router = APIRouter()


@router.post("/search", response_model=RetrievalResponse)
async def search(
    request: RetrievalRequest,
    session: AsyncSession = Depends(get_session),
):
    """向量检索"""
    # 检查知识库
    kb_result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == request.kb_id)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {request.kb_id} not found",
        )
    
    # TODO: 调用 Embedding 服务获取查询向量
    # 模拟查询向量（实际需要调用 Embedding 服务）
    import random
    query_vector = [random.random() for _ in range(1024)]
    
    # 执行向量检索
    results = milvus_client.search(
        kb_id=request.kb_id,
        query_vector=query_vector,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filters=request.filters,
    )
    
    # 获取文档名称
    doc_ids = list(set(r["doc_id"] for r in results))
    doc_names = {}
    if doc_ids:
        docs_result = await session.execute(
            select(Document.id, Document.file_name).where(Document.id.in_(doc_ids))
        )
        for doc_id, doc_name in docs_result:
            doc_names[doc_id] = doc_name
    
    # 构建响应
    retrieval_results = [
        RetrievalResult(
            chunk_id=r["chunk_id"],
            doc_id=r["doc_id"],
            doc_name=doc_names.get(r["doc_id"], "Unknown"),
            content=r["content"],
            score=r["score"],
            metadata=r.get("metadata"),
        )
        for r in results
    ]
    
    return RetrievalResponse(
        query=request.query,
        results=retrieval_results,
        total=len(retrieval_results),
    )
