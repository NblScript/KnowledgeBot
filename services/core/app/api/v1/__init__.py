"""API v1 路由"""

from app.api.v1 import chat, documents, knowledge_bases, retrieval, system
from fastapi import APIRouter

router = APIRouter()

# 注册子路由
router.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
# 文档路由 - 上传和列表在知识库下
router.include_router(documents.kb_router, prefix="/knowledge-bases", tags=["documents"])
# 文档直接操作路由 (详情、处理、删除)
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(retrieval.router, prefix="/retrieval", tags=["retrieval"])
router.include_router(system.router, tags=["system"])