"""API v1 module"""

from fastapi import APIRouter

from app.api.v1.embeddings import router as embeddings_router

router = APIRouter()

router.include_router(embeddings_router, prefix="/embeddings", tags=["embeddings"])