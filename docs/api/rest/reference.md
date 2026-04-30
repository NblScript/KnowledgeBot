# API 参考文档

## 概述

KnowledgeBot 提供完整的 RESTful API 和 WebSocket 接口。

### 基础信息

| 项目 | 值 |
|------|-----|
| 基础 URL | `https://api.knowledgebot.io/v1` |
| 本地开发 | `http://localhost:8000/v1` |
| API 版本 | v1 |
| 协议 | HTTPS |
| 数据格式 | JSON |

### 认证方式

所有 API 请求需要在 Header 中携带 JWT Token：

```http
Authorization: Bearer <your_jwt_token>
```

获取 Token：

```bash
POST /v1/auth/token
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

响应：

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 通用响应格式

#### 成功响应

```json
{
  "data": { ... },
  "message": "Success"
}
```

#### 分页响应

```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

#### 错误响应

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无返回体） |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或 Token 过期） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 验证错误 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 错误码列表

| 错误码 | 说明 |
|--------|------|
| `VALIDATION_ERROR` | 参数验证失败 |
| `UNAUTHORIZED` | 未授权访问 |
| `FORBIDDEN` | 无权限访问 |
| `NOT_FOUND` | 资源不存在 |
| `CONFLICT` | 资源冲突 |
| `RATE_LIMIT_EXCEEDED` | 超出频率限制 |
| `INTERNAL_ERROR` | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 服务不可用 |

## API 端点概览

### 认证 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/v1/auth/token` | 获取访问令牌 |
| POST | `/v1/auth/refresh` | 刷新访问令牌 |
| POST | `/v1/auth/logout` | 注销登录 |
| POST | `/v1/auth/password/reset` | 重置密码 |

### 用户 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/v1/users/me` | 获取当前用户信息 |
| PUT | `/v1/users/me` | 更新当前用户信息 |
| GET | `/v1/users` | 获取用户列表（管理员） |

### 知识库 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/v1/knowledge-bases` | 获取知识库列表 |
| POST | `/v1/knowledge-bases` | 创建知识库 |
| GET | `/v1/knowledge-bases/{id}` | 获取知识库详情 |
| PUT | `/v1/knowledge-bases/{id}` | 更新知识库 |
| DELETE | `/v1/knowledge-bases/{id}` | 删除知识库 |

### 文档 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/v1/knowledge-bases/{kb_id}/documents` | 获取文档列表 |
| POST | `/v1/knowledge-bases/{kb_id}/documents` | 上传文档 |
| GET | `/v1/documents/{id}` | 获取文档详情 |
| DELETE | `/v1/documents/{id}` | 删除文档 |
| POST | `/v1/documents/{id}/process` | 触发文档处理 |

### 对话 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/v1/chat/completions` | 创建对话补全 |
| POST | `/v1/chat/completions/stream` | 流式对话补全 |
| GET | `/v1/chat/conversations` | 获取对话列表 |
| GET | `/v1/chat/conversations/{id}` | 获取对话详情 |
| DELETE | `/v1/chat/conversations/{id}` | 删除对话 |

### 检索 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/v1/retrieval/search` | 向量检索 |
| POST | `/v1/retrieval/hybrid` | 混合检索 |

## 快速示例

### Python

```python
import requests

# 认证
response = requests.post(
    "https://api.knowledgebot.io/v1/auth/token",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# 设置请求头
headers = {"Authorization": f"Bearer {token}"}

# 创建知识库
response = requests.post(
    "https://api.knowledgebot.io/v1/knowledge-bases",
    headers=headers,
    json={"name": "我的知识库", "description": "测试知识库"}
)
kb_id = response.json()["data"]["id"]

# 上传文档
with open("document.pdf", "rb") as f:
    requests.post(
        f"https://api.knowledgebot.io/v1/knowledge-bases/{kb_id}/documents",
        headers=headers,
        files={"file": f}
    )

# 对话
response = requests.post(
    "https://api.knowledgebot.io/v1/chat/completions",
    headers=headers,
    json={
        "knowledge_base_id": kb_id,
        "messages": [{"role": "user", "content": "请介绍一下这个文档"}]
    }
)
print(response.json())
```

### cURL

```bash
# 获取 Token
curl -X POST https://api.knowledgebot.io/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# 创建知识库
curl -X POST https://api.knowledgebot.io/v1/knowledge-bases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "我的知识库"}'

# 对话补全
curl -X POST https://api.knowledgebot.io/v1/chat/completions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_id": "<kb_id>",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 相关文档

- [认证 API 详情](endpoints/auth.md)
- [用户 API 详情](endpoints/users.md)
- [知识库 API 详情](endpoints/knowledge-bases.md)
- [文档 API 详情](endpoints/documents.md)
- [对话 API 详情](endpoints/chat.md)
- [检索 API 详情](endpoints/retrieval.md)
- [OpenAPI 规范文件](openapi.yaml)