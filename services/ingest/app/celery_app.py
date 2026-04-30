"""Celery 应用配置"""

from celery import Celery

from app.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "ingest_service",
    broker=settings.get_celery_broker_url(),
    backend=settings.get_celery_backend_url(),
)

# Celery 配置
celery_app.conf.update(
    # 任务队列配置
    task_default_queue=settings.celery_task_queue,
    task_routes={
        "app.tasks.document_tasks.*": {"queue": settings.celery_task_queue},
    },
    
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 结果配置
    result_expires=3600,  # 结果保留 1 小时
    task_track_started=True,
    
    # 并发配置
    worker_prefetch_multiplier=1,  # 每次只取一个任务
    worker_concurrency=4,  # 并发 worker 数量
    
    # 任务时间限制
    task_soft_time_limit=300,  # 软限制 5 分钟
    task_time_limit=600,  # 硬限制 10 分钟
    
    # 重试配置
    task_acks_late=True,  # 任务完成后才确认
    task_reject_on_worker_lost=True,
    
    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])