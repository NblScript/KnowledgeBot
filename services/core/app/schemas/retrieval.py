"""检索 Schema"""

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class RetrievalRequest(BaseModel):
    """检索请求"""
    
    kb_id: str = Field(..., description="知识库 ID")
    query: str = Field(..., min_length=1, description="查询文本")
    top_k: int = Field(default=10, ge=1, le=50, description="返回数量")
    score_threshold: float = Field(default=0.3, ge=0, le=1, description="相似度阈值")
    filters: dict[str, Any] | None = Field(None, description="过滤条件")


class RetrievalResult(BaseSchema):
    """检索结果"""
    
    chunk_id: str
    doc_id: str
    doc_name: str
    content: str
    score: float
    metadata: dict[str, Any] | None = None


class RetrievalResponse(BaseModel):
    """检索响应"""
    
    query: str
    results: list[RetrievalResult]
    total: int
