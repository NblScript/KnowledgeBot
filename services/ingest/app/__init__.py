"""Ingest Service - 文档摄入服务"""

from app.config import settings
from app.celery_app import celery_app

__version__ = "1.0.0"

__all__ = [
    "settings",
    "celery_app",
    "__version__",
]