# Ingest Service

文档摄入服务 - 异步处理文档解析、分块和向量化

## 功能特性

- 文档解析（PDF、Word、Markdown、HTML、纯文本）
- 智能分块（按段落、句子分割）
- 异步向量化（通过 Embedding Service）
- 任务队列管理（Celery + Redis）
- 批量处理支持

## 服务架构

```
┌──────────────────────────────────────────────┐
│           Ingest Service (Port 8005)         │
├──────────────────────────────────────────────┤
│  API Layer (FastAPI)                         │
│  - POST /v1/tasks         创建任务            │
│  - GET  /v1/tasks/{id}   查询状态            │
│  - POST /v1/tasks/batch  批量任务            │
│  - GET  /v1/queue/stats  队列统计            │
├──────────────────────────────────────────────┤
│  Celery Worker                               │
│  - process_document_task                    │
│  - batch_process_documents_task             │
├──────────────────────────────────────────────┤
│  Document Processor                         │
│  - 解析文档内容                              │
│  - 智能分块                                  │
└──────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────┐      ┌─────────────────┐
│  Knowledge  │      │    Embedding    │
│  Service    │      │    Service      │
│  (Port 8002)│      │   (Port 8003)   │
└─────────────┘      └─────────────────┘
```

## API 端点

### 创建任务
```http
POST /v1/tasks
Content-Type: application/json

{
  "task_type": "document_process",
  "doc_id": "doc_xxx",
  "kb_id": "kb_xxx",
  "file_path": "documents/doc.pdf",
  "file_name": "doc.pdf",
  "file_type": "pdf"
}
```

### 查询任务状态
```http
GET /v1/tasks/{task_id}

Response:
{
  "task_id": "xxx",
  "status": "completed",
  "progress": 100,
  "message": "Processed 10 chunks",
  "result": {
    "chunk_count": 10,
    "total_tokens": 5000
  }
}
```

### 队列统计
```http
GET /v1/queue/stats

Response:
{
  "active_tasks": 2,
  "reserved_tasks": 5,
  "workers": ["worker-1@host"],
  "registered_tasks": ["app.tasks.document_tasks.process_document"]
}
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| APP_PORT | 8005 | 服务端口 |
| REDIS_HOST | localhost | Redis 主机 |
| REDIS_PORT | 6379 | Redis 端口 |
| KNOWLEDGE_SERVICE_URL | http://knowledge:8002 | Knowledge Service URL |
| EMBEDDING_SERVICE_URL | http://embedding:8003 | Embedding Service URL |
| CHUNK_SIZE | 500 | 分块大小 |
| CHUNK_OVERLAP | 50 | 分块重叠 |

## 运行

### 启动 API 服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8005
```

### 启动 Celery Worker
```bash
celery -A app.celery_app worker --queue=processing --loglevel=info
```

### 启动 Celery Beat（定时任务调度器）
```bash
celery -A app.celery_app beat --loglevel=info
```

### 使用 Docker
```bash
docker build -t ingest-service .
docker run -p 8005:8005 \
  -e REDIS_HOST=redis \
  -e KNOWLEDGE_SERVICE_URL=http://knowledge:8002 \
  -e EMBEDDING_SERVICE_URL=http://embedding:8003 \
  ingest-service
```

## 任务类型

1. **document_process**
   - 从 MinIO 读取文件
   - 解析文档内容
   - 智能分块
   - 向量化并存储

2. **batch_process**
   - 批量处理多个文档
   - 并行执行
   - 统计结果

## 文档处理流程

1. 接收处理请求
2. 从 MinIO 获取文件
3. 解析文档（PDF/Word/Markdown/HTML等）
4. 智能分块（按段落、句子）
5. 调用 Embedding Service 向量化
6. 调用 Knowledge Service 存储分块
7. 更新文档状态

## 监控

- **Health Check**: `GET /health`
- **Celery Status**: `GET /health/celery`
- **Queue Stats**: `GET /v1/queue/stats`

## 配置

详细配置见 `app/config.py`