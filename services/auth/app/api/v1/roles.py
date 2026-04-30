"""角色管理 API"""

from typing import Optional
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
)
from app.services.role_service import RoleService
from app.api.v1.auth import get_current_user_id, get_current_tenant_slug
from libs.common.responses import success_response, paginate_response


router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("", summary="创建角色")
async def create_role(
    request: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """创建角色"""
    role_service = RoleService(db)
    
    # 如果没有指定租户，使用当前用户的租户
    if not request.tenant_slug:
        request.tenant_slug = tenant_slug
    
    role = await role_service.create_role(
        tenant_slug=request.tenant_slug,
        name=request.name,
        description=request.description,
        permissions=request.permissions,
        is_default=request.is_default,
    )
    
    return success_response(
        data=RoleResponse.from_model(role).model_dump(),
        message="角色创建成功",
    )


@router.get("/{role_id}", summary="获取角色详情")
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """获取角色详情"""
    role_service = RoleService(db)
    role = await role_service.get_role(role_id, tenant_slug)
    
    if not role:
        return success_response(data=None, message="角色不存在")
    
    return success_response(data=RoleResponse.from_model(role).model_dump())


@router.get("", summary="获取角色列表")
async def list_roles(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """获取角色列表"""
    role_service = RoleService(db)
    roles, total = await role_service.get_roles(
        tenant_slug=tenant_slug,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    
    data = [
        {
            "id": r.id,
            "tenant_slug": r.tenant_slug,
            "name": r.name,
            "description": r.description,
            "is_default": r.is_default,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
        }
        for r in roles
    ]
    
    return paginate_response(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    request: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """更新角色"""
    role_service = RoleService(db)
    
    update_data = request.model_dump(exclude_unset=True)
    role = await role_service.update_role(role_id, tenant_slug, **update_data)
    
    return success_response(
        data=RoleResponse.from_model(role).model_dump(),
        message="角色更新成功",
    )


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """删除角色"""
    role_service = RoleService(db)
    await role_service.delete_role(role_id, tenant_slug)
    
    return success_response(message="角色删除成功")