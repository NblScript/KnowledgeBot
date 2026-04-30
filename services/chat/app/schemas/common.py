"""通用 Schema"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """基础 Schema"""
    
    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    """分页元数据"""
    
    page: int = Field(description="当前页码", ge=1)
    page_size: int = Field(description="每页数量", ge=1, le=100)
    total: int = Field(description="总数量", ge=0)
    total_pages: int = Field(description="总页数", ge=0)


class PaginatedResponse(BaseSchema, Generic[T]):
    """分页响应"""
    
    data: list[T] = Field(default_factory=list, description="数据列表")
    pagination: PaginationMeta = Field(description="分页信息")


class ErrorResponse(BaseModel):
    """错误响应"""
    
    error: str = Field(description="错误类型")
    message: str = Field(description="错误信息")
    detail: Any | None = Field(default=None, description="详细错误")
