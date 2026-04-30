"""API v1 路由"""

from fastapi import APIRouter

from app.api.v1 import chat, system

router = APIRouter()

router.include_router(system.router, prefix="/system", tags=["System"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
