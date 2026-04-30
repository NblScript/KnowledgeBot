"""租户服务"""

from typing import Optional, List
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import TenantModel, RoleModel
from app.config import settings
from libs.common.exceptions import NotFoundError, ConflictError, ValidationError


class TenantService:
    """租户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tenant(
        self,
        slug: str,
        name: str,
        description: Optional[str] = None,
        tenant_settings: Optional[dict] = None,
    ) -> TenantModel:
        """创建租户"""
        # 检查 slug 是否已存在
        existing = await self.db.execute(
            select(TenantModel).where(TenantModel.slug == slug)
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"租户 '{slug}' 已存在")
        
        # 创建租户
        tenant = TenantModel(
            slug=slug,
            name=name,
            description=description,
            is_active=True,
            settings=json.dumps(tenant_settings) if tenant_settings else None,
        )
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        
        # 创建默认角色
        await self._create_default_roles(slug)
        
        return tenant
    
    async def _create_default_roles(self, tenant_slug: str):
        """创建默认角色"""
        default_roles = [
            {
                "name": "admin",
                "description": "管理员角色，拥有所有权限",
                "permissions": ["*"],
                "is_default": False,
            },
            {
                "name": "user",
                "description": "普通用户角色",
                "permissions": ["documents:read", "documents:create", "chat:read", "chat:create"],
                "is_default": True,
            },
            {
                "name": "viewer",
                "description": "只读用户角色",
                "permissions": ["documents:read", "chat:read"],
                "is_default": False,
            },
        ]
        
        for role_data in default_roles:
            role = RoleModel(
                tenant_slug=tenant_slug,
                name=role_data["name"],
                description=role_data["description"],
                permissions=json.dumps(role_data["permissions"]),
                is_default=role_data["is_default"],
                is_active=True,
            )
            self.db.add(role)
        
        await self.db.commit()
    
    async def get_tenant(self, tenant_id: Optional[int] = None, slug: Optional[str] = None) -> Optional[TenantModel]:
        """获取租户"""
        if tenant_id:
            result = await self.db.execute(
                select(TenantModel).where(TenantModel.id == tenant_id)
            )
        elif slug:
            result = await self.db.execute(
                select(TenantModel).where(TenantModel.slug == slug)
            )
        else:
            return None
        
        return result.scalar_one_or_none()
    
    async def get_tenants(
        self,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[TenantModel], int]:
        """获取租户列表"""
        query = select(TenantModel)
        count_query = select(TenantModel.id)
        
        if is_active is not None:
            query = query.where(TenantModel.is_active == is_active)
            count_query = count_query.where(TenantModel.is_active == is_active)
        
        # 计数
        total = await self.db.execute(count_query)
        total = len(list(total.all()))
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(TenantModel.id.desc())
        result = await self.db.execute(query)
        tenants = list(result.scalars().all())
        
        return tenants, total
    
    async def update_tenant(
        self,
        tenant_id: int,
        **kwargs,
    ) -> TenantModel:
        """更新租户"""
        tenant = await self.get_tenant(tenant_id=tenant_id)
        if not tenant:
            raise NotFoundError("租户不存在")
        
        # 更新字段
        for key, value in kwargs.items():
            if value is not None:
                if key == "settings" and isinstance(value, dict):
                    setattr(tenant, key, json.dumps(value))
                else:
                    setattr(tenant, key, value)
        
        await self.db.commit()
        await self.db.refresh(tenant)
        
        return tenant
    
    async def delete_tenant(self, tenant_id: int) -> bool:
        """删除租户"""
        tenant = await self.get_tenant(tenant_id=tenant_id)
        if not tenant:
            raise NotFoundError("租户不存在")
        
        # 不允许删除默认租户
        if tenant.slug == settings.default_tenant_slug:
            raise ValidationError("不能删除默认租户")
        
        await self.db.delete(tenant)
        await self.db.commit()
        
        return True
    
    async def ensure_default_tenant(self) -> TenantModel:
        """确保默认租户存在"""
        tenant = await self.get_tenant(slug=settings.default_tenant_slug)
        if not tenant:
            tenant = await self.create_tenant(
                slug=settings.default_tenant_slug,
                name="Default Tenant",
                description="默认租户",
            )
        return tenant