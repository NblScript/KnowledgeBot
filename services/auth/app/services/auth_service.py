"""JWT 认证服务"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from app.database import UserModel, RoleModel, RefreshTokenModel, TenantModel
from libs.common.exceptions import UnauthorizedError, ValidationError, NotFoundError


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self,
        user_id: int,
        tenant_slug: str,
        username: str,
        email: str,
        roles: List[str],
        permissions: List[str],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """创建 Access Token"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        
        now = datetime.utcnow()
        expire = now + expires_delta
        
        payload = {
            "user_id": user_id,
            "tenant_slug": tenant_slug,
            "username": username,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "exp": expire,
            "iat": now,
            "type": "access",
        }
        
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def create_refresh_token(
        self,
        user_id: int,
        tenant_slug: str,
        username: str,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """创建 Refresh Token"""
        if expires_delta is None:
            expires_delta = timedelta(days=settings.refresh_token_expire_days)
        
        now = datetime.utcnow()
        expire = now + expires_delta
        
        payload = {
            "user_id": user_id,
            "tenant_slug": tenant_slug,
            "username": username,
            "email": email,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }
        
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def decode_token(self, token: str) -> dict:
        """解码 Token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise UnauthorizedError("Invalid token", {"error": str(e)})
    
    async def get_user_roles(self, user: UserModel) -> List[RoleModel]:
        """获取用户角色"""
        try:
            role_ids = json.loads(user.role_ids)
        except:
            role_ids = []
        
        if not role_ids:
            return []
        
        result = await self.db.execute(
            select(RoleModel).where(RoleModel.id.in_(role_ids))
        )
        return list(result.scalars().all())
    
    async def get_user_permissions(self, user: UserModel) -> List[str]:
        """获取用户权限"""
        roles = await self.get_user_roles(user)
        permissions = set()
        for role in roles:
            try:
                role_perms = json.loads(role.permissions)
                permissions.update(role_perms)
            except:
                pass
        return list(permissions)
    
    async def login(
        self,
        username: str,
        password: str,
        tenant_slug: Optional[str] = None,
    ) -> Tuple[UserModel, str, str]:
        """用户登录"""
        # 查找用户（支持用户名或邮箱登录）
        query = select(UserModel).where(
            and_(
                UserModel.is_active == True,
                (UserModel.username == username) | (UserModel.email == username)
            )
        )
        
        if tenant_slug:
            query = query.where(UserModel.tenant_slug == tenant_slug)
        
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedError("用户名或密码错误")
        
        # 验证密码
        if not self.verify_password(password, user.hashed_password):
            raise UnauthorizedError("用户名或密码错误")
        
        # 获取角色和权限
        roles = await self.get_user_roles(user)
        permissions = await self.get_user_permissions(user)
        
        # 生成 Token
        access_token = self.create_access_token(
            user_id=user.id,
            tenant_slug=user.tenant_slug,
            username=user.username,
            email=user.email,
            roles=[r.name for r in roles],
            permissions=permissions,
        )
        
        refresh_token = self.create_refresh_token(
            user_id=user.id,
            tenant_slug=user.tenant_slug,
            username=user.username,
            email=user.email,
        )
        
        # 存储 Refresh Token
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        token_model = RefreshTokenModel(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        self.db.add(token_model)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user, access_token, refresh_token
    
    async def register(
        self,
        username: str,
        email: str,
        password: str,
        tenant_slug: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> UserModel:
        """用户注册"""
        # 使用默认租户
        if not tenant_slug:
            tenant_slug = settings.default_tenant_slug
        
        # 检查租户是否存在
        tenant = await self.db.execute(
            select(TenantModel).where(TenantModel.slug == tenant_slug)
        )
        tenant = tenant.scalar_one_or_none()
        if not tenant:
            raise NotFoundError(f"租户 '{tenant_slug}' 不存在")
        
        # 检查用户名是否已存在
        existing = await self.db.execute(
            select(UserModel).where(
                and_(
                    UserModel.tenant_slug == tenant_slug,
                    (UserModel.username == username) | (UserModel.email == email)
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValidationError("用户名或邮箱已存在")
        
        # 创建用户
        hashed_password = self.hash_password(password)
        user = UserModel(
            tenant_slug=tenant_slug,
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            role_ids="[]",
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """刷新 Token"""
        # 解码 Token
        payload = self.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise UnauthorizedError("无效的刷新令牌")
        
        user_id = payload.get("user_id")
        
        # 检查 Token 是否在数据库中且未撤销
        token_model = await self.db.execute(
            select(RefreshTokenModel).where(
                and_(
                    RefreshTokenModel.token == refresh_token,
                    RefreshTokenModel.is_revoked == False,
                    RefreshTokenModel.expires_at > datetime.utcnow(),
                )
            )
        )
        token_model = token_model.scalar_one_or_none()
        
        if not token_model:
            raise UnauthorizedError("刷新令牌已过期或已撤销")
        
        # 获取用户
        user = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise UnauthorizedError("用户不存在或已禁用")
        
        # 撤销旧的 Refresh Token
        token_model.is_revoked = True
        token_model.revoked_at = datetime.utcnow()
        
        # 获取角色和权限
        roles = await self.get_user_roles(user)
        permissions = await self.get_user_permissions(user)
        
        # 生成新的 Token
        new_access_token = self.create_access_token(
            user_id=user.id,
            tenant_slug=user.tenant_slug,
            username=user.username,
            email=user.email,
            roles=[r.name for r in roles],
            permissions=permissions,
        )
        
        new_refresh_token = self.create_refresh_token(
            user_id=user.id,
            tenant_slug=user.tenant_slug,
            username=user.username,
            email=user.email,
        )
        
        # 存储新的 Refresh Token
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        new_token_model = RefreshTokenModel(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at,
        )
        self.db.add(new_token_model)
        await self.db.commit()
        
        return new_access_token, new_refresh_token
    
    async def logout(self, refresh_token: Optional[str], user_id: Optional[int] = None):
        """登出（撤销 Refresh Token）"""
        if refresh_token:
            # 撤销指定的 Refresh Token
            token_model = await self.db.execute(
                select(RefreshTokenModel).where(RefreshTokenModel.token == refresh_token)
            )
            token_model = token_model.scalar_one_or_none()
            if token_model:
                token_model.is_revoked = True
                token_model.revoked_at = datetime.utcnow()
                await self.db.commit()
        
        if user_id:
            # 撤销用户所有的 Refresh Token
            result = await self.db.execute(
                select(RefreshTokenModel).where(
                    and_(
                        RefreshTokenModel.user_id == user_id,
                        RefreshTokenModel.is_revoked == False,
                    )
                )
            )
            for token in result.scalars().all():
                token.is_revoked = True
                token.revoked_at = datetime.utcnow()
            await self.db.commit()
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> UserModel:
        """修改密码"""
        # 获取用户
        user = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("用户不存在")
        
        # 验证旧密码
        if not self.verify_password(old_password, user.hashed_password):
            raise UnauthorizedError("原密码错误")
        
        # 更新密码
        user.hashed_password = self.hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        
        # 撤销所有 Refresh Token
        await self.logout(None, user_id)
        
        return user
    
    async def verify_access_token(self, token: str) -> dict:
        """验证 Access Token"""
        payload = self.decode_token(token)
        
        if payload.get("type") != "access":
            raise UnauthorizedError("无效的访问令牌")
        
        # 检查用户是否存在且活跃
        user_id = payload.get("user_id")
        user = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise UnauthorizedError("用户不存在或已禁用")
        
        return payload