"""用户服务"""

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import UserModel, RoleModel, TenantModel
from app.services.auth_service import AuthService
from libs.common.exceptions import NotFoundError, ValidationError, ConflictError


class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        tenant_slug: str,
        full_name: Optional[str] = None,
        role_ids: Optional[List[int]] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> UserModel:
        """创建用户"""
        # 检查租户是否存在
        tenant = await self.db.execute(
            select(TenantModel).where(TenantModel.slug == tenant_slug)
        )
        tenant = tenant.scalar_one_or_none()
        if not tenant:
            raise NotFoundError(f"租户 '{tenant_slug}' 不存在")
        
        # 检查用户名/邮箱是否已存在
        existing = await self.db.execute(
            select(UserModel).where(
                and_(
                    UserModel.tenant_slug == tenant_slug,
                    or_(UserModel.username == username, UserModel.email == email)
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("用户名或邮箱已存在")
        
        # 验证角色
        if role_ids:
            roles_result = await self.db.execute(
                select(RoleModel).where(
                    and_(
                        RoleModel.id.in_(role_ids),
                        RoleModel.tenant_slug == tenant_slug,
                    )
                )
            )
            valid_roles = list(roles_result.scalars().all())
            if len(valid_roles) != len(role_ids):
                raise ValidationError("部分角色不存在或不属于该租户")
        
        # 创建用户
        hashed_password = self.auth_service.hash_password(password)
        user = UserModel(
            tenant_slug=tenant_slug,
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
            role_ids=json.dumps(role_ids or []),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user(self, user_id: int, tenant_slug: Optional[str] = None) -> Optional[UserModel]:
        """获取用户"""
        query = select(UserModel).where(UserModel.id == user_id)
        if tenant_slug:
            query = query.where(UserModel.tenant_slug == tenant_slug)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_users(
        self,
        tenant_slug: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[UserModel], int]:
        """获取用户列表"""
        query = select(UserModel)
        count_query = select(UserModel.id)
        
        if tenant_slug:
            query = query.where(UserModel.tenant_slug == tenant_slug)
            count_query = count_query.where(UserModel.tenant_slug == tenant_slug)
        
        if is_active is not None:
            query = query.where(UserModel.is_active == is_active)
            count_query = count_query.where(UserModel.is_active == is_active)
        
        # 计数
        total = await self.db.execute(count_query)
        total = len(list(total.all()))
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(UserModel.id.desc())
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def update_user(
        self,
        user_id: int,
        tenant_slug: Optional[str] = None,
        **kwargs,
    ) -> UserModel:
        """更新用户"""
        user = await self.get_user(user_id, tenant_slug)
        if not user:
            raise NotFoundError("用户不存在")
        
        # 更新字段
        for key, value in kwargs.items():
            if value is not None:
                if key == "role_ids":
                    # 验证角色
                    if value:
                        roles_result = await self.db.execute(
                            select(RoleModel).where(
                                and_(
                                    RoleModel.id.in_(value),
                                    RoleModel.tenant_slug == user.tenant_slug,
                                )
                            )
                        )
                        valid_roles = list(roles_result.scalars().all())
                        if len(valid_roles) != len(value):
                            raise ValidationError("部分角色不存在或不属于该租户")
                    setattr(user, key, json.dumps(value))
                else:
                    setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int, tenant_slug: Optional[str] = None) -> bool:
        """删除用户"""
        user = await self.get_user(user_id, tenant_slug)
        if not user:
            raise NotFoundError("用户不存在")
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def assign_roles(
        self,
        user_id: int,
        role_ids: List[int],
        tenant_slug: Optional[str] = None,
    ) -> UserModel:
        """分配角色"""
        return await self.update_user(user_id, tenant_slug, role_ids=role_ids)
    
    async def get_user_with_roles(self, user_id: int) -> dict:
        """获取用户及其角色、权限"""
        user = await self.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        
        roles = await self.auth_service.get_user_roles(user)
        permissions = await self.auth_service.get_user_permissions(user)
        
        return {
            "user": user,
            "roles": roles,
            "permissions": permissions,
        }
    
    async def reset_password(
        self,
        user_id: int,
        new_password: str,
        tenant_slug: Optional[str] = None,
    ) -> bool:
        """重置密码（管理员操作）"""
        user = await self.get_user(user_id, tenant_slug)
        if not user:
            raise NotFoundError("用户不存在")
        
        user.hashed_password = self.auth_service.hash_password(new_password)
        await self.db.commit()
        
        return True