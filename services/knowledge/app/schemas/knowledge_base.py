"""知识库 Schema"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import BaseSchema


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    
    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: str | None = Field(None, description="知识库描述")
    embedding_model: str = Field(default="bge-m3", description="Embedding 模型")
    llm_model: str = Field(default="glm-4", description="LLM 模型")


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    
    name: str | None = Field(None, min_length=1, max_length=255, description="知识库名称")
    description: str | None = Field(None, description="知识库描述")
    status: str | None = Field(None, description="状态")


class KnowledgeBaseResponse(BaseSchema):
    """知识库响应"""
    
    id: str
    name: str
    description: str | None
    embedding_model: str
    llm_model: str
    embedding_dim: int
    status: str
    document_count: int = 0
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseListResponse(BaseSchema):
    """知识库列表响应"""
    
    id: str
    name: str
    description: str | None
    status: str
    document_count: int = 0
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime