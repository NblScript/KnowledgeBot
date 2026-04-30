"""Celery 任务 - 异步文档处理"""

import asyncio
import time
from typing import Optional

from celery import Task

from app.celery_app import celery_app
from app.config import settings


class AsyncTask(Task):
    """支持异步函数的 Task 基类"""
    
    def __call__(self, *args, **kwargs):
        """重写调用方法，支持 async 函数"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_call(*args, **kwargs))
        finally:
            loop.close()
    
    async def _async_call(self, *args, **kwargs):
        """异步调用方法，由子类实现"""
        raise NotImplementedError


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.document_tasks.process_document",
    max_retries=3,
    default_retry_delay=60,
)
async def process_document_task(
    self,
    doc_id: str,
    kb_id: str,
    file_path: str,
    file_name: str,
    file_type: str,
) -> dict:
    """
    异步处理文档任务
    
    Args:
        doc_id: 文档 ID
        kb_id: 知识库 ID
        file_path: MinIO 中的文件路径
        file_name: 文件名
        file_type: 文件类型
    
    Returns:
        处理结果
    """
    from app.services.ingest_service import get_ingest_service
    
    start_time = time.time()
    
    try:
        # 更新任务状态
        self.update_state(
            state="PROCESSING",
            meta={"doc_id": doc_id, "progress": 0},
        )
        
        # 获取服务实例
        ingest_service = get_ingest_service()
        
        # 处理文档
        result = await ingest_service.process_document_from_storage(
            doc_id=doc_id,
            kb_id=kb_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
        )
        
        processing_time = time.time() - start_time
        
        if result.get("success"):
            return {
                "status": "completed",
                "doc_id": doc_id,
                "chunk_count": result.get("chunk_count", 0),
                "total_tokens": result.get("total_tokens", 0),
                "processing_time": processing_time,
            }
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as e:
        # 重试
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "failed",
                "doc_id": doc_id,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.document_tasks.process_document_content",
    max_retries=3,
)
async def process_document_content_task(
    self,
    doc_id: str,
    kb_id: str,
    file_content_b64: str,
    file_name: str,
    file_type: str,
) -> dict:
    """
    处理文档内容（Base64 编码）
    
    用于直接传递文件内容，不依赖 MinIO 存储
    
    Args:
        doc_id: 文档 ID
        kb_id: 知识库 ID
        file_content_b64: Base64 编码的文件内容
        file_name: 文件名
        file_type: 文件类型
    
    Returns:
        处理结果
    """
    import base64
    import time
    
    from app.services.ingest_service import get_ingest_service
    
    start_time = time.time()
    
    try:
        # 解码文件内容
        file_content = base64.b64decode(file_content_b64)
        
        # 更新任务状态
        self.update_state(
            state="PROCESSING",
            meta={"doc_id": doc_id, "progress": 0},
        )
        
        # 获取服务实例
        ingest_service = get_ingest_service()
        
        # 处理文档
        result = await ingest_service.process_document(
            doc_id=doc_id,
            kb_id=kb_id,
            file_content=file_content,
            file_name=file_name,
            file_type=file_type,
        )
        
        processing_time = time.time() - start_time
        
        if result.get("success"):
            return {
                "status": "completed",
                "doc_id": doc_id,
                "chunk_count": result.get("chunk_count", 0),
                "total_tokens": result.get("total_tokens", 0),
                "processing_time": processing_time,
            }
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as e:
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "failed",
                "doc_id": doc_id,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }


@celery_app.task(
    bind=True,
    name="app.tasks.document_tasks.batch_process_documents",
)
def batch_process_documents_task(self, tasks: list[dict]) -> dict:
    """
    批量处理文档
    
    Args:
        tasks: 任务列表，每个任务包含:
            - doc_id: 文档 ID
            - kb_id: 知识库 ID
            - file_path: 文件路径
            - file_name: 文件名
            - file_type: 文件类型
    
    Returns:
        批量处理结果
    """
    from celery import group
    
    # 创建并行任务组
    job = group(
        process_document_task.s(
            task["doc_id"],
            task["kb_id"],
            task["file_path"],
            task["file_name"],
            task["file_type"],
        )
        for task in tasks
    )
    
    # 执行并获取结果
    result = job.apply_async()
    results = result.get()
    
    # 统计结果
    completed = sum(1 for r in results if r.get("status") == "completed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    
    return {
        "total": len(tasks),
        "completed": completed,
        "failed": failed,
        "results": results,
    }


@celery_app.task(name="app.tasks.document_tasks.health_check")
def health_check() -> dict:
    """健康检查任务"""
    return {
        "status": "ok",
        "service": "ingest",
        "queue": settings.celery_task_queue,
    }