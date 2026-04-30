"""Milvus 检索器"""

from typing import Any

from pymilvus import Collection, connections, utility

from app.config import settings


class MilvusRetriever:
    """Milvus 检索器"""
    
    def __init__(self, kb_id: str, embedding_dim: int = 1024):
        self.kb_id = kb_id
        self.collection_name = f"kb_{kb_id.replace('-', '_')}"
        self.embedding_dim = embedding_dim
        self._collection: Collection | None = None
        self._connected = False
    
    def connect(self):
        """连接 Milvus"""
        if not self._connected:
            connections.connect(
                "default",
                host=settings.milvus_host,
                port=settings.milvus_port,
            )
            self._connected = True
    
    def get_collection(self) -> Collection | None:
        """获取 Collection"""
        self.connect()
        
        if utility.has_collection(self.collection_name):
            self._collection = Collection(self.collection_name)
            self._collection.load()
            return self._collection
        
        return None
    
    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """向量检索"""
        collection = self.get_collection()
        if collection is None:
            return []
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16},
        }
        
        # 构建过滤表达式
        expr = None
        if filters:
            filter_parts = []
            if "doc_ids" in filters and filters["doc_ids"]:
                doc_ids_str = ", ".join(f'"{did}"' for did in filters["doc_ids"])
                filter_parts.append(f"doc_id in [{doc_ids_str}]")
            if filter_parts:
                expr = " and ".join(filter_parts)
        
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["chunk_id", "doc_id", "kb_id", "content", "metadata"],
        )
        
        return [
            {
                "chunk_id": hit.entity.get("chunk_id"),
                "doc_id": hit.entity.get("doc_id"),
                "kb_id": hit.entity.get("kb_id"),
                "content": hit.entity.get("content"),
                "score": hit.distance,
                "metadata": hit.entity.get("metadata"),
            }
            for hit in results[0]
            if hit.distance >= score_threshold
        ]
    
    def disconnect(self):
        """断开连接"""
        if self._connected:
            connections.disconnect("default")
            self._connected = False