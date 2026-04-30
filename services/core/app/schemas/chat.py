"""对话和聊天 Schema"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class MessageCreate(BaseModel):
    """创建消息"""
    
    role: str = "user"
    content: str


class ChatCompletionRequest(BaseModel):
    """对话补全请求"""
    
    kb_id: str = Field(..., description="知识库 ID")
    conversation_id: str | None = Field(None, description="对话 ID，为空则创建新对话")
    messages: list[MessageCreate] = Field(..., min_length=1, description="消息列表")
    top_k: int = Field(default=5, ge=1, le=20, description="检索数量")
    score_threshold: float = Field(default=0.5, ge=0, le=1, description="相似度阈值")
    temperature: float = Field(default=0.7, ge=0, le=2, description="生成温度")
    max_tokens: int = Field(default=2000, ge=1, le=8000, description="最大生成 tokens")


class SourceReference(BaseModel):
    """来源引用"""
    
    chunk_id: str
    doc_id: str
    doc_name: str
    content: str
    score: float
    metadata: dict[str, Any] | None = None


class ChatChoice(BaseModel):
    """对话选择"""
    
    index: int = 0
    message: MessageCreate
    finish_reason: str = "stop"


class ChatUsage(BaseModel):
    """Token 使用统计"""
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """对话补全响应"""
    
    id: str
    conversation_id: str
    kb_id: str
    choices: list[ChatChoice]
    sources: list[SourceReference] = []
    usage: ChatUsage = ChatUsage()
    created_at: datetime


class ConversationCreate(BaseModel):
    """创建对话请求"""
    
    kb_id: str | None = None
    title: str | None = None


class MessageResponse(BaseSchema):
    """消息响应"""
    
    id: str
    role: str
    content: str
    token_count: int | None
    sources: list[dict[str, Any]] | None = None
    created_at: datetime


class ConversationResponse(BaseSchema):
    """对话响应"""
    
    id: str
    kb_id: str | None
    title: str | None
    message_count: int = 0
    messages: list[MessageResponse] = []
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseSchema):
    """对话列表响应"""
    
    id: str
    kb_id: str | None
    title: str | None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
