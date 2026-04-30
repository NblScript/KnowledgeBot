"""Milvus 向量数据库客户端"""

from typing import Any

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.config import settings
from app.services.embedding_service import get_embedding_service


class MilvusClient:
    """Milvus 向量数据库客户端"""
    
    def __init__(self):
        self._connected = False
        self.alias = "default"
        self._embedding_service = get_embedding_service()
    
    def connect(self):
        """连接 Milvus"""
        if not self._connected:
            connections.connect(
                alias=self.alias,
                host=settings.milvus_host,
                port=settings.milvus_port,
            )
            self._connected = True
    
    def disconnect(self):
        """断开连接"""
        if self._connected:
            try:
                connections.disconnect(self.alias)
            except Exception:
                pass
            self._connected = False
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    def collection_name_from_id(self, collection_id: str) -> str:
        """将集合 ID 转换为 Milvus 集合名称"""
        return f"kb_{collection_id.replace('-', '_')}"
    
    def create_collection(self, collection_id: str, embedding_dim: int | None = None) -> Collection:
        """创建集合
        
        Args:
            collection_id: 集合 ID
            embedding_dim: 向量维度，默认使用配置中的维度
            
        Returns:
            Collection 对象
        """
        self.connect()
        
        if embedding_dim is None:
            embedding_dim = self._embedding_service.embedding_dim
        
        collection_name = self.collection_name_from_id(collection_id)
        
        # 如果已存在，直接返回
        if utility.has_collection(collection_name, using=self.alias):
            return Collection(collection_name, using=self.alias)
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="kb_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        
        # 创建 Schema
        schema = CollectionSchema(
            fields=fields,
            description=f"Document chunks for collection {collection_id}",
            enable_dynamic_field=True,
        )
        
        # 创建 Collection
        collection = Collection(
            name=collection_name,
            schema=schema,
            using=self.alias,
        )
        
        # 创建向量索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        
        # 创建标量索引
        collection.create_index(field_name="doc_id")
        collection.create_index(field_name="kb_id")
        
        return collection
    
    def get_collection(self, collection_id: str) -> Collection | None:
        """获取集合"""
        self.connect()
        collection_name = self.collection_name_from_id(collection_id)
        
        if utility.has_collection(collection_name, using=self.alias):
            return Collection(collection_name, using=self.alias)
        return None
    
    def drop_collection(self, collection_id: str) -> bool:
        """删除集合"""
        self.connect()
        collection_name = self.collection_name_from_id(collection_id)
        
        if utility.has_collection(collection_name, using=self.alias):
            utility.drop_collection(collection_name, using=self.alias)
            return True
        return False
    
    def has_collection(self, collection_id: str) -> bool:
        """检查集合是否存在"""
        self.connect()
        collection_name = self.collection_name_from_id(collection_id)
        return utility.has_collection(collection_name, using=self.alias)
    
    def insert_vectors(
        self,
        collection_id: str,
        data: list[dict[str, Any]],
    ) -> list[int]:
        """插入向量数据
        
        Args:
            collection_id: 集合 ID
            data: 向量数据列表，每个元素包含 chunk_id, doc_id, kb_id, content, embedding, metadata
            
        Returns:
            插入的向量 ID 列表
        """
        collection = self.get_collection(collection_id)
        if collection is None:
            raise ValueError(f"Collection {collection_id} not found")
        
        # 准备插入数据
        insert_data = [
            [item["chunk_id"] for item in data],
            [item["doc_id"] for item in data],
            [item["kb_id"] for item in data],
            [item["content"] for item in data],
            [item["embedding"] for item in data],
            [item.get("metadata", {}) for item in data],
        ]
        
        # 插入数据
        result = collection.insert(insert_data)
        collection.flush()
        
        return result.primary_keys
    
    def search(
        self,
        collection_id: str,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """向量检索
        
        Args:
            collection_id: 集合 ID
            query_vector: 查询向量
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filters: 过滤条件
            
        Returns:
            检索结果列表
        """
        collection = self.get_collection(collection_id)
        if collection is None:
            return []
        
        # 加载 Collection 到内存
        collection.load()
        
        # 构建搜索参数
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16},
        }
        
        # 构建过滤表达式
        expr = None
        if filters:
            filter_parts = []
            if "doc_ids" in filters:
                doc_ids = filters["doc_ids"]
                if doc_ids:
                    doc_ids_str = ", ".join(f'"{did}"' for did in doc_ids)
                    filter_parts.append(f"doc_id in [{doc_ids_str}]")
            if filter_parts:
                expr = " and ".join(filter_parts)
        
        # 执行搜索
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["chunk_id", "doc_id", "kb_id", "content", "metadata"],
        )
        
        # 处理结果
        search_results = []
        for hit in results[0]:
            if hit.distance >= score_threshold:
                search_results.append({
                    "chunk_id": hit.entity.get("chunk_id"),
                    "doc_id": hit.entity.get("doc_id"),
                    "kb_id": hit.entity.get("kb_id"),
                    "content": hit.entity.get("content"),
                    "score": hit.distance,
                    "metadata": hit.entity.get("metadata"),
                })
        
        return search_results
    
    def delete_by_doc_id(self, collection_id: str, doc_id: str):
        """根据文档 ID 删除向量"""
        collection = self.get_collection(collection_id)
        if collection is None:
            return
        
        collection.delete(f'doc_id == "{doc_id}"')
        collection.flush()
    
    def delete_by_collection_id(self, collection_id: str):
        """删除集合的所有向量"""
        collection = self.get_collection(collection_id)
        if collection is None:
            return
        
        # 删除整个 collection
        kb_id = collection_id
        collection.delete(f'kb_id == "{kb_id}"')
        collection.flush()
    
    def get_collection_stats(self, collection_id: str) -> dict[str, Any]:
        """获取集合统计信息"""
        collection = self.get_collection(collection_id)
        if collection is None:
            return {"exists": False}
        
        collection.load()
        stats = collection.stats
        
        return {
            "exists": True,
            "name": collection.name,
            "count": stats.get("row_count", 0),
        }


# 全局 Milvus 客户端
_milvus_client: MilvusClient | None = None


def get_milvus_client() -> MilvusClient:
    """获取 Milvus 客户端实例"""
    global _milvus_client
    if _milvus_client is None:
        _milvus_client = MilvusClient()
    return _milvus_client