# API 参考

KnowledgeBot 提供 RESTful API 和 WebSocket 接口。

## 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `http://localhost/v1` |
| 认证方式 | Bearer Token (JWT) |
| 内容类型 | `application/json` |
| 字符编码 | UTF-8 |

## 认证

所有 API（登录/注册除外）需要携带 Authorization Header：

```
Authorization: Bearer <access_token>
```

Token 有效期：
- Access Token: 30 分钟
- Refresh Token: 7 天

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {"field": "email", "message": "邮箱格式不正确"}
    ]
  }
}
```

## 分页

列表接口支持分页：

```
GET /v1/knowledge-bases?page=1&page_size=20
```

响应：
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 错误码

| HTTP 状态码 | 错误码 | 说明 |
|------------|--------|------|
| 400 | VALIDATION_ERROR | 参数验证失败 |
| 401 | UNAUTHORIZED | 未认证或 Token 过期 |
| 403 | FORBIDDEN | 无权限访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | UNPROCESSABLE_ENTITY | 请求格式错误 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

## API 端点

### 认证 (Auth)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /v1/auth/register | 用户注册 |
| POST | /v1/auth/login | 用户登录 |
| POST | /v1/auth/refresh | 刷新 Token |
| POST | /v1/auth/logout | 登出 |

### 知识库 (Knowledge Base)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /v1/knowledge-bases | 获取知识库列表 |
| POST | /v1/knowledge-bases | 创建知识库 |
| GET | /v1/knowledge-bases/{id} | 获取知识库详情 |
| PUT | /v1/knowledge-bases/{id} | 更新知识库 |
| DELETE | /v1/knowledge-bases/{id} | 删除知识库 |

### 文档 (Document)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /v1/knowledge-bases/{kb_id}/documents | 获取文档列表 |
| POST | /v1/knowledge-bases/{kb_id}/documents | 上传文档 |
| GET | /v1/documents/{id} | 获取文档详情 |
| DELETE | /v1/documents/{id} | 删除文档 |

### 对话 (Chat)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /v1/chat/completions | 对话（非流式） |
| POST | /v1/stream/chat | 对话（流式 SSE） |
| GET | /v1/conversations | 获取会话列表 |
| GET | /v1/conversations/{id} | 获取会话历史 |

### 检索 (Retrieval)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /v1/embeddings/search | 向量检索 |
| POST | /v1/embeddings | 生成向量 |

## Swagger 文档

各服务提供 Swagger UI：

- Auth: http://localhost:8001/docs
- Knowledge: http://localhost:8002/docs
- Embedding: http://localhost:8003/docs
- Chat: http://localhost:8004/docs
- Ingest: http://localhost:8005/docs

## 下一步

- [认证 API](endpoints/auth.md)
- [知识库 API](endpoints/knowledge-bases.md)
- [对话 API](endpoints/chat.md)