"""权限相关 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """权限基础 Schema"""
    code: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9_:]+$")
    name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=20)


class PermissionCreate(PermissionBase):
    """创建权限请求"""
    description: Optional[str] = Field(None, max_length=255)


class PermissionUpdate(BaseModel):
    """更新权限请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    resource: Optional[str] = Field(None, min_length=1, max_length=50)
    action: Optional[str] = Field(None, min_length=1, max_length=20)


class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """权限列表响应"""
    id: int
    code: str
    name: str
    resource: str
    action: str
    
    class Config:
        from_attributes = True