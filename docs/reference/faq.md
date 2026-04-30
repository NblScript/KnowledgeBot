# 常见问题

## 安装相关

### Docker 启动失败？

检查 Docker 是否正常运行：
```bash
docker info
```

确保有足够内存（建议 8GB+）。

### Milvus 启动很慢？

Milvus 需要下载镜像，首次启动可能需要 5-10 分钟。

### 端口冲突怎么办？

修改 `.env` 文件中的端口：
```bash
GATEWAY_PORT=8080
AUTH_PORT=9001
KNOWLEDGE_PORT=9002
```

## 使用相关

### 文档上传失败？

常见原因：
1. 文件格式不支持
2. 文件过大（默认限制 50MB）
3. API Key 未配置

解决方法：
```bash
# 查看错误详情
make logs SERVICE=ingest
```

### 对话没有回答？

检查：
1. 知识库是否有文档
2. LLM API Key 是否正确
3. 文档是否处理完成

### 回答不准确？

可能原因：
1. Embedding 模型不适合文档类型
2. 分块策略不合适
3. 文档内容不相关

优化建议：
- 尝试不同的 Embedding 模型
- 调整分块大小
- 上传更多相关文档

## API 相关

### Token 过期？

刷新 Token：
```bash
curl -X POST http://localhost/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### 401 Unauthorized？

确保：
1. Token 正确
2. Token 未过期
3. Header 格式正确：`Authorization: Bearer <token>`

### 429 Rate Limit？

请求频率过快，等待后重试。

## 性能相关

### 检索慢？

优化建议：
1. 减少 `top_k` 数值
2. 使用更快的 Embedding 模型
3. 优化 Milvus 配置

### 内存占用高？

Milvus 和 LLM 模型占用较大内存。

解决方法：
1. 限制容器内存
2. 使用更小的模型
3. 清理无用数据

## 其他

### 如何备份数据？

```bash
# PostgreSQL
docker-compose exec postgres pg_dump -U knowledgebot knowledgebot > backup.sql

# MinIO（文档）
docker-compose exec minio mc mirror local/knowledgebot ./backup/
```

### 如何切换语言模型？

编辑 `.env`：
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your-key
LLM_MODEL=qwen-max
```

重启服务：
```bash
make restart
```

---

更多问题？提交 [GitHub Issue](https://github.com/NblScript/KnowledgeBot/issues)。