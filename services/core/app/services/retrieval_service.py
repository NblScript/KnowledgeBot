"""检索服务"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import milvus_client
from app.models import Document
from app.services.embedding_service import get_embedder


class RetrievalService:
    """检索服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """向量检索"""
        # 获取查询向量
        embedder = get_embedder()
        query_vector = await embedder.embed_single(query)
        
        # 执行向量检索
        results = milvus_client.search(
            kb_id=kb_id,
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=score_threshold,
            filters=filters,
        )
        
        # 获取文档名称
        doc_ids = list(set(r["doc_id"] for r in results))
        doc_names = {}
        if doc_ids:
            docs_result = await self.session.execute(
                select(Document.id, Document.file_name).where(
                    Document.id.in_(doc_ids)
                )
            )
            for doc_id, doc_name in docs_result:
                doc_names[doc_id] = doc_name
        
        # 添加文档名称
        for result in results:
            result["doc_name"] = doc_names.get(result["doc_id"], "Unknown")
        
        return results
    
    async def search_by_doc(
        self,
        kb_id: str,
        doc_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
    ) -> list[dict[str, Any]]:
        """在指定文档中检索"""
        return await self.search(
            kb_id=kb_id,
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            filters={"doc_ids": [doc_id]},
        )
