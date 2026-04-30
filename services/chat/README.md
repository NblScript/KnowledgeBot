# Chat Service

RAG 对话服务 - 提供智能问答能力

## 功能

- **对话管理**: 创建、查询、删除对话
- **RAG 问答**: 基于知识库的检索增强生成
- **流式响应**: 支持 SSE 流式输出
- **多 LLM 支持**: OpenAI、通义千问、智谱、SiliconFlow

## 服务架构

```
Chat Service (Port 8004)
├── /v1/chat/completions      - 创建对话补全
├── /v1/chat/completions/stream - 流式对话补全
├── /v1/chat/conversations   - 对话管理
└── /v1/system/health        - 健康检查
```

## 依赖服务

- **Embedding Service** (http://embedding:8003): 向量检索服务
- **PostgreSQL** (knowledgebot_chat schema): 对话数据存储

## 配置

参考 `.env.example` 进行配置：

```bash
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=knowledgebot
POSTGRES_PASSWORD=knowledgebot123
POSTGRES_DB=knowledgebot
POSTGRES_SCHEMA=chat

# Embedding Service
EMBEDDING_SERVICE_URL=http://embedding:8003

# LLM 配置
LLM_PROVIDER=mock
LLM_MODEL=gpt-4o-mini
```

## 运行

### Docker

```bash
docker build -t chat-service .
docker run -p 8004:8004 chat-service
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## API 示例

### 创建对话补全

```bash
curl -X POST http://localhost:8004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "kb_id": "your-kb-id",
    "messages": [{"role": "user", "content": "什么是 RAG?"}],
    "top_k": 5,
    "temperature": 0.7
  }'
```

### 流式响应

```bash
curl -X POST http://localhost:8004/v1/chat/completions/stream \
  -H "Content-Type: application/json" \
  -d '{
    "kb_id": "your-kb-id",
    "messages": [{"role": "user", "content": "什么是 RAG?"}]
  }'
```

### 获取对话列表

```bash
curl http://localhost:8004/v1/chat/conversations
```

### 获取对话详情

```bash
curl http://localhost:8004/v1/chat/conversations/{conv_id}
```

## 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "initial"

# 执行迁移
alembic upgrade head
```

## 项目结构

```
services/chat/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── api/
│   │   ├── deps.py       # 依赖注入
│   │   └── v1/
│   │       ├── chat.py   # 对话路由
│   │       └── system.py # 系统路由
│   ├── models/
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/
│   │   ├── chat.py
│   │   └── common.py
│   ├── llm/
│   │   └── llm_service.py
│   ├── clients/
│   │   └── embedding.py  # Embedding Service 客户端
│   └── services/
│       └── retrieval_service.py
├── alembic/              # 数据库迁移
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example
```
