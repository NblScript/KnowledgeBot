.PHONY: help build up down logs test clean restart

# 默认目标
help:
	@echo "KnowledgeBot 微服务管理"
	@echo ""
	@echo "使用方法: make [目标]"
	@echo ""
	@echo "目标:"
	@echo "  build    - 构建所有服务"
	@echo "  up       - 启动所有服务"
	@echo "  down     - 停止所有服务"
	@echo "  logs     - 查看日志"
	@echo "  test     - 运行测试"
	@echo "  clean    - 清理数据"
	@echo "  restart  - 重启服务"
	@echo ""
	@echo "单服务操作:"
	@echo "  make logs SERVICE=auth"
	@echo "  make restart SERVICE=chat"
	@echo ""

# 构建所有服务
build:
	docker-compose build

# 启动所有服务
up:
	docker-compose up -d
	@echo ""
	@echo "服务启动完成!"
	@echo "API Gateway: http://localhost"
	@echo "Auth API:    http://localhost:8001/docs"
	@echo "Knowledge:   http://localhost:8002/docs"
	@echo "Embedding:   http://localhost:8003/docs"
	@echo "Chat:        http://localhost:8004/docs"
	@echo "Ingest:      http://localhost:8005/docs"
	@echo "Flower:      http://localhost:5555 (需 make up-monitoring)"

# 启动带监控
up-monitoring:
	docker-compose --profile monitoring up -d

# 停止所有服务
down:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f $(SERVICE)

# 运行测试
test:
	@echo "运行 Auth Service 测试..."
	cd services/auth && python -m pytest tests/ -v
	@echo "运行 Knowledge Service 测试..."
	cd services/knowledge && python -m pytest tests/ -v
	@echo "运行 Embedding Service 测试..."
	cd services/embedding && python -m pytest tests/ -v
	@echo "运行 Chat Service 测试..."
	cd services/chat && python -m pytest tests/ -v
	@echo "运行 Ingest Service 测试..."
	cd services/ingest && python -m pytest tests/ -v

# 清理数据
clean:
	docker-compose down -v
	@echo "数据已清理"

# 重启服务
restart:
	docker-compose restart $(SERVICE)

# 初始化数据库
init-db:
	@echo "初始化 Auth Service 数据库..."
	cd services/auth && alembic upgrade head
	@echo "初始化 Knowledge Service 数据库..."
	cd services/knowledge && alembic upgrade head
	@echo "初始化 Chat Service 数据库..."
	cd services/chat && alembic upgrade head

# 开发模式（本地运行）
dev-auth:
	cd services/auth && uvicorn app.main:app --reload --port 8001

dev-knowledge:
	cd services/knowledge && uvicorn app.main:app --reload --port 8002

dev-embedding:
	cd services/embedding && uvicorn app.main:app --reload --port 8003

dev-chat:
	cd services/chat && uvicorn app.main:app --reload --port 8004

dev-ingest:
	cd services/ingest && uvicorn app.main:app --reload --port 8005

dev-worker:
	cd services/ingest && celery -A app.celery_app worker -l info

# 检查服务状态
status:
	@echo "服务状态:"
	@docker-compose ps

# 健康检查
health:
	@echo "检查服务健康状态..."
	@curl -s http://localhost:8001/health || echo "Auth: DOWN"
	@curl -s http://localhost:8002/health || echo "Knowledge: DOWN"
	@curl -s http://localhost:8003/v1/embeddings/health || echo "Embedding: DOWN"
	@curl -s http://localhost:8004/health || echo "Chat: DOWN"
	@curl -s http://localhost:8005/health || echo "Ingest: DOWN"

# ==================== 监控 ====================

# 启动监控栈
monitoring-up:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
	@echo ""
	@echo "监控服务启动完成!"
	@echo "Prometheus:  http://localhost:9090"
	@echo "Grafana:     http://localhost:3000 (admin/admin123)"
	@echo "Alertmanager: http://localhost:9093"

# 停止监控栈
monitoring-down:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down

# 查看监控日志
monitoring-logs:
	docker-compose -f docker-compose.monitoring.yml logs -f

# ==================== CI/CD ====================

# 本地运行 CI 检查
ci-lint:
	@echo "运行代码检查..."
	pip install ruff black isort mypy
	ruff check services/ libs/
	black --check services/ libs/
	isort --check-only services/ libs/

# 本地运行测试（模拟 CI）
ci-test:
	@echo "运行所有测试..."
	./scripts/run-tests.sh

# 构建所有镜像
ci-build:
	@echo "构建所有 Docker 镜像..."
	docker build -t knowledgebot-auth:latest -f services/auth/Dockerfile services/auth
	docker build -t knowledgebot-knowledge:latest -f services/knowledge/Dockerfile services/knowledge
	docker build -t knowledgebot-embedding:latest -f services/embedding/Dockerfile services/embedding
	docker build -t knowledgebot-chat:latest -f services/chat/Dockerfile services/chat
	docker build -t knowledgebot-ingest:latest -f services/ingest/Dockerfile services/ingest
	docker build -t knowledgebot-web:latest -f web/Dockerfile web

# 安全扫描
security-scan:
	@echo "运行安全扫描..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image knowledgebot-auth:latest
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image knowledgebot-knowledge:latest