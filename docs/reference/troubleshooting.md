# 故障排查指南

本文档提供 KnowledgeBot 常见问题的诊断和解决方案。

## 服务健康检查

### 检查所有服务状态

```bash
# Docker Compose 部署
docker-compose ps

# Kubernetes 部署
kubectl get pods -n knowledgebot
```

### 检查服务日志

```bash
# 查看特定服务日志
docker-compose logs api-gateway
docker-compose logs chat-service

# 实时跟踪日志
docker-compose logs -f --tail=100 chat-service

# Kubernetes 环境
kubectl logs -f deployment/chat-service -n knowledgebot
```

### 健康检查端点

```bash
# API Gateway 健康检查
curl http://localhost:8000/health

# 各服务健康检查
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Chat Service
```

---

## 常见问题

### 1. 服务无法启动

#### 症状
```bash
docker-compose up -d
# 某些服务启动失败
```

#### 排查步骤

1. **检查端口占用**
   ```bash
   # 检查端口是否被占用
   lsof -i :8000
   lsof -i :5432
   lsof -i :19530
   
   # 或使用 netstat
   netstat -tlnp | grep 8000
   ```

2. **检查资源限制**
   ```bash
   # 检查 Docker 资源
   docker info | grep -i memory
   
   # 检查系统资源
   free -h
   df -h
   ```

3. **检查环境变量**
   ```bash
   # 验证 .env 文件
   cat .env | grep -v '^#' | grep -v '^$'
   
   # 检查必需变量是否设置
   docker-compose config
   ```

4. **查看详细错误日志**
   ```bash
   docker-compose logs --tail=200 api-gateway
   ```

#### 解决方案
- 释放占用的端口或修改配置中的端口
- 增加 Docker 资源限制
- 确保所有必需的环境变量已设置
- 检查配置文件语法错误

---

### 2. 数据库连接失败

#### 症状
```json
{
  "error": {
    "code": "DATABASE_CONNECTION_ERROR",
    "message": "Failed to connect to database"
  }
}
```

#### 排查步骤

1. **检查 PostgreSQL 状态**
   ```bash
   docker-compose ps postgres
   docker-compose logs postgres
   ```

2. **验证连接信息**
   ```bash
   # 进入容器测试连接
   docker-compose exec postgres psql -U knowledgebot -d knowledgebot
   
   # 从应用容器测试
   docker-compose exec api-gateway ping postgres
   ```

3. **检查网络连接**
   ```bash
   docker network ls
   docker network inspect knowledgebot_default
   ```

#### 解决方案
- 确保 PostgreSQL 服务已启动
- 验证连接字符串、用户名、密码
- 检查网络配置

---

### 3. 向量数据库 (Milvus) 问题

#### 症状
```json
{
  "error": {
    "code": "VECTOR_DB_ERROR",
    "message": "Failed to connect to Milvus"
  }
}
```

#### 排查步骤

1. **检查 Milvus 状态**
   ```bash
   docker-compose ps milvus
   docker-compose logs milvus
   ```

2. **验证 Milvus 连接**
   ```python
   from pymilvus import connections
   
   connections.connect(
       alias="default",
       host="localhost",
       port="19530"
   )
   print(connections.get_connection_addr("default"))
   ```

3. **检查 Collection 状态**
   ```python
   from pymilvus import utility
   
   print(utility.list_collections())
   ```

#### 解决方案
- 重启 Milvus 服务
- 检查 Milvus 配置
- 确保 Collection 已正确创建

---

### 4. API 认证失败

#### 症状
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

#### 排查步骤

1. **检查 Token 格式**
   ```bash
   # 正确格式
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   
   # 检查请求头
   curl -v http://localhost:8000/v1/users/me \
     -H "Authorization: Bearer $TOKEN"
   ```

2. **验证 Token 有效性**
   ```bash
   # 刷新 Token
   curl -X POST http://localhost:8000/v1/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "$REFRESH_TOKEN"}'
   ```

3. **检查 JWT 密钥配置**
   ```bash
   # 确保 JWT_SECRET_KEY 在所有服务中一致
   grep JWT_SECRET_KEY .env
   ```

#### 解决方案
- 确保正确传递 Bearer Token
- Token 过期时使用 Refresh Token 刷新
- 重新登录获取新 Token

---

### 5. 文档上传/处理失败

#### 症状
- 文档上传后状态一直为 `pending`
- 处理状态为 `failed`

#### 排查步骤

1. **检查文档处理服务**
   ```bash
   docker-compose logs document-service
   docker-compose logs embedding-service
   ```

2. **检查 MinIO 存储**
   ```bash
   # 检查 MinIO 状态
   docker-compose ps minio
   
   # 访问 MinIO 控制台
   open http://localhost:9000
   ```

3. **检查 Kafka 消息队列**
   ```bash
   docker-compose logs kafka
   
   # 检查 Topic
   docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

#### 解决方案
- 重启 Document Service 和 Embedding Service
- 检查文件格式是否支持
- 验证文件大小限制
- 检查存储空间

---

### 6. 对话响应慢或无响应

#### 症状
- 对话请求超时
- 响应时间过长

#### 排查步骤

1. **检查 LLM 服务**
   ```bash
   docker-compose logs llm-service
   ```

2. **检查 OpenAI API 连接**
   ```bash
   # 测试 OpenAI API
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **检查 Redis 缓存**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

4. **检查检索服务**
   ```bash
   docker-compose logs retrieval-service
   ```

#### 解决方案
- 检查 OpenAI API Key 是否有效
- 检查 API 配额限制
- 优化向量检索参数
- 增加缓存

---

### 7. 内存占用过高

#### 症状
- 服务 OOM (Out of Memory)
- 系统响应慢

#### 排查步骤

1. **检查容器资源使用**
   ```bash
   docker stats
   
   # Kubernetes
   kubectl top pods -n knowledgebot
   ```

2. **分析内存使用**
   ```python
   # Python 内存分析
   import tracemalloc
   tracemalloc.start()
   # ... 运行代码 ...
   snapshot = tracemalloc.take_snapshot()
   for stat in snapshot.statistics('lineno'):
       print(stat)
   ```

#### 解决方案
- 增加 Docker 内存限制
- 优化向量检索参数
- 减少批处理大小
- 启用模型量化

---

### 8. 网络连接问题

#### 症状
- 服务间无法通信
- 外部无法访问服务

#### 排查步骤

1. **检查 Docker 网络**
   ```bash
   docker network inspect knowledgebot_default
   ```

2. **检查防火墙规则**
   ```bash
   # Linux
   sudo iptables -L
   sudo ufw status
   
   # 检查端口开放
   telnet localhost 8000
   ```

3. **检查 DNS 解析**
   ```bash
   docker-compose exec api-gateway nslookup postgres
   ```

#### 解决方案
- 检查 Docker 网络配置
- 开放必要端口
- 检查防火墙规则

---

## 日志分析

### 日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 常规信息 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |
| CRITICAL | 严重错误 |

### 常用日志查询

```bash
# 查找错误日志
docker-compose logs | grep -i error

# 查找特定请求日志
docker-compose logs | grep "request_id"

# 按时间范围查询
docker-compose logs --since 1h | grep error

# Kubernetes 日志
kubectl logs deployment/chat-service -n knowledgebot --since=1h
```

---

## 性能调优

### 数据库优化

```sql
-- 检查慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- 添加索引
CREATE INDEX idx_documents_kb_id ON documents(knowledge_base_id);
```

### 向量检索优化

```python
# 调整检索参数
search_params = {
    "metric_type": "COSINE",
    "params": {
        "nprobe": 10,  # 减少搜索范围
    }
}

# 使用近似检索
search_params = {
    "metric_type": "COSINE",
    "params": {
        "nprobe": 5,
        "nlist": 128,  # 减少聚类数量
    }
}
```

---

## 获取帮助

如果以上方案无法解决问题：

1. **查看详细日志**: 收集相关服务的完整日志
2. **搜索 Issue**: 在 GitHub Issues 中搜索类似问题
3. **提交 Issue**: 提供详细的问题描述、日志和复现步骤

**提交 Issue 模板**:

```markdown
## 问题描述
[描述遇到的问题]

## 复现步骤
1. ...
2. ...

## 预期结果
[描述预期行为]

## 实际结果
[描述实际行为]

## 环境信息
- KnowledgeBot 版本:
- 部署方式: Docker Compose / Kubernetes
- 操作系统:
- 相关配置:

## 日志
```
[粘贴相关日志]
```
```