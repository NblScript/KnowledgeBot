# Makefile for KnowledgeBot Core Service

.PHONY: help install dev test run docker-up docker-down clean

help:
	@echo "KnowledgeBot Core Service Commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Install development dependencies"
	@echo "  make test        - Run tests"
	@echo "  make run         - Run development server"
	@echo "  make worker      - Run Celery worker"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make lint        - Run linter"
	@echo "  make clean       - Clean cache files"

install:
	cd services/core && pip install -r requirements.txt

dev:
	cd services/core && pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx faker ruff

test:
	cd services/core && pytest -v

run:
	cd services/core && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd services/core && celery -A app.tasks.celery_app worker --loglevel=info

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

lint:
	ruff check services/core/app

clean:
	find services/core -type d -name "__pycache__" -exec rm -rf {} +
	find services/core -type f -name "*.pyc" -delete
	find services/core -type f -name ".pytest_cache" -exec rm -rf {} +

# Database commands
db-init:
	cd services/core && python -c "from app.database import engine; from app.models import Base; import asyncio; asyncio.run(engine.run_sync(Base.metadata.create_all))"

# Show routes
routes:
	cd services/core && python -c "from app.main import app; for r in app.routes: print(r.path, r.methods if hasattr(r, 'methods') else '')"
