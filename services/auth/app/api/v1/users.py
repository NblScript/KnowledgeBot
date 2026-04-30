"""用户管理 API"""

from typing import Optional
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.services.user_service import UserService
from app.api.v1.auth import get_current_user_id, get_current_tenant_slug
from libs.common.responses import success_response, paginate_response
from libs.common.exceptions import ForbiddenError


router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", summary="创建用户")
async def create_user(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """创建用户（需要管理员权限）"""
    user_service = UserService(db)
    
    # 如果请求中没有指定租户，使用当前用户的租户
    if not request.tenant_slug:
        request.tenant_slug = tenant_slug
    
    user = await user_service.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        tenant_slug=request.tenant_slug,
        full_name=request.full_name,
        role_ids=request.role_ids,
        is_active=request.is_active,
        is_superuser=request.is_superuser,
    )
    
    return success_response(
        data={"id": user.id, "username": user.username, "email": user.email},
        message="用户创建成功",
    )


@router.get("/{user_id}", summary="获取用户详情")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """获取用户详情"""
    user_service = UserService(db)
    user = await user_service.get_user(user_id, tenant_slug)
    
    if not user:
        return success_response(data=None, message="用户不存在")
    
    # 获取角色
    roles = await user_service.auth_service.get_user_roles(user)
    permissions = await user_service.auth_service.get_user_permissions(user)
    
    return success_response(data={
        "id": user.id,
        "tenant_slug": user.tenant_slug,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "roles": [r.name for r in roles],
        "permissions": permissions,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    })


@router.get("", summary="获取用户列表")
async def list_users(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """获取用户列表"""
    user_service = UserService(db)
    users, total = await user_service.get_users(
        tenant_slug=tenant_slug,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    
    data = [
        {
            "id": u.id,
            "tenant_slug": u.tenant_slug,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]
    
    return paginate_response(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """更新用户"""
    user_service = UserService(db)
    
    update_data = request.model_dump(exclude_unset=True)
    user = await user_service.update_user(user_id, tenant_slug, **update_data)
    
    return success_response(
        data={"id": user.id, "username": user.username},
        message="用户更新成功",
    )


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """删除用户"""
    # 不允许删除自己
    if user_id == current_user_id:
        return success_response(success=False, message="不能删除自己")
    
    user_service = UserService(db)
    await user_service.delete_user(user_id, tenant_slug)
    
    return success_response(message="用户删除成功")


@router.post("/{user_id}/reset-password", summary="重置用户密码")
async def reset_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """重置用户密码（管理员操作）"""
    user_service = UserService(db)
    await user_service.reset_password(user_id, new_password, tenant_slug)
    
    return success_response(message="密码重置成功")


@router.post("/{user_id}/roles", summary="分配角色")
async def assign_roles(
    user_id: int,
    role_ids: list[int],
    db: AsyncSession = Depends(get_db),
    tenant_slug: str = Depends(get_current_tenant_slug),
):
    """分配角色"""
    user_service = UserService(db)
    user = await user_service.assign_roles(user_id, role_ids, tenant_slug)
    
    return success_response(message="角色分配成功")