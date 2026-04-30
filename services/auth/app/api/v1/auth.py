"""认证 API"""

from datetime import datetime
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    LogoutRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.config import settings
from libs.common.responses import success_response
from libs.common.exceptions import UnauthorizedError


router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post("/register", summary="用户注册")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户注册"""
    auth_service = AuthService(db)
    user = await auth_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        tenant_slug=request.tenant_slug,
        full_name=request.full_name,
    )
    
    return success_response(
        data={"user_id": user.id, "username": user.username, "email": user.email},
        message="注册成功",
    )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.login(
        username=request.username,
        password=request.password,
        tenant_slug=request.tenant_slug,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """刷新 Token"""
    auth_service = AuthService(db)
    access_token, refresh_token = await auth_service.refresh_tokens(request.refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", summary="用户登出")
async def logout(
    request: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """用户登出"""
    auth_service = AuthService(db)
    
    # 解码 token 获取 user_id
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    user_id = payload.get("user_id")
    
    await auth_service.logout(request.refresh_token, user_id)
    
    return success_response(message="登出成功")


@router.post("/change-password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    auth_service = AuthService(db)
    
    # 解码 token 获取 user_id
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    user_id = payload.get("user_id")
    
    user = await auth_service.change_password(
        user_id=user_id,
        old_password=request.old_password,
        new_password=request.new_password,
    )
    
    return success_response(message="密码修改成功，请重新登录")


@router.get("/me", response_model=UserResponse, summary="获取当前用户")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息"""
    auth_service = AuthService(db)
    
    token = credentials.credentials
    payload = await auth_service.verify_access_token(token)
    
    # 返回用户信息
    return success_response(data={
        "id": payload["user_id"],
        "tenant_slug": payload["tenant_slug"],
        "username": payload["username"],
        "email": payload["email"],
        "roles": payload["roles"],
        "permissions": payload["permissions"],
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    })


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> int:
    """获取当前用户 ID（依赖注入）"""
    auth_service = AuthService(db)
    token = credentials.credentials
    payload = await auth_service.verify_access_token(token)
    return payload["user_id"]


async def get_current_tenant_slug(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> str:
    """获取当前租户 slug（依赖注入）"""
    auth_service = AuthService(db)
    token = credentials.credentials
    payload = await auth_service.verify_access_token(token)
    return payload["tenant_slug"]