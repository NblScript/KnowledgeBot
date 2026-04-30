"""Embedding Service HTTP 客户端"""

import httpx

from app.config import settings


class EmbeddingClient:
    """Embedding Service HTTP 客户端
    
    用于调用 Embedding Service 的 API 进行向量检索
    """
    
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.embedding_service_url
        self._client: httpx.AsyncClient | None = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=60.0,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
        return False
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("EmbeddingClient not initialized. Use async context manager.")
        return self._client
    
    async def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict | None = None,
    ) -> list[dict]:
        """向量检索
        
        调用 Embedding Service 的 /v1/search 接口
        
        Args:
            kb_id: 知识库 ID（作为 collection_id）
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filters: 过滤条件
            
        Returns:
            检索结果列表，每个结果包含:
            - chunk_id: 文档块 ID
            - doc_id: 文档 ID
            - content: 内容
            - score: 相似度分数
            - metadata: 元数据
        """
        response = await self.client.post(
            "/v1/search",
            json={
                "collection_id": kb_id,
                "query": query,
                "top_k": top_k,
                "score_threshold": score_threshold,
                "filters": filters,
            },
        )
        response.raise_for_status()
        data = response.json()
        
        # 添加 doc_name 字段（从 metadata 中提取或使用默认值）
        results = []
        for r in data.get("results", []):
            result = {
                "chunk_id": r["chunk_id"],
                "doc_id": r["doc_id"],
                "content": r["content"],
                "score": r["score"],
                "metadata": r.get("metadata", {}),
                "doc_name": r.get("metadata", {}).get("doc_name", "Unknown"),
            }
            results.append(result)
        
        return results
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量文本向量化
        
        调用 Embedding Service 的 /v1/texts 接口
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        response = await self.client.post(
            "/v1/texts",
            json={"texts": texts},
        )
        response.raise_for_status()
        data = response.json()
        
        # 返回按索引排序的向量列表
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [e["embedding"] for e in embeddings]
    
    async def create_collection(
        self,
        kb_id: str,
        embedding_dim: int = 1024,
    ) -> dict:
        """创建向量集合
        
        Args:
            kb_id: 知识库 ID
            embedding_dim: 向量维度
            
        Returns:
            创建结果
        """
        response = await self.client.post(
            "/v1/collections",
            json={
                "collection_id": kb_id,
                "embedding_dim": embedding_dim,
            },
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_collection(self, kb_id: str) -> dict:
        """删除向量集合
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            删除结果
        """
        response = await self.client.delete(f"/v1/collections/{kb_id}")
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> dict:
        """健康检查"""
        response = await self.client.get("/v1/health")
        response.raise_for_status()
        return response.json()


# 全局客户端实例（懒加载）
_embedding_client: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient:
    """获取 Embedding 客户端实例"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    return _embedding_client
