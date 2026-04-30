"""Knowledge Service HTTP 客户端"""

import httpx
from typing import Any, Optional

from app.config import settings


class KnowledgeClient:
    """Knowledge Service HTTP 客户端"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or settings.knowledge_service_url
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
    
    async def get_document(self, doc_id: str) -> dict[str, Any]:
        """获取文档信息"""
        client = await self.get_client()
        response = await client.get(f"/v1/documents/{doc_id}")
        response.raise_for_status()
        return response.json()
    
    async def update_document_status(
        self,
        doc_id: str,
        status: str,
        chunk_count: int = None,
        error_message: str = None,
        metadata: dict = None,
    ) -> dict[str, Any]:
        """更新文档状态"""
        client = await self.get_client()
        data = {"status": status}
        
        if chunk_count is not None:
            data["chunk_count"] = chunk_count
        if error_message is not None:
            data["error_message"] = error_message
        if metadata is not None:
            data["metadata"] = metadata
        
        response = await client.patch(f"/v1/documents/{doc_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    async def create_chunks(
        self,
        doc_id: str,
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """创建文档分块"""
        client = await self.get_client()
        response = await client.post(
            f"/v1/documents/{doc_id}/chunks",
            json={"chunks": chunks},
        )
        response.raise_for_status()
        return response.json()
    
    async def get_knowledge_base(self, kb_id: str) -> dict[str, Any]:
        """获取知识库信息"""
        client = await self.get_client()
        response = await client.get(f"/v1/knowledge-bases/{kb_id}")
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            client = await self.get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False


# 全局实例
_knowledge_client: Optional[KnowledgeClient] = None


async def get_knowledge_client() -> KnowledgeClient:
    """获取 Knowledge 客户端实例"""
    global _knowledge_client
    if _knowledge_client is None:
        _knowledge_client = KnowledgeClient()
    return _knowledge_client