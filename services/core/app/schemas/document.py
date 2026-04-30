"""文档 Schema"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class DocumentCreate(BaseModel):
    """创建文档请求（内部使用）"""
    
    file_name: str
    file_path: str | None = None
    file_size: int | None = None
    file_type: str | None = None
    file_hash: str | None = None


class DocumentUpdate(BaseModel):
    """更新文档请求"""
    
    status: str | None = None
    chunk_count: int | None = None
    error_message: str | None = None


class DocumentResponse(BaseSchema):
    """文档响应"""
    
    id: str
    kb_id: str
    file_name: str
    file_path: str | None
    file_size: int | None
    file_type: str | None
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseSchema):
    """文档列表响应"""
    
    id: str
    file_name: str
    file_type: str | None
    file_size: int | None
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """文档详情响应"""
    
    chunks: list["ChunkPreview"] = []


class ChunkPreview(BaseSchema):
    """分块预览"""
    
    id: str
    chunk_index: int
    content_preview: str
    token_count: int | None


class ProcessDocumentResponse(BaseModel):
    """文档处理响应"""
    
    task_id: str
    status: str
    message: str
