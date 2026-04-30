"""Embedding 相关 Schema"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """基础 Schema"""
    
    model_config = ConfigDict(from_attributes=True)


class EmbeddingData(BaseModel):
    """单个嵌入数据"""
    
    index: int = Field(..., description="索引")
    embedding: list[float] = Field(..., description="向量")
    object: str = Field(default="embedding", description="对象类型")


class BatchEmbedRequest(BaseModel):
    """批量嵌入请求"""
    
    texts: list[str] = Field(..., min_length=1, max_length=100, description="文本列表")
    model: str | None = Field(default=None, description="模型名称，可选")


class BatchEmbedResponse(BaseModel):
    """批量嵌入响应"""
    
    object: str = Field(default="list", description="对象类型")
    data: list[EmbeddingData] = Field(..., description="嵌入数据列表")
    model: str = Field(..., description="使用的模型")
    usage: dict[str, int] = Field(..., description="Token 使用量")


class SearchRequest(BaseModel):
    """向量检索请求"""
    
    collection_id: str = Field(..., description="集合 ID (知识库 ID)")
    query: str = Field(..., min_length=1, description="查询文本")
    top_k: int = Field(default=10, ge=1, le=100, description="返回数量")
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="相似度阈值")
    filters: dict[str, Any] | None = Field(default=None, description="过滤条件")


class SearchResult(BaseSchema):
    """检索结果"""
    
    chunk_id: str = Field(..., description="块 ID")
    doc_id: str = Field(..., description="文档 ID")
    content: str = Field(..., description="内容")
    score: float = Field(..., description="相似度分数")
    metadata: dict[str, Any] | None = Field(default=None, description="元数据")


class SearchResponse(BaseModel):
    """检索响应"""
    
    query: str = Field(..., description="查询文本")
    results: list[SearchResult] = Field(default_factory=list, description="结果列表")
    total: int = Field(..., description="总数")


class CollectionCreateRequest(BaseModel):
    """创建集合请求"""
    
    collection_id: str = Field(..., description="集合 ID")
    embedding_dim: int = Field(default=1024, ge=128, le=4096, description="向量维度")


class CollectionInfo(BaseModel):
    """集合信息"""
    
    collection_id: str = Field(..., description="集合 ID")
    name: str = Field(..., description="集合名称")
    embedding_dim: int = Field(..., description="向量维度")
    exists: bool = Field(..., description="是否存在")


class DeleteResponse(BaseModel):
    """删除响应"""
    
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    
    status: str = "healthy"
    service: str = "embedding-service"
    milvus: str = "connected"
    version: str = "1.0.0"