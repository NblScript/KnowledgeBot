#!/bin/bash
# Ingest Service 本地运行脚本

set -e

echo "Starting Ingest Service..."

# 检查 Redis 连接
echo "Checking Redis connection..."
if ! nc -z localhost 6379 2>/dev/null; then
    echo "Warning: Redis is not running on localhost:6379"
    echo "Please start Redis first: docker run -d -p 6379:6379 redis:7-alpine"
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export APP_ENV="${APP_ENV:-development}"
export APP_PORT="${APP_PORT:-8005}"
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export KNOWLEDGE_SERVICE_URL="${KNOWLEDGE_SERVICE_URL:-http://localhost:8002}"
export EMBEDDING_SERVICE_URL="${EMBEDDING_SERVICE_URL:-http://localhost:8003}"

echo "Configuration:"
echo "  APP_PORT: $APP_PORT"
echo "  REDIS_HOST: $REDIS_HOST"
echo "  KNOWLEDGE_SERVICE_URL: $KNOWLEDGE_SERVICE_URL"
echo "  EMBEDDING_SERVICE_URL: $EMBEDDING_SERVICE_URL"
echo

# 安装依赖
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# 启动服务
case "${1:-api}" in
    api)
        echo "Starting API server..."
        uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
        ;;
    worker)
        echo "Starting Celery worker..."
        celery -A app.celery_app worker --queue=processing --loglevel=info --concurrency=4
        ;;
    flower)
        echo "Starting Celery Flower..."
        celery -A app.celery_app flower --port=5555
        ;;
    test)
        echo "Running tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 {api|worker|flower|test}"
        exit 1
        ;;
esac