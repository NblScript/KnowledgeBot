"""租户相关 Schema"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import json


class TenantBase(BaseModel):
    """租户基础 Schema"""
    slug: str = Field(..., min_length=3, max_length=50, pattern="^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=100)


class TenantCreate(TenantBase):
    """创建租户请求"""
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[Dict[str, Any]] = None


class TenantUpdate(BaseModel):
    """更新租户请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class TenantResponse(BaseModel):
    """租户响应"""
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    is_active: bool
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_model(cls, model):
        """从模型转换"""
        settings_dict = None
        if model.settings:
            try:
                settings_dict = json.loads(model.settings)
            except:
                settings_dict = None
        return cls(
            id=model.id,
            slug=model.slug,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            settings=settings_dict,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class TenantListResponse(BaseModel):
    """租户列表响应"""
    id: int
    slug: str
    name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True