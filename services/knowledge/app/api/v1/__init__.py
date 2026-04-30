"""API v1 路由"""

from fastapi import APIRouter

from app.api.v1 import documents, knowledge_bases

router = APIRouter()

# 注册子路由
router.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
# 文档路由 - 上传和列表在知识库下
router.include_router(documents.kb_router, prefix="/knowledge-bases", tags=["documents"])
# 文档直接操作路由 (详情、处理、删除)
router.include_router(documents.router, prefix="/documents", tags=["documents"])