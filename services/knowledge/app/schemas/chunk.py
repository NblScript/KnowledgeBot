"""分块 Schema"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ChunkCreate(BaseModel):
    """创建分块请求"""
    
    content: str
    content_hash: str | None = None
    chunk_index: int
    token_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkResponse(BaseSchema):
    """分块响应"""
    
    id: str
    doc_id: str
    kb_id: str
    content: str
    chunk_index: int
    token_count: int | None
    metadata: dict[str, Any]
    created_at: datetime


class ChunkListResponse(BaseSchema):
    """分块列表响应"""
    
    id: str
    chunk_index: int
    content_preview: str = Field(description="内容预览（前200字符）")
    token_count: int | None
    created_at: datetime