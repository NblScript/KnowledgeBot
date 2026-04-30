"""Celery 应用配置"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "knowledgebot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document_tasks"],
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务结果
    result_expires=3600,  # 1小时过期
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 任务路由
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "processing"},
    },
    
    # 重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
