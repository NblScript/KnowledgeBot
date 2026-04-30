# 部署指南 - Docker Compose

本指南介绍如何使用 Docker Compose 部署 KnowledgeBot。

## 前置要求

- Docker 24.0+
- Docker Compose 2.20+
- 至少 8GB 内存
- 至少 50GB 磁盘空间

## 快速部署

### 1. 获取项目

```bash
git clone https://github.com/org/knowledgebot.git
cd knowledgebot
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

**必需配置：**

```bash
# LLM 配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxx

# 安全配置（生产环境必须修改）
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
MINIO_ROOT_PASSWORD=your_minio_password
JWT_SECRET_KEY=your_jwt_secret_key

# 其他配置使用默认值即可
```

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

## 服务架构

```mermaid
graph TB
    subgraph "Docker Network"
        Gateway[API Gateway<br/>:8000]
        Auth[Auth Service<br/>:8001]
        Chat[Chat Service<br/>:8002]
        KB[Knowledge Base<br/>:8003]
        Doc[Document Service<br/>:8004]
        Embed[Embedding Service<br/>:8005]
        Retr[Retrieval Service<br/>:8006]
        LLM[LLM Service<br/>:8007]
        User[User Service<br/>:8008]
        
        Postgres[(PostgreSQL<br/>:5432)]
        Redis[(Redis<br/>:6379)]
        Milvus[(Milvus<br/>:19530)]
        Minio[(MinIO<br/>:9000)]
        Kafka{{Kafka<br/>:9092}}
    end
    
    Gateway --> Auth
    Gateway --> Chat
    Gateway --> KB
    Gateway --> Doc
    Gateway --> User
    
    Auth --> Postgres
    Auth --> Redis
    Chat --> Retr
    Chat --> LLM
    Doc --> Minio
    Doc --> Kafka
    Embed --> Kafka
    Embed --> Milvus
    Retr --> Milvus
    Retr --> Redis
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_ENV` | 运行环境 | `production` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `POSTGRES_HOST` | PostgreSQL 主机 | `postgres` |
| `POSTGRES_PORT` | PostgreSQL 端口 | `5432` |
| `POSTGRES_USER` | 数据库用户名 | `knowledgebot` |
| `POSTGRES_PASSWORD` | 数据库密码 | - |
| `POSTGRES_DB` | 数据库名 | `knowledgebot` |
| `REDIS_HOST` | Redis 主机 | `redis` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `MILVUS_HOST` | Milvus 主机 | `milvus` |
| `MILVUS_PORT` | Milvus 端口 | `19530` |
| `MINIO_ENDPOINT` | MinIO 端点 | `minio:9000` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka 地址 | `kafka:9092` |
| `LLM_PROVIDER` | LLM 提供商 | `openai` |
| `OPENAI_API_KEY` | OpenAI API Key | - |

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| API Gateway | 8000 | 统一入口 |
| Web UI | 3000 | 前端界面 |
| MinIO Console | 9001 | MinIO 管理界面 |
| Kafka UI | 8080 | Kafka 管理界面（可选） |

## 运维操作

### 启动/停止服务

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启特定服务
docker-compose restart api-gateway

# 查看日志
docker-compose logs -f api-gateway
```

### 数据备份

```bash
# 备份 PostgreSQL
docker-compose exec postgres pg_dump -U knowledgebot > backup_$(date +%Y%m%d).sql

# 备份 MinIO
mc mirror local/knowledgebot ./backup/minio/

# 备份 Milvus
# 使用 Milvus backup 工具
```

### 数据恢复

```bash
# 恢复 PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U knowledgebot

# 恢复 MinIO
mc mirror ./backup/minio/ local/knowledgebot
```

### 更新服务

```bash
# 拉取最新镜像
docker-compose pull

# 重新部署
docker-compose up -d
```

### 扩容服务

```bash
# 扩展 Chat Service 到 3 个实例
docker-compose up -d --scale chat-service=3

# 需要配置负载均衡
```

## 生产环境建议

### 安全加固

1. **修改所有默认密码**
2. **启用 HTTPS**
   ```yaml
   # 添加 Nginx 反向代理
   nginx:
     image: nginx:alpine
     ports:
       - "443:443"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
       - ./certs:/etc/nginx/certs
   ```
3. **配置防火墙规则**
4. **启用 JWT 密钥轮换**

### 性能优化

1. **增加资源限制**
   ```yaml
   services:
     chat-service:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

2. **调整 JVM 参数（Milvus）**
3. **优化 PostgreSQL 配置**
4. **启用 Redis 持久化**

### 高可用配置

1. **数据库主从复制**
2. **Redis Sentinel**
3. **Milvus 集群模式**
4. **服务多副本部署**

## 故障排查

### 服务无法启动

```bash
# 检查端口占用
lsof -i :8000

# 检查日志
docker-compose logs api-gateway

# 检查资源
docker stats
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose exec postgres pg_isready

# 测试连接
docker-compose exec api-gateway python -c "
import psycopg2
conn = psycopg2.connect('postgresql://knowledgebot:password@postgres:5432/knowledgebot')
print('Connected!')
"
```

### 向量检索失败

```bash
# 检查 Milvus 状态
docker-compose exec milvus curl http://localhost:9091/healthz

# 检查 Collection
docker-compose exec embedding-service python -c "
from pymilvus import connections, utility
connections.connect('default', host='milvus', port='19530')
print(utility.list_collections())
"
```

## 下一步

- [Kubernetes 部署](kubernetes/cluster-setup.md)
- [运维手册](operations/runbook.md)
- [监控配置](infrastructure/monitoring.md)