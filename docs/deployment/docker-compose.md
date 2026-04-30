# Docker Compose 部署

适合开发、测试和小规模生产环境。

## 快速部署

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env

# 2. 构建并启动
make build
make up

# 3. 查看状态
make status
```

## 服务列表

| 服务 | 端口 | 说明 |
|------|------|------|
| gateway | 80 | API 网关 |
| auth | 8001 | 认证服务 |
| knowledge | 8002 | 知识库服务 |
| embedding | 8003 | 向量化服务 |
| chat | 8004 | 对话服务 |
| ingest | 8005 | 文档处理服务 |
| web | - | 前端 UI |
| postgres | 5432 | PostgreSQL |
| redis | 6379 | Redis |
| milvus | 19530 | Milvus |
| minio | 9000 | MinIO |

## 常用命令

```bash
# 启动
make up

# 停止
make down

# 重启
make restart

# 查看日志
make logs SERVICE=chat

# 进入容器
docker-compose exec auth bash

# 重新构建
make build
```

## 数据持久化

Docker Compose 会创建以下卷：

- `knowledgebot_postgres` - PostgreSQL 数据
- `knowledgebot_redis` - Redis 数据
- `knowledgebot_milvus` - Milvus 数据
- `knowledgebot_minio` - MinIO 数据

## 备份

```bash
# 备份 PostgreSQL
docker-compose exec postgres pg_dump -U knowledgebot knowledgebot > backup.sql

# 备份 MinIO
docker-compose exec minio mc mirror local/knowledgebot ./backup/
```

## 更新

```bash
# 拉取最新代码
git pull

# 重新构建并启动
make build
make down
make up
```

## 监控（可选）

```bash
# 启动监控栈
make monitoring-up

# 访问
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

## 生产环境建议

1. **修改默认密码**
   ```bash
   POSTGRES_PASSWORD=strong-password
   REDIS_PASSWORD=strong-password
   MINIO_ROOT_PASSWORD=strong-password
   ```

2. **启用 HTTPS**
   - 配置反向代理（如 Nginx、Caddy）
   - 使用 Let's Encrypt 证书

3. **限制资源**
   ```yaml
   services:
     auth:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
   ```

4. **定期备份**
   ```bash
   # 添加到 crontab
   0 2 * * * /path/to/backup.sh
   ```

## 下一步

- [Kubernetes 部署](kubernetes/cluster-setup.md)
- [监控配置](../infrastructure/monitoring.md)