# KnowledgeBot

**企业级 RAG 知识库问答系统**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-24.0+-blue.svg)](https://www.docker.com/)

## 项目简介

KnowledgeBot 是一个高性能、可扩展的企业级 RAG（检索增强生成）知识库问答系统，支持多租户、多知识库、多模型接入。

### 核心特性

- **多模型支持** - OpenAI、Azure OpenAI、本地模型等多种 LLM 后端
- **高性能检索** - 基于 Milvus 的向量检索，支持混合搜索
- **文档智能解析** - 自动解析 PDF、Word、Markdown 等格式
- **多租户架构** - 完整的租户隔离与权限控制
- **流式输出** - WebSocket 支持，实时响应
- **API 优先** - 完整的 REST API 与 OpenAPI 规范

### 技术栈

| 组件 | 技术选型 |
|------|----------|
| Web 框架 | FastAPI |
| LLM 框架 | LangChain |
| 嵌入模型 | BGE-M3 |
| 向量数据库 | Milvus |
| 关系数据库 | PostgreSQL |
| 对象存储 | MinIO |
| 缓存 | Redis |
| 消息队列 | Kafka |

## 快速开始

### 环境要求

- Docker 24.0+
- Docker Compose 2.20+

### 一键启动

```bash
# 克隆项目
git clone https://github.com/org/knowledgebot.git
cd knowledgebot

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 启动服务
docker-compose up -d

# 访问服务
open http://localhost:8000/docs
```

详细安装指南请查看 [部署文档](docs/deployment/docker-compose.md)。

## 项目结构

```
knowledgebot/
├── docs/                    # 项目文档
├── services/               # 微服务源码
│   ├── api-gateway/       # API 网关
│   ├── auth-service/      # 认证服务
│   ├── chat-service/      # 对话服务
│   └── ...                # 其他服务
├── libs/                   # 共享库
├── scripts/                # 工具脚本
├── docker/                 # Docker 配置
└── k8s/                    # Kubernetes 配置
```

## 文档

- [快速开始](docs/getting-started/index.md)
- [架构设计](docs/architecture/overview.md)
- [API 参考](docs/api/rest/reference.md)
- [开发指南](docs/development/environment-setup.md)
- [部署运维](docs/deployment/docker-compose.md)

## 开发

### 本地开发

```bash
# 安装依赖
poetry install

# 启动开发服务器
uvicorn services.api_gateway.src.main:app --reload

# 运行测试
pytest
```

### 贡献指南

欢迎贡献代码！请查看 [贡献指南](docs/development/contributing.md)。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- GitHub Issues: https://github.com/org/knowledgebot/issues
- Email: support@knowledgebot.io