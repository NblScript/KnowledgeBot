"""认证相关 Schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名或邮箱")
    password: str = Field(..., min_length=1, description="密码")
    tenant_slug: Optional[str] = Field(None, description="租户标识")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    tenant_slug: Optional[str] = Field(None, description="租户标识，不填则使用默认租户")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """密码强度验证"""
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access Token 过期时间（秒）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """密码强度验证"""
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class LogoutRequest(BaseModel):
    """登出请求"""
    refresh_token: Optional[str] = Field(None, description="要撤销的刷新令牌")


class TokenPayload(BaseModel):
    """Token 载荷"""
    user_id: int
    tenant_slug: str
    username: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    exp: datetime
    iat: datetime
    type: str  # access or refresh