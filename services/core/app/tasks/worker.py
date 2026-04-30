"""Celery worker 启动脚本"""

import logging

from app.tasks.celery_app import celery_app

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info"])