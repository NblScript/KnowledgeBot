"""检索服务 - 通过 Embedding Service 进行向量检索"""

from typing import Any

from app.clients.embedding import EmbeddingClient


class RetrievalService:
    """检索服务
    
    通过 HTTP 调用 Embedding Service 进行向量检索
    """
    
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
    
    async def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """向量检索
        
        Args:
            kb_id: 知识库 ID
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filters: 过滤条件
            
        Returns:
            检索结果列表
        """
        return await self.embedding_client.search(
            kb_id=kb_id,
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            filters=filters,
        )
    
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
