"""数据库连接管理 - PostgreSQL + Milvus"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# SQLAlchemy Base
class Base(DeclarativeBase):
    """SQLAlchemy 声明基类"""
    pass


# PostgreSQL 异步引擎
_engine_kwargs = {
    "echo": settings.app_debug,
    "pool_size": 5,
    "max_overflow": 10,
}

engine = create_async_engine(settings.database_url_async, **_engine_kwargs)

# 异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """数据库会话上下文管理器"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class MilvusClient:
    """Milvus 向量数据库客户端"""
    
    def __init__(self):
        self._connected = False
        self.alias = "default"
    
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
            connections.disconnect(self.alias)
            self._connected = False
    
    def create_collection(self, kb_id: str, embedding_dim: int = 1024) -> Collection:
        """为知识库创建 Collection
        
        Args:
            kb_id: 知识库 ID
            embedding_dim: 向量维度
            
        Returns:
            Collection 对象
        """
        self.connect()
        
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        
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
            description=f"Document chunks for knowledge base {kb_id}",
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
    
    def get_collection(self, kb_id: str) -> Collection | None:
        """获取知识库的 Collection"""
        self.connect()
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        
        if utility.has_collection(collection_name, using=self.alias):
            return Collection(collection_name, using=self.alias)
        return None
    
    def drop_collection(self, kb_id: str):
        """删除知识库的 Collection"""
        self.connect()
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        
        if utility.has_collection(collection_name, using=self.alias):
            utility.drop_collection(collection_name, using=self.alias)
    
    def insert_vectors(
        self,
        kb_id: str,
        data: list[dict[str, Any]],
    ) -> list[int]:
        """插入向量数据
        
        Args:
            kb_id: 知识库 ID
            data: 向量数据列表，每个元素包含 chunk_id, doc_id, kb_id, content, embedding, metadata
            
        Returns:
            插入的向量 ID 列表
        """
        collection = self.get_collection(kb_id)
        if collection is None:
            raise ValueError(f"Collection for knowledge base {kb_id} not found")
        
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
        kb_id: str,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """向量检索
        
        Args:
            kb_id: 知识库 ID
            query_vector: 查询向量
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filters: 过滤条件
            
        Returns:
            检索结果列表
        """
        collection = self.get_collection(kb_id)
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
    
    def delete(self, kb_id: str, expr: str):
        """删除向量数据"""
        collection = self.get_collection(kb_id)
        if collection is None:
            return
        
        collection.delete(expr)
        collection.flush()
    
    def delete_by_doc_id(self, kb_id: str, doc_id: str):
        """根据文档 ID 删除向量"""
        self.delete(kb_id, f'doc_id == "{doc_id}"')
    
    def delete_by_kb_id(self, kb_id: str):
        """删除知识库的所有向量"""
        self.delete(kb_id, f'kb_id == "{kb_id}"')


# 全局 Milvus 客户端
milvus_client = MilvusClient()


# MinIO 客户端
def get_minio_client():
    """获取 MinIO 客户端"""
    from minio import Minio
    
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_minio_bucket():
    """确保 MinIO bucket 存在"""
    client = get_minio_client()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)
