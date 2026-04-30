"""用户相关 Schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=8, max_length=128)
    tenant_slug: Optional[str] = Field(None, description="租户标识")
    role_ids: List[int] = Field(default=[], description="角色ID列表")
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    tenant_slug: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    roles: List[str] = []
    permissions: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    id: int
    tenant_slug: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserFilter(BaseModel):
    """用户过滤条件"""
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    tenant_slug: Optional[str] = None