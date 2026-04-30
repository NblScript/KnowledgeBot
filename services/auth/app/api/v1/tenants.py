"""租户管理 API"""

from typing import Optional
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
)
from app.services.tenant_service import TenantService
from app.api.v1.auth import get_current_user_id
from libs.common.responses import success_response, paginate_response
from app.config import settings


router = APIRouter(prefix="/tenants", tags=["租户管理"])


@router.post("", summary="创建租户")
async def create_tenant(
    request: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """创建租户"""
    tenant_service = TenantService(db)
    tenant = await tenant_service.create_tenant(
        slug=request.slug,
        name=request.name,
        description=request.description,
        tenant_settings=request.settings,
    )
    
    return success_response(
        data=TenantResponse.from_model(tenant).model_dump(),
        message="租户创建成功",
    )


@router.get("/{tenant_id}", summary="获取租户详情")
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取租户详情"""
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant(tenant_id=tenant_id)
    
    if not tenant:
        return success_response(data=None, message="租户不存在")
    
    return success_response(data=TenantResponse.from_model(tenant).model_dump())


@router.get("/slug/{slug}", summary="根据 slug 获取租户")
async def get_tenant_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """根据 slug 获取租户"""
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant(slug=slug)
    
    if not tenant:
        return success_response(data=None, message="租户不存在")
    
    return success_response(data=TenantResponse.from_model(tenant).model_dump())


@router.get("", summary="获取租户列表")
async def list_tenants(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取租户列表"""
    tenant_service = TenantService(db)
    tenants, total = await tenant_service.get_tenants(
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    
    data = [
        {
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat(),
        }
        for t in tenants
    ]
    
    return paginate_response(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{tenant_id}", summary="更新租户")
async def update_tenant(
    tenant_id: int,
    request: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """更新租户"""
    tenant_service = TenantService(db)
    
    update_data = request.model_dump(exclude_unset=True)
    tenant = await tenant_service.update_tenant(tenant_id, **update_data)
    
    return success_response(
        data=TenantResponse.from_model(tenant).model_dump(),
        message="租户更新成功",
    )


@router.delete("/{tenant_id}", summary="删除租户")
async def delete_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """删除租户"""
    tenant_service = TenantService(db)
    await tenant_service.delete_tenant(tenant_id)
    
    return success_response(message="租户删除成功")