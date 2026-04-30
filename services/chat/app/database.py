"""数据库连接管理"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类"""
    pass


# PostgreSQL 异步引擎
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.app_debug,
    pool_size=5,
    max_overflow=10,
)

# 异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """数据库会话上下文管理器"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """初始化数据库 - 创建 schema 和表"""
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        # 创建 schema（如果不存在）
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.postgres_schema}"))
        
        # 设置默认 search_path
        await conn.execute(text(f"SET search_path TO {settings.postgres_schema}, public"))
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
