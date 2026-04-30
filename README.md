# KnowledgeBot - 企业级 RAG 知识库系统

[![CI/CD](https://github.com/NblScript/knowledgebot/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/NblScript/knowledgebot/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

基于微服务架构的 RAG（检索增强生成）知识库系统，支持多租户、多模型、分布式部署。

## 特性

- **微服务架构**: 6 个独立服务，可独立扩展
- **多 LLM 支持**: OpenAI、通义千问、智谱 AI、SiliconFlow
- **多 Embedding 支持**: 可切换不同向量模型
- **向量检索**: 基于 Milvus 的高性能向量检索
- **文档处理**: 支持 PDF、Word、Markdown、TXT、HTML
- **流式响应**: 支持 SSE 流式对话
- **多租户**: 支持租户隔离和 RBAC 权限
- **监控告警**: Prometheus + Grafana + Alertmanager
- **CI/CD**: GitHub Actions 自动化测试和部署

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (Nginx)                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
    ┌─────────────┬───────────┼───────────┬─────────────┐
    │             │           │           │             │
    ▼             ▼           ▼           ▼             ▼
┌───────┐   ┌─────────┐  ┌───────┐  ┌───────┐   ┌───────┐
│ Auth  │   │Knowledge│  │Embed- │  │ Chat  │   │Ingest │
│:8001  │   │  :8002  │  │ding   │  │ :8004 │   │ :8005 │
│       │   │         │  │ :8003 │  │       │   │       │
└───┬───┘   └────┬────┘  └───┬───┘  └───┬───┘   └───┬───┘
    │            │           │          │           │
    └────────────┴───────────┴──────────┴───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │PostgreSQL│   │  Milvus  │   │  MinIO   │
        │  Redis   │   │          │   │          │
        └──────────┘   └──────────┘   └──────────┘
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- 8GB+ 内存
- 20GB+ 磁盘空间

### 启动服务

```bash
# 克隆项目
git clone https://github.com/NblScript/knowledgebot.git
cd knowledgebot

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写 API Key

# 构建并启动
make build
make up

# 访问
open http://localhost
```

### 启动监控（可选）

```bash
make monitoring-up

# 访问
open http://localhost:3000  # Grafana (admin/admin123)
open http://localhost:9090  # Prometheus
```

## 服务列表

| 服务 | 端口 | 功能 |
|------|------|------|
| Gateway | 80 | API 网关、路由 |
| Auth | 8001 | 认证、用户、租户 |
| Knowledge | 8002 | 知识库、文档管理 |
| Embedding | 8003 | 向量化、向量检索 |
| Chat | 8004 | 对话、RAG |
| Ingest | 8005 | 文档处理、Celery |
| Web | - | Vue 3 前端 |

## API 文档

启动后访问各服务的 Swagger 文档：

- Auth: http://localhost:8001/docs
- Knowledge: http://localhost:8002/docs
- Embedding: http://localhost:8003/docs
- Chat: http://localhost:8004/docs
- Ingest: http://localhost:8005/docs

### 主要 API 端点

```
# 认证
POST /v1/auth/register     # 注册
POST /v1/auth/login        # 登录
POST /v1/auth/refresh      # 刷新 Token

# 知识库
GET    /v1/knowledge-bases          # 列表
POST   /v1/knowledge-bases          # 创建
POST   /v1/knowledge-bases/{id}/documents  # 上传文档

# 对话
POST /v1/chat/completions   # 对话（RAG）
POST /v1/stream/chat        # 流式对话

# 向量检索
POST /v1/embeddings/search  # 向量检索
```

## 开发指南

### 本地开发

```bash
# 安装依赖
cd services/auth && pip install -r requirements.txt

# 运行服务
make dev-auth

# 运行测试
make test
```

### 代码规范

```bash
# Lint
make ci-lint

# 格式化
black services/ libs/
isort services/ libs/
```

## 部署

### Docker Compose（开发/测试）

```bash
make build
make up
```

### Kubernetes（生产）

```bash
# 配置 kubectl
export KUBECONFIG=/path/to/kubeconfig

# 部署
./scripts/k8s-deploy.sh deploy

# 查看状态
./scripts/k8s-deploy.sh status

# 扩容
./scripts/k8s-deploy.sh scale chat 5
```

### CI/CD

项目使用 GitHub Actions 自动化 CI/CD：

1. **代码检查**: Lint、格式检查
2. **单元测试**: 各服务独立测试
3. **集成测试**: 服务间集成测试
4. **构建镜像**: 推送到 GHCR
5. **部署 Staging**: develop 分支自动部署
6. **部署 Production**: main 分支自动部署（Blue-Green）

## 监控告警

### Prometheus 指标

- `http_requests_total`: 请求总数
- `http_request_duration_seconds`: 请求延迟
- `documents_processed_total`: 处理文档数
- `conversations_active_total`: 活跃对话数

### Grafana Dashboard

- 服务概览
- 请求速率
- 错误率
- 响应时间
- 资源使用

### 告警规则

- Pod 不可用
- CPU/内存过高
- 错误率过高
- 响应时间过长
- PostgreSQL 连接数过多
- Redis 内存过高

## 配置

### LLM 提供商

```bash
# OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-xxx

# 通义千问
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxx

# 智谱 AI
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=xxx

# SiliconFlow
LLM_PROVIDER=siliconflow
SILICONFLOW_API_KEY=xxx
```

### Embedding 提供商

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

## 目录结构

```
knowledgebot/
├── services/           # 微服务
│   ├── auth/          # 认证服务
│   ├── knowledge/     # 知识库服务
│   ├── embedding/     # 向量化服务
│   ├── chat/          # 对话服务
│   └── ingest/        # 文档处理服务
├── web/               # Vue 3 前端
├── libs/              # 共享库
│   └── common/        # 通用工具
├── k8s/               # Kubernetes 配置
│   ├── infrastructure.yaml
│   ├── services.yaml
│   ├── hpa.yaml
│   └── monitoring/
├── docker/            # Docker 配置
├── tests/             # 测试
│   ├── integration/   # 集成测试
│   └── performance/   # 性能测试
├── scripts/           # 工具脚本
├── docs/              # 文档
├── docker-compose.yml
├── docker-compose.monitoring.yml
├── Makefile
└── .github/
    └── workflows/
        └── ci-cd.yml
```

## 常见问题

### 1. Milvus 启动失败

确保有足够的内存，建议至少 8GB。

### 2. 文档上传失败

检查 MinIO 配置和文件大小限制（默认 50MB）。

### 3. 对话无响应

检查 LLM API Key 配置，查看 Chat 服务日志。

## 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)。

## License

MIT License