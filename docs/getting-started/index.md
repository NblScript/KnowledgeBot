# 快速开始

欢迎使用 KnowledgeBot！本指南将帮助您在 10 分钟内完成系统安装并运行第一个知识库问答。

## 环境要求

### 必需组件

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Docker | 24.0+ | 容器运行环境 |
| Docker Compose | 2.20+ | 容器编排工具 |
| Git | 2.30+ | 版本控制 |

### 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 磁盘 | 50 GB | 100 GB SSD |

### 外部服务（使用 API 模式）

| 服务 | 说明 |
|------|------|
| OpenAI API | 或 Azure OpenAI API |
| API Key | 用于 LLM 调用 |

!!! tip "提示"
    本指南采用 API 模式调用外部 AI 服务，无需本地部署模型。

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/org/knowledgebot.git
cd knowledgebot
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**必需配置项：**

```bash
# LLM 配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 数据库配置（使用默认值即可）
POSTGRES_USER=knowledgebot
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=knowledgebot

# Redis 配置
REDIS_PASSWORD=your_redis_password

# MinIO 配置
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your_minio_password

# JWT 密钥
JWT_SECRET_KEY=your_jwt_secret_key
```

### 3. 启动服务

```bash
# 启动所有服务（首次启动会拉取镜像，需要几分钟）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 验证安装

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "services": {
    "api_gateway": "healthy",
    "auth": "healthy",
    "chat": "healthy",
    "knowledge_base": "healthy",
    "document": "healthy",
    "embedding": "healthy",
    "retrieval": "healthy",
    "llm": "healthy",
    "user": "healthy"
  }
}
```

### 5. 访问 Web UI

打开浏览器访问：

- Web UI: http://localhost:3000
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 快速体验

### 使用 API

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo@123456",
    "name": "Demo User"
  }'

# 2. 登录获取 Token
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo@123456"
  }'

# 保存返回的 access_token
TOKEN="<your_access_token>"

# 3. 创建知识库
curl -X POST http://localhost:8000/v1/knowledge-bases \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个知识库",
    "description": "这是一个演示知识库"
  }'

# 保存返回的知识库 ID
KB_ID="<knowledge_base_id>"

# 4. 上传文档
curl -X POST "http://localhost:8000/v1/knowledge-bases/$KB_ID/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf"

# 5. 等待文档处理完成（通常几秒到几分钟）
curl "http://localhost:8000/v1/knowledge-bases/$KB_ID/documents" \
  -H "Authorization: Bearer $TOKEN"

# 6. 开始对话
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_id": "'$KB_ID'",
    "messages": [
      {"role": "user", "content": "请总结这个文档的主要内容"}
    ]
  }'
```

### 使用 Python SDK

```python
# 安装 SDK
pip install knowledgebot-sdk

# 使用示例
from knowledgebot import KnowledgeBot

# 初始化客户端
client = KnowledgeBot(
    base_url="http://localhost:8000",
    email="demo@example.com",
    password="Demo@123456"
)

# 创建知识库
kb = client.knowledge_bases.create(
    name="我的知识库",
    description="演示知识库"
)

# 上传文档
with open("document.pdf", "rb") as f:
    doc = client.documents.upload(kb.id, f)

# 等待处理完成
client.documents.wait_for_completion(doc.id)

# 对话
response = client.chat.completions.create(
    knowledge_base_id=kb.id,
    messages=[{"role": "user", "content": "这个文档讲了什么？"}]
)
print(response.content)
```

## 常见问题

### 服务启动失败

**问题**: Docker 容器启动失败

**解决方案**:
```bash
# 检查端口占用
lsof -i :8000

# 检查 Docker 日志
docker-compose logs api-gateway

# 重启服务
docker-compose down
docker-compose up -d
```

### API 调用返回 401

**问题**: 认证失败

**解决方案**:
- 检查 Token 是否正确传递
- 检查 Token 是否过期
- 确认请求头格式: `Authorization: Bearer <token>`

### 文档上传后无法检索

**问题**: 文档处理失败或未完成

**解决方案**:
```bash
# 检查文档状态
curl "http://localhost:8000/v1/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN"

# 查看处理日志
docker-compose logs embedding-service
```

## 下一步

- 📖 了解 [系统架构](../architecture/overview.md)
- 🔧 查看 [完整 API 文档](../api/rest/reference.md)
- 🚀 学习 [部署指南](../deployment/docker-compose.md)
- 💡 阅读 [开发指南](../development/environment-setup.md)