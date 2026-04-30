# Celery Worker 启动脚本

worker:
	celery -A app.celery_app worker \
		--loglevel=info \
		--queue=processing \
		--concurrency=4 \
		--logfile=logs/worker.log

worker_beat:
	celery -A app.celery_app beat --loglevel=info

flower:
	celery -A app.celery_app flower --port=5555