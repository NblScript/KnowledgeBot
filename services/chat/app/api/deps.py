"""依赖注入"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in get_db():
        yield session
