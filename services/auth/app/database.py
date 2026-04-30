"""数据库配置"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey, Index
from datetime import datetime
from typing import Optional
import uuid

from app.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """声明基类"""
    pass


class TimestampMixin:
    """时间戳混入类"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class TenantModel(Base, TimestampMixin):
    """租户模型"""
    __tablename__ = "tenants"
    __table_args__ = {"schema": settings.database_schema}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 格式的租户配置
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, slug={self.slug}, name={self.name})>"


class RoleModel(Base, TimestampMixin):
    """角色模型"""
    __tablename__ = "roles"
    __table_args__ = (
        Index("ix_roles_tenant_slug", "tenant_slug"),
        Index("ix_roles_tenant_name", "tenant_slug", "name", unique=True),
        {"schema": settings.database_schema}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_slug: Mapped[str] = mapped_column(String(50), ForeignKey(f"{settings.database_schema}.tenants.slug"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    permissions: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON 格式的权限列表
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<Role(id={self.id}, tenant={self.tenant_slug}, name={self.name})>"


class UserModel(Base, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_tenant_email", "tenant_slug", "email", unique=True),
        Index("ix_users_tenant_username", "tenant_slug", "username", unique=True),
        {"schema": settings.database_schema}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_slug: Mapped[str] = mapped_column(String(50), ForeignKey(f"{settings.database_schema}.tenants.slug"), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role_ids: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON 格式的角色ID列表
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, tenant={self.tenant_slug}, email={self.email})>"


class PermissionModel(Base, TimestampMixin):
    """权限模型"""
    __tablename__ = "permissions"
    __table_args__ = {"schema": settings.database_schema}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)  # 资源类型
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # 动作: create, read, update, delete, etc.
    
    def __repr__(self):
        return f"<Permission(code={self.code}, name={self.name})>"


class RefreshTokenModel(Base, TimestampMixin):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_user", "user_id"),
        {"schema": settings.database_schema}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{settings.database_schema}.users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 创建 schema
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.database_schema}")
        # 创建表
        await conn.run_sync(Base.metadata.create_all)