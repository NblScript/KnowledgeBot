"""角色服务"""

from typing import Optional, List
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import RoleModel, TenantModel
from libs.common.exceptions import NotFoundError, ConflictError, ValidationError


class RoleService:
    """角色服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_role(
        self,
        tenant_slug: str,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        is_default: bool = False,
    ) -> RoleModel:
        """创建角色"""
        # 检查租户是否存在
        tenant = await self.db.execute(
            select(TenantModel).where(TenantModel.slug == tenant_slug)
        )
        if not tenant.scalar_one_or_none():
            raise NotFoundError(f"租户 '{tenant_slug}' 不存在")
        
        # 检查角色名是否已存在
        existing = await self.db.execute(
            select(RoleModel).where(
                and_(
                    RoleModel.tenant_slug == tenant_slug,
                    RoleModel.name == name,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"角色 '{name}' 已存在")
        
        # 如果设置为默认角色，取消其他默认角色
        if is_default:
            result = await self.db.execute(
                select(RoleModel).where(
                    and_(
                        RoleModel.tenant_slug == tenant_slug,
                        RoleModel.is_default == True,
                    )
                )
            )
            for role in result.scalars().all():
                role.is_default = False
        
        # 创建角色
        role = RoleModel(
            tenant_slug=tenant_slug,
            name=name,
            description=description,
            permissions=json.dumps(permissions or []),
            is_default=is_default,
            is_active=True,
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        return role
    
    async def get_role(self, role_id: int, tenant_slug: Optional[str] = None) -> Optional[RoleModel]:
        """获取角色"""
        query = select(RoleModel).where(RoleModel.id == role_id)
        if tenant_slug:
            query = query.where(RoleModel.tenant_slug == tenant_slug)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_roles(
        self,
        tenant_slug: str,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[RoleModel], int]:
        """获取角色列表"""
        query = select(RoleModel).where(RoleModel.tenant_slug == tenant_slug)
        count_query = select(RoleModel.id).where(RoleModel.tenant_slug == tenant_slug)
        
        if is_active is not None:
            query = query.where(RoleModel.is_active == is_active)
            count_query = count_query.where(RoleModel.is_active == is_active)
        
        # 计数
        total = await self.db.execute(count_query)
        total = len(list(total.all()))
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(RoleModel.id.desc())
        result = await self.db.execute(query)
        roles = list(result.scalars().all())
        
        return roles, total
    
    async def update_role(
        self,
        role_id: int,
        tenant_slug: Optional[str] = None,
        **kwargs,
    ) -> RoleModel:
        """更新角色"""
        role = await self.get_role(role_id, tenant_slug)
        if not role:
            raise NotFoundError("角色不存在")
        
        # 更新字段
        for key, value in kwargs.items():
            if value is not None:
                if key == "permissions" and isinstance(value, list):
                    setattr(role, key, json.dumps(value))
                elif key == "is_default" and value:
                    # 如果设置为默认角色，取消其他默认角色
                    result = await self.db.execute(
                        select(RoleModel).where(
                            and_(
                                RoleModel.tenant_slug == role.tenant_slug,
                                RoleModel.is_default == True,
                                RoleModel.id != role_id,
                            )
                        )
                    )
                    for r in result.scalars().all():
                        r.is_default = False
                    setattr(role, key, value)
                else:
                    setattr(role, key, value)
        
        await self.db.commit()
        await self.db.refresh(role)
        
        return role
    
    async def delete_role(self, role_id: int, tenant_slug: Optional[str] = None) -> bool:
        """删除角色"""
        role = await self.get_role(role_id, tenant_slug)
        if not role:
            raise NotFoundError("角色不存在")
        
        if role.is_default:
            raise ValidationError("不能删除默认角色")
        
        await self.db.delete(role)
        await self.db.commit()
        
        return True
    
    async def get_tenant_default_role(self, tenant_slug: str) -> Optional[RoleModel]:
        """获取租户默认角色"""
        result = await self.db.execute(
            select(RoleModel).where(
                and_(
                    RoleModel.tenant_slug == tenant_slug,
                    RoleModel.is_default == True,
                    RoleModel.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()