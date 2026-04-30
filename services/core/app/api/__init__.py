"""API 路由导出"""

from fastapi import APIRouter

from app.api.v1 import chat, documents, knowledge_bases, retrieval, system

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    knowledge_bases.router,
    prefix="/knowledge-bases",
    tags=["knowledge-bases"],
)
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"],
)
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"],
)
api_router.include_router(
    retrieval.router,
    prefix="/retrieval",
    tags=["retrieval"],
)
api_router.include_router(
    system.router,
    tags=["system"],
)
