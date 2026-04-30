"""任务相关 Schema"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型"""
    DOCUMENT_PROCESS = "document_process"
    DOCUMENT_EMBED = "document_embed"
    BATCH_PROCESS = "batch_process"


class TaskCreate(BaseModel):
    """创建任务请求"""
    task_type: TaskType
    doc_id: str
    kb_id: str
    file_name: str
    file_type: str
    file_path: str
    priority: int = Field(default=5, ge=1, le=10)
    metadata: Optional[dict[str, Any]] = None


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    doc_id: str
    kb_id: str
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: TaskStatus
    progress: int = Field(default=0, ge=0, le=100)
    message: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class DocumentProcessResult(BaseModel):
    """文档处理结果"""
    doc_id: str
    chunk_count: int
    total_tokens: int
    file_type: str
    processing_time: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchTaskCreate(BaseModel):
    """批量任务创建"""
    kb_id: str
    doc_ids: list[str]
    priority: int = Field(default=5, ge=1, le=10)


class BatchTaskStatus(BaseModel):
    """批量任务状态"""
    batch_id: str
    total: int
    completed: int
    failed: int
    pending: int
    tasks: list[TaskStatusResponse]