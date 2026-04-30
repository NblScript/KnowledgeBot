"""任务管理 API"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.schemas.task import (
    BatchTaskCreate,
    BatchTaskStatus,
    TaskCreate,
    TaskInfo,
    TaskStatus,
    TaskStatusResponse,
    TaskType,
)
from app.tasks.document_tasks import (
    batch_process_documents_task,
    process_document_content_task,
    process_document_task,
)

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskInfo,
    status_code=status.HTTP_202_ACCEPTED,
    summary="创建处理任务",
)
async def create_task(task: TaskCreate):
    """
    创建文档处理任务
    
    - 将任务提交到 Celery 队列
    - 返回任务 ID 用于查询状态
    """
    if task.task_type == TaskType.DOCUMENT_PROCESS:
        # 提交文档处理任务
        result = process_document_task.delay(
            doc_id=task.doc_id,
            kb_id=task.kb_id,
            file_path=task.file_path,
            file_name=task.file_name,
            file_type=task.file_type,
        )
        
        return TaskInfo(
            task_id=result.id,
            task_type=task.task_type,
            status=TaskStatus.PENDING,
            doc_id=task.doc_id,
            kb_id=task.kb_id,
        )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported task type: {task.task_type}",
    )


@router.post(
    "/tasks/content",
    response_model=TaskInfo,
    status_code=status.HTTP_202_ACCEPTED,
    summary="创建内容处理任务",
)
async def create_content_task(task_data: dict):
    """
    创建文档处理任务（直接传内容）
    
    用于直接传递文件内容（Base64编码），不依赖文件存储
    
    Request body:
        - doc_id: 文档 ID
        - kb_id: 知识库 ID
        - file_content: Base64 编码的文件内容
        - file_name: 文件名
        - file_type: 文件类型
    """
    doc_id = task_data.get("doc_id")
    kb_id = task_data.get("kb_id")
    file_content = task_data.get("file_content")
    file_name = task_data.get("file_name")
    file_type = task_data.get("file_type")
    
    if not all([doc_id, kb_id, file_content, file_name, file_type]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields",
        )
    
    result = process_document_content_task.delay(
        doc_id=doc_id,
        kb_id=kb_id,
        file_content_b64=file_content,
        file_name=file_name,
        file_type=file_type,
    )
    
    return TaskInfo(
        task_id=result.id,
        task_type=TaskType.DOCUMENT_PROCESS,
        status=TaskStatus.PENDING,
        doc_id=doc_id,
        kb_id=kb_id,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    summary="获取任务状态",
)
async def get_task_status(task_id: str):
    """
    获取任务执行状态
    
    - PENDING: 等待处理
    - PROCESSING: 正在处理
    - COMPLETED: 处理完成
    - FAILED: 处理失败
    """
    result = AsyncResult(task_id, app=celery_app)
    
    # 映射状态
    status_map = {
        "PENDING": TaskStatus.PENDING,
        "STARTED": TaskStatus.PROCESSING,
        "PROCESSING": TaskStatus.PROCESSING,
        "SUCCESS": TaskStatus.COMPLETED,
        "FAILURE": TaskStatus.FAILED,
        "RETRY": TaskStatus.PROCESSING,
        "REVOKED": TaskStatus.CANCELLED,
    }
    
    current_status = status_map.get(result.status.value, TaskStatus.PENDING)
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=current_status,
    )
    
    # 获取结果或错误信息
    if result.ready():
        try:
            task_result = result.get(timeout=1)
            if isinstance(task_result, dict):
                response.result = task_result
                if task_result.get("status") == "completed":
                    response.status = TaskStatus.COMPLETED
                    response.message = f"Processed {task_result.get('chunk_count', 0)} chunks"
                else:
                    response.status = TaskStatus.FAILED
                    response.error = task_result.get("error")
        except Exception as e:
            response.status = TaskStatus.FAILED
            response.error = str(e)
    elif result.state == "PROCESSING":
        # 获取进度信息
        meta = result.info or {}
        response.progress = meta.get("progress", 0)
        response.message = f"Processing document {meta.get('doc_id', '')}"
    
    return response


@router.post(
    "/tasks/batch",
    response_model=BatchTaskStatus,
    status_code=status.HTTP_202_ACCEPTED,
    summary="批量创建任务",
)
async def create_batch_tasks(batch: BatchTaskCreate):
    """
    批量创建处理任务
    
    用于一次性提交多个文档处理任务
    """
    # 获取文档信息（这里需要调用 Knowledge Service）
    # 简化处理，假设前端已经提供完整信息
    
    # 实际使用时需要：
    # 1. 调用 Knowledge Service 获取文档列表
    # 2. 提交批量任务
    
    batch_id = f"batch_{batch.kb_id}_{len(batch.doc_ids)}"
    
    # 构建任务列表（这里需要从 Knowledge Service 获取文档信息）
    # 暂时返回 batch_id
    return BatchTaskStatus(
        batch_id=batch_id,
        total=len(batch.doc_ids),
        completed=0,
        failed=0,
        pending=len(batch.doc_ids),
        tasks=[],
    )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="取消任务",
)
async def cancel_task(task_id: str):
    """
    取消正在执行的任务
    
    注意：只有在队列中等待的任务可以被取消
    """
    result = AsyncResult(task_id, app=celery_app)
    
    if result.state in ("PENDING", "STARTED"):
        result.revoke(terminate=True)
        return None
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Task already {result.state.value}",
    )


@router.get(
    "/queue/stats",
    summary="获取队列统计",
)
async def get_queue_stats():
    """
    获取队列统计信息
    
    - 等待中的任务数
    - 正在执行的任务数
    - Worker 状态
    """
    # 获取 Celery inspect
    inspect = celery_app.control.inspect()
    
    # 获取活跃任务
    active = inspect.active() or {}
    active_count = sum(len(tasks) for tasks in active.values())
    
    # 获取预约任务
    reserved = inspect.reserved() or {}
    reserved_count = sum(len(tasks) for tasks in reserved.values())
    
    # 获取注册任务
    registered = inspect.registered() or {}
    
    return {
        "active_tasks": active_count,
        "reserved_tasks": reserved_count,
        "workers": list(active.keys()),
        "registered_tasks": list(registered.keys()),
    }