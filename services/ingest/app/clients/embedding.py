"""Embedding Service HTTP 客户端"""

import httpx
from typing import Any, Optional

from app.config import settings


class EmbeddingClient:
    """Embedding Service HTTP 客户端"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or settings.embedding_service_url
        self.timeout = timeout or settings.http_timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client
    
    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def embed_texts(self, texts: list[str]) -> dict[str, Any]:
        """获取文本向量"""
        client = await self.get_client()
        response = await client.post(
            "/v1/embeddings",
            json={"texts": texts},
        )
        response.raise_for_status()
        return response.json()
    
    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = None,
    ) -> list[list[float]]:
        """批量获取文本向量"""
        batch_size = batch_size or settings.embedding_batch_size
        all_vectors = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = await self.embed_texts(batch)
            vectors = [item["vector"] for item in result["data"]]
            all_vectors.extend(vectors)
        
        return all_vectors
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            client = await self.get_client()
            response = await client.get("/")
            return response.status_code == 200
        except Exception:
            return False


# 全局实例
_embedding_client: Optional[EmbeddingClient] = None


async def get_embedding_client() -> EmbeddingClient:
    """获取 Embedding 客户端实例"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    return _embedding_client