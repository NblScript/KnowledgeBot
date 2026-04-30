# 环境变量配置

完整的环境变量说明。

## 核心配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_PROVIDER` | `openai` | LLM 提供商 |
| `LLM_MODEL` | `gpt-4o-mini` | 使用的模型 |
| `EMBEDDING_PROVIDER` | `openai` | Embedding 提供商 |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding 模型 |
| `EMBEDDING_DIM` | `1536` | 向量维度 |

## LLM 提供商配置

### OpenAI

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | API Key（必需） |
| `OPENAI_BASE_URL` | API 地址（可选） |

### 通义千问

| 变量 | 说明 |
|------|------|
| `QWEN_API_KEY` | API Key（必需） |

### 智谱 AI

| 变量 | 说明 |
|------|------|
| `ZHIPU_API_KEY` | API Key（必需） |

### SiliconFlow

| 变量 | 说明 |
|------|------|
| `SILICONFLOW_API_KEY` | API Key（必需） |

## 数据库配置

### PostgreSQL

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `POSTGRES_HOST` | `postgres` | 主机 |
| `POSTGRES_PORT` | `5432` | 端口 |
| `POSTGRES_USER` | `knowledgebot` | 用户名 |
| `POSTGRES_PASSWORD` | `knowledgebot123` | 密码 |
| `POSTGRES_DB` | `knowledgebot` | 数据库名 |

### Redis

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REDIS_HOST` | `redis` | 主机 |
| `REDIS_PORT` | `6379` | 端口 |
| `REDIS_PASSWORD` | `redis123` | 密码 |

### Milvus

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MILVUS_HOST` | `milvus` | 主机 |
| `MILVUS_PORT` | `19530` | 端口 |

### MinIO

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MINIO_ENDPOINT` | `minio:9000` | 地址 |
| `MINIO_ROOT_USER` | `minioadmin` | 用户名 |
| `MINIO_ROOT_PASSWORD` | `minioadmin` | 密码 |
| `MINIO_BUCKET` | `knowledgebot` | 存储桶 |

## 服务配置

### Auth Service

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AUTH_PORT` | `8001` | 服务端口 |
| `JWT_SECRET` | `secret` | JWT 密钥 |
| `JWT_ALGORITHM` | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh Token 有效期 |

### Knowledge Service

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `KNOWLEDGE_PORT` | `8002` | 服务端口 |

### Embedding Service

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `EMBEDDING_PORT` | `8003` | 服务端口 |

### Chat Service

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CHAT_PORT` | `8004` | 服务端口 |
| `MAX_CONTEXT_LENGTH` | `4000` | 最大上下文长度 |
| `DEFAULT_TOP_K` | `5` | 默认检索数量 |

### Ingest Service

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `INGEST_PORT` | `8005` | 服务端口 |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery Broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/1` | Celery Backend |
| `MAX_FILE_SIZE` | `52428800` | 最大文件大小 (50MB) |

### Gateway

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GATEWAY_PORT` | `80` | 网关端口 |

## 文档处理配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | `500` | 分块大小 |
| `CHUNK_OVERLAP` | `100` | 分块重叠 |
| `CHUNK_MIN_SIZE` | `50` | 最小分块大小 |

## 日志配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FORMAT` | `json` | 日志格式 |

## 多租户配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ENABLE_MULTI_TENANT` | `true` | 启用多租户 |
| `DEFAULT_TENANT_ID` | `default` | 默认租户 |

## 配置示例

```bash
# .env 文件示例

# LLM 配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key
LLM_MODEL=gpt-4o-mini

# Embedding 配置
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# 数据库密码（生产环境请修改）
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
MINIO_ROOT_PASSWORD=your-minio-password

# JWT 密钥（生产环境请修改）
JWT_SECRET=your-jwt-secret

# 文档处理
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# 日志
LOG_LEVEL=INFO
```

## 安全建议

生产环境必须修改：

1. **数据库密码** - 使用强密码
2. **JWT_SECRET** - 使用随机生成
3. **API Keys** - 使用环境变量，不要硬编码

生成随机密钥：
```bash
# JWT Secret
openssl rand -hex 32

# 数据库密码
openssl rand -base64 24
```