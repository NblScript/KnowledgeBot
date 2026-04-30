"""角色相关 Schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import json


class RoleBase(BaseModel):
    """角色基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """创建角色请求"""
    tenant_slug: str
    permissions: List[str] = Field(default=[], description="权限代码列表")
    is_default: bool = Field(default=False)


class RoleUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    tenant_slug: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_model(cls, model):
        """从模型转换"""
        permissions_list = []
        if model.permissions:
            try:
                permissions_list = json.loads(model.permissions)
            except:
                permissions_list = []
        return cls(
            id=model.id,
            tenant_slug=model.tenant_slug,
            name=model.name,
            description=model.description,
            permissions=permissions_list,
            is_default=model.is_default,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class RoleListResponse(BaseModel):
    """角色列表响应"""
    id: int
    tenant_slug: str
    name: str
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True