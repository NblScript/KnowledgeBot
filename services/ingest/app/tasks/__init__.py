"""Celery 任务模块"""

from app.tasks.document_tasks import (
    batch_process_documents_task,
    health_check,
    process_document_content_task,
    process_document_task,
)

__all__ = [
    "process_document_task",
    "process_document_content_task",
    "batch_process_documents_task",
    "health_check",
]