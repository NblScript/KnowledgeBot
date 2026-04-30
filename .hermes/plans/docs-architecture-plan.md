# KnowledgeBot 文档系统架构规划方案

> 版本: v1.0  
> 日期: 2026-04-30  
> 作者: 系统架构师

---

## 一、概述

### 1.1 设计目标

为 KnowledgeBot 企业级 RAG 知识库问答系统设计一套完整的文档系统架构，实现：

- **清晰化**: 参考 OpenAI 文档风格，结构清晰、层次分明
- **版本化**: 文档与代码同步演进，支持版本追溯
- **可搜索**: 全文检索，快速定位信息
- **自动化**: API 文档自动生成，减少维护成本
- **协作友好**: 支持团队协作编辑和审核

### 1.2 项目背景回顾

KnowledgeBot 采用 9 个微服务架构：
- API Gateway (网关服务)
- Auth Service (认证服务)
- User Service (用户服务)
- Knowledge Base Service (知识库服务)
- Document Service (文档处理服务)
- Embedding Service (向量嵌入服务)
- Retrieval Service (检索服务)
- LLM Service (大模型服务)
- Chat Service (对话服务)

技术栈：FastAPI + LangChain + BGE-M3 + Milvus + PostgreSQL + MinIO + Redis + Kafka

---

## 二、文档目录结构设计

### 2.1 项目根目录 docs/ 结构

```
knowledgebot/
├── docs/                          # 文档根目录
│   ├── README.md                  # 文档导航首页
│   ├── index.md                   # MkDocs 首页
│   │
│   ├── architecture/              # 架构设计文档
│   │   ├── overview.md            # 系统架构概览
│   │   ├── microservices.md       # 微服务架构详解
│   │   ├── data-flow.md           # 数据流向设计
│   │   ├── adr/                   # 架构决策记录 (ADR)
│   │   │   ├── ADR-001-microservices-decision.md
│   │   │   ├── ADR-002-vector-database-choice.md
│   │   │   ├── ADR-003-embedding-model-selection.md
│   │   │   ├── ADR-004-message-queue-choice.md
│   │   │   ├── ADR-005-caching-strategy.md
│   │   │   └── README.md          # ADR 索引
│   │   └── diagrams/              # 架构图资源
│   │       ├── system-overview.drawio
│   │       ├── service-mesh.drawio
│   │       └── data-pipeline.drawio
│   │
│   ├── services/                  # 各服务文档
│   │   ├── api-gateway/
│   │   │   ├── README.md          # 服务概述
│   │   │   ├── design.md          # 详细设计
│   │   │   └── config.md          # 配置说明
│   │   ├── auth-service/
│   │   ├── user-service/
│   │   ├── knowledge-base-service/
│   │   ├── document-service/
│   │   ├── embedding-service/
│   │   ├── retrieval-service/
│   │   ├── llm-service/
│   │   └── chat-service/
│   │
│   ├── api/                       # API 文档
│   │   ├── rest/                  # REST API 规范
│   │   │   ├── openapi.yaml       # OpenAPI 3.0 规范文件
│   │   │   ├── endpoints/         # 各服务端点文档
│   │   │   │   ├── auth.md
│   │   │   │   ├── users.md
│   │   │   │   ├── knowledge-bases.md
│   │   │   │   ├── documents.md
│   │   │   │   ├── chat.md
│   │   │   │   └── retrieval.md
│   │   │   └── reference.md       # API 调用参考
│   │   ├── grpc/                  # gRPC 文档
│   │   │   ├── protocol-buffers.md
│   │   │   └── service-contracts/
│   │   └── websocket/             # WebSocket 接口
│   │       └── streaming-api.md
│   │
│   ├── development/               # 开发指南
│   │   ├── getting-started.md     # 快速开始
│   │   ├── environment-setup.md   # 环境搭建
│   │   ├── coding-standards.md    # 编码规范
│   │   ├── git-workflow.md        # Git 工作流
│   │   ├── testing-guide.md       # 测试指南
│   │   ├── debugging.md           # 调试指南
│   │   └── contributing.md        # 贡献指南
│   │
│   ├── deployment/                # 部署运维
│   │   ├── docker-compose.md      # Docker Compose 部署
│   │   ├── kubernetes/            # K8s 部署文档
│   │   │   ├── cluster-setup.md
│   │   │   ├── helm-charts.md
│   │   │   └── scaling.md
│   │   ├── infrastructure/        # 基础设施
│   │   │   ├── networking.md
│   │   │   ├── storage.md
│   │   │   ├── monitoring.md
│   │   │   └── logging.md
│   │   ├── operations/            # 运维手册
│   │   │   ├── runbook.md         # 故障处理手册
│   │   │   ├── backup-restore.md  # 备份恢复
│   │   │   ├── security.md        # 安全运维
│   │   │   └── maintenance.md     # 维护流程
│   │   └── envars.md              # 环境变量说明
│   │
│   ├── testing/                   # 测试文档
│   │   ├── strategy.md            # 测试策略
│   │   ├── unit-testing.md       # 单元测试
│   │   ├── integration-testing.md # 集成测试
│   │   ├── e2e-testing.md         # 端到端测试
│   │   ├── performance-testing.md # 性能测试
│   │   └── test-data/             # 测试数据
│   │       └── fixtures.md
│   │
│   ├── changelog/                 # 变更日志
│   │   ├── CHANGELOG.md           # 主变更日志
│   │   └── releases/              # 版本发布说明
│   │       ├── v0.1.0.md
│   │       └── v0.2.0.md
│   │
│   ├── reference/                 # 参考资料
│   │   ├── glossary.md            # 术语表
│   │   ├── faq.md                 # 常见问题
│   │   ├── troubleshooting.md    # 故障排查
│   │   └── external-resources.md  # 外部资源
│   │
│   └── assets/                    # 静态资源
│       ├── images/
│       ├── diagrams/
│       └── videos/
│
├── services/                      # 各服务源码目录(各服务内含 docs/)
│   ├── api-gateway/
│   │   ├── docs/
│   │   │   ├── README.md
│   │   │   ├── architecture.md
│   │   │   └── troubleshooting.md
│   │   └── src/
│   └── ...
│
└── .hermes/
    └── plans/                     # 规划文档
```

### 2.2 微服务内部文档结构模板

每个微服务目录内部，包含独立的文档结构：

```
services/{service-name}/
├── docs/
│   ├── README.md              # 服务概述
│   │   - 功能简介
│   │   - 核心接口
│   │   - 快速开始
│   │
│   ├── architecture.md        # 服务架构
│   │   - 内部模块设计
│   │   - 数据模型
│   │   - 状态管理
│   │
│   ├── api.md                 # 服务 API 详细说明
│   │   - REST 接口
│   │   - 内部调用接口
│   │
│   ├── config.md              # 配置说明
│   │   - 环境变量
│   │   - 配置文件
│   │   - 敏感信息管理
│   │
│   ├── dependencies.md        # 依赖说明
│   │   - 外部服务依赖
│   │   - 第三方库依赖
│   │
│   └── troubleshooting.md     # 问题排查
│
├── src/
│   └── {service-name}/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── services/
│       └── tests/
│
└── Dockerfile
```

---

## 三、文档类型定义

### 3.1 架构决策记录 (ADR)

采用 Michael Nygard 推荐的 ADR 格式：

```markdown
# ADR-{编号}: {决策标题}

## 状态
[提议 | 已接受 | 已废弃 | 已替代]

## 背景
描述导致此决策的背景和问题陈述

## 决策
描述做出的决策及其理由

## 后果
- 正面影响：
- 负面影响：
- 风险：

## 替代方案
列出考虑过的替代方案及选择此方案的原因

## 参考
- 相关文档链接
- 技术资料链接
```

**已规划 ADR 列表：**

| 编号 | 标题 | 优先级 |
|------|------|--------|
| ADR-001 | 微服务架构决策 | P0 |
| ADR-002 | Milvus 向量数据库选型 | P0 |
| ADR-003 | BGE-M3 嵌入模型选择 | P0 |
| ADR-004 | Kafka 消息队列选型 | P0 |
| ADR-005 | Redis 缓存策略 | P1 |
| ADR-006 | MinIO 对象存储选型 | P1 |
| ADR-007 | PostgreSQL 关系数据存储 | P0 |
| ADR-008 | FastAPI 框架选择 | P0 |
| ADR-009 | LangChain 框架集成 | P0 |
| ADR-010 | JWT 认证方案 | P1 |

### 3.2 API 规范文档

#### OpenAPI 3.0 规范

```yaml
openapi: 3.0.3
info:
  title: KnowledgeBot API
  version: 1.0.0
  description: 企业级 RAG 知识库问答系统 API
  
servers:
  - url: https://api.knowledgebot.io/v1
    description: 生产环境
  - url: http://localhost:8000/v1
    description: 本地开发

paths:
  /v1/chat/completions:
    post:
      summary: 创建对话补全
      tags:
        - Chat
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: 成功响应
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

#### API 文档模板

```markdown
# {API 名称}

## 概述
简要描述 API 功能

## 端点

### `POST /v1/{resource}`

创建资源

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| name | string | 是 | 资源名称 |

**请求示例**

```json
{
  "name": "example"
}
```

**响应示例**

```json
{
  "id": "xxx",
  "name": "example",
  "created_at": "2026-01-01T00:00:00Z"
}
```

**错误码**

| 错误码 | 描述 |
|--------|------|
| 400 | 参数错误 |
| 401 | 未授权 |
| 500 | 服务器错误 |
```

### 3.3 开发指南

#### 快速开始文档模板

```markdown
# 快速开始

## 环境要求

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (前端)

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/org/knowledgebot.git
cd knowledgebot
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 3. 启动开发环境

```bash
docker-compose up -d
```

### 4. 验证安装

```bash
curl http://localhost:8000/health
```

## 下一步

- 阅读 [架构概览](architecture/overview.md)
- 查看 [API 文档](api/rest/reference.md)
```

### 3.4 部署运维手册

#### 运维手册模板

```markdown
# 运维手册

## 服务管理

### 启动服务

```bash
docker-compose up -d
# 或
kubectl apply -f k8s/
```

### 停止服务

```bash
docker-compose down
```

### 健康检查

| 服务 | 端点 | 预期响应 |
|------|------|----------|
| API Gateway | /health | 200 OK |
| Milvus | /healthz | 200 OK |

## 故障排查流程

### 服务无法启动

1. 检查日志: `docker-compose logs {service}`
2. 检查端口占用
3. 检查环境变量配置

### 常见问题

[详细故障排查指南](../reference/troubleshooting.md)
```

### 3.5 测试文档

```markdown
# 测试策略

## 测试分层

```
┌─────────────────────────────────┐
│         E2E Tests               │  10%
├─────────────────────────────────┤
│      Integration Tests          │  30%
├─────────────────────────────────┤
│        Unit Tests               │  60%
└─────────────────────────────────┘
```

## 覆盖率目标

- 单元测试: > 80%
- 集成测试: > 60%
- E2E 测试: 核心流程 100%

## 执行命令

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```
```

---

## 四、版本管理策略

### 4.1 文档版本控制

#### Git 分支策略

```
main          # 生产版本文档
  └── develop # 开发版本文档
       └── feature/xxx  # 功能开发文档
```

#### 文档更新流程

```
┌──────────────────┐
│  代码变更        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  同步文档更新     │
│  - API 变更      │
│  - 架构变更      │
│  - 配置变更      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PR Review       │
│  - 代码审核      │
│  - 文档审核      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  合并到主分支     │
│  - 触发文档构建   │
└──────────────────┘
```

### 4.2 变更日志格式

遵循 [Keep a Changelog](https://keepachangelog.com/) 规范：

```markdown
# Changelog

All notable changes to KnowledgeBot will be documented in this file.

## [Unreleased]

### Added
- 新增 XXX 功能

### Changed
- 优化 XXX 性能

### Deprecated
- 弃用 XXX 接口

### Removed
- 移除 XXX 功能

### Fixed
- 修复 XXX 问题

### Security
- 修复 XXX 安全漏洞

## [1.0.0] - 2026-04-30

### Added
- 初始版本发布
```

### 4.3 版本发布说明模板

```markdown
# Release v{version}

## 🎉 新功能

- 功能 1
- 功能 2

## 🐛 Bug 修复

- 修复问题 1
- 修复问题 2

## 📝 文档更新

- 更新 API 文档
- 新增部署指南

## ⚠️ 破坏性变更

- 变更 1 及迁移指南

## 🔗 相关链接

- 完整变更日志: CHANGELOG.md
- 升级指南: docs/deployment/upgrade-guide.md
```

---

## 五、文档工具链

### 5.1 推荐方案：MkDocs + Material

**选择理由：**
- Markdown 原生支持，学习成本低
- Material 主题美观、响应式
- 搜索功能内置，支持中文
- 插件丰富，易于扩展
- GitHub Pages 部署简单

### 5.2 工具配置

#### MkDocs 配置文件

```yaml
# mkdocs.yml
site_name: KnowledgeBot Documentation
site_url: https://docs.knowledgebot.io
site_description: 企业级 RAG 知识库问答系统文档

theme:
  name: material
  language: zh
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 切换到深色模式
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: 切换到浅色模式
  features:
    - navigation.instant      # 即时加载
    - navigation.tracking     # 锚点追踪
    - navigation.tabs         # 顶部导航
    - navigation.sections     # 分段导航
    - navigation.expand       # 展开导航
    - search.suggest          # 搜索建议
    - search.highlight        # 搜索高亮
    - content.code.copy       # 代码复制

plugins:
  - search:
      lang:
        - zh
        - en
  - git-revision-date-localized:
      enable_creation_date: true
  - redirects:
      redirect_maps:
        'old-page.md': 'new-page.md'
  - mermaid2:                  # 流程图支持
  - awesome-pages:             # 页面排序

markdown_extensions:
  - admonition                 # 提示块
  - codehilite:
      guess_lang: false
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences:      # 嵌套代码块
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_tab: true
  - pymdownx.tasklist:
      checkbox: true
  - toc:
      permalink: true
      toc_depth: 3
  - footnotes
  - meta
  - attr_list

nav:
  - 首页: index.md
  - 快速开始:
      - 概述: getting-started/index.md
      - 安装: getting-started/installation.md
      - 快速体验: getting-started/quickstart.md
  - 架构:
      - 系统概述: architecture/overview.md
      - 微服务架构: architecture/microservices.md
      - 数据流: architecture/data-flow.md
      - 架构决策: architecture/adr/README.md
  - API 参考:
      - 概述: api/rest/reference.md
      - 认证: api/rest/endpoints/auth.md
      - 用户: api/rest/endpoints/users.md
      - 知识库: api/rest/endpoints/knowledge-bases.md
      - 文档: api/rest/endpoints/documents.md
      - 对话: api/rest/endpoints/chat.md
  - 开发指南:
      - 环境搭建: development/environment-setup.md
      - 编码规范: development/coding-standards.md
      - 测试指南: development/testing-guide.md
      - Git 工作流: development/git-workflow.md
  - 部署运维:
      - Docker 部署: deployment/docker-compose.md
      - Kubernetes: deployment/kubernetes/cluster-setup.md
      - 运维手册: deployment/operations/runbook.md
  - 参考资源:
      - 术语表: reference/glossary.md
      - FAQ: reference/faq.md
      - 故障排查: reference/troubleshooting.md
  - 变更日志: changelog/CHANGELOG.md

extra:
  version:
    provider: mike
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/org/knowledgebot
  analytics:
    provider: google
    property: G-XXXXXXXXXX

extra_css:
  - stylesheets/extra.css

extra_javascript:
  - javascripts/extra.js
```

### 5.3 API 文档自动生成方案

#### 方案：FastAPI + ReDoc + MkDocs 集成

```
┌─────────────────────────────────────────────────────┐
│                  代码层                              │
│  ┌─────────────────────────────────────────────┐   │
│  │  FastAPI 路由 + Docstring + Type Hints      │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  生成层                              │
│  ┌───────────────┐    ┌───────────────┐            │
│  │ OpenAPI JSON  │───▶│ ReDoc HTML    │            │
│  │ (自动生成)     │    │ (静态页面)    │            │
│  └───────────────┘    └───────────────┘            │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  发布层                              │
│  ┌─────────────────────────────────────────────┐   │
│  │  MkDocs + API 文档嵌入                       │   │
│  │  /api/redoc/ → ReDoc 界面                   │   │
│  │  /api/openapi.yaml → 规范文件下载           │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### FastAPI 集成示例

```python
# services/api-gateway/src/api/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="KnowledgeBot API",
    description="企业级 RAG 知识库问答系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="KnowledgeBot API",
        version="1.0.0",
        description="""
## 认证方式

所有 API 请求需要在 Header 中携带 JWT Token：

```
Authorization: Bearer <token>
```

## 错误处理

所有错误响应遵循统一格式：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### 自动生成 OpenAPI 文件

```bash
# 构建时自动导出 OpenAPI 规范
python -c "
from src.main import app
import json
with open('docs/api/rest/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
"
```

### 5.4 文档搜索方案

**MkDocs Material 内置搜索 + 增强配置**

支持特性：
- 全文检索
- 中文分词支持
- 搜索建议
- 结果高亮
- 键盘快捷键 (按 `/` 聚焦搜索)

**可选增强：Algolia DocSearch**

如果需要更强大的搜索能力：
- 支持同义词
- 搜索结果分类
- 搜索分析

```yaml
# mkdocs.yml 增强配置
extra:
  analytics:
    provider: google
  # Algolia 搜索（需要申请）
  search:
    provider: algolia
    algolia:
      api_key: YOUR_API_KEY
      index_name: knowledgebot
```

---

## 六、文档发布流程

### 6.1 CI/CD 集成

```yaml
# .github/workflows/docs.yml
name: Build and Deploy Docs

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 获取完整历史，用于 git-revision-date
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install mkdocs-git-revision-date-localized-plugin
          pip install mkdocs-redirects
          pip install mkdocs-mermaid2-plugin
          pip install mkdocs-awesome-pages-plugin
      
      - name: Build API docs
        run: |
          # 从 FastAPI 生成 OpenAPI 规范
          python scripts/generate_openapi.py
      
      - name: Build MkDocs
        run: mkdocs build --strict
      
      - name: Upload artifacts
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'site'
  
  deploy:
    needs: build
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    
    permissions:
      pages: write
      id-token: write
    
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 6.2 版本化文档

使用 `mike` 实现多版本文档：

```bash
# 安装 mike
pip install mike

# 发布特定版本
mike deploy v1.0.0 latest --push
mike deploy v0.9.0 --push

# 设置默认版本
mike set-default latest --push
```

用户可以通过界面切换版本：
```
https://docs.knowledgebot.io/        # 重定向到 latest
https://docs.knowledgebot.io/v1.0.0/ # 特定版本
https://docs.knowledgebot.io/v0.9.0/ # 历史版本
```

---

## 七、文档写作规范

### 7.1 Markdown 基础规范

```markdown
# 一级标题 (页面标题，仅一个)

## 二级标题 (主要章节)

### 三级标题 (子章节)

#### 四级标题 (细节内容)

**强调文本**

*斜体文本*

`行内代码`

[链接文本](url)

![图片替代文本](image.png)

> 引用文本

- 无序列表项 1
- 无序列表项 2

1. 有序列表 1
2. 有序列表 2

| 表头 | 内容 |
|------|------|
| 数据 | 值 |
```

### 7.2 代码块规范

```markdown
```python
# 语言标识必须，便于语法高亮
def example():
    pass
```

```json
{
  "key": "value"
}
```

```bash
# Shell 命令
ls -la
```

```yaml
# 配置文件
key: value
```
```

### 7.3 文档注释页眉模板

```markdown
---
title: 文档标题
description: 简短描述，用于 SEO
author: 作者
date: 2026-04-30
version: 1.0
tags:
  - tag1
  - tag2
status: draft | review | published | deprecated
---
```

---

## 八、项目管理清单

### 8.1 文档创建优先级

| 优先级 | 文档类型 | 文档名称 | 预计工时 |
|--------|----------|----------|----------|
| P0 | 架构 | 系统架构概览 | 4h |
| P0 | 架构 | 微服务架构详解 | 6h |
| P0 | 开发 | 快速开始指南 | 2h |
| P0 | 开发 | 环境搭建指南 | 4h |
| P0 | API | OpenAPI 规范文件 | 8h |
| P0 | 架构 | ADR-001 ~ ADR-003 | 4h |
| P1 | 开发 | 编码规范 | 3h |
| P1 | 开发 | 测试指南 | 4h |
| P1 | 部署 | Docker Compose 部署 | 3h |
| P1 | 参考资源 | 术语表 | 2h |
| P2 | 部署 | Kubernetes 部署 | 6h |
| P2 | 部署 | 运维手册 | 8h |
| P2 | 参考资源 | 故障排查指南 | 4h |
| P2 | 参考资源 | FAQ | 3h |

### 8.2 文档维护检查清单

- [ ] 代码变更时同步更新 API 文档
- [ ] 新增功能时添加使用说明
- [ ] 版本发布时更新 CHANGELOG
- [ ] 季度文档审核与清理
- [ ] 定期检查文档链接有效性
- [ ] 收集用户反馈持续改进

---

## 九、附录

### 9.1 参考 OpenAI 文档设计特点

1. **结构清晰**: 左侧导航，右侧目录，中间内容
2. **版本管理**: 不同版本可切换
3. **交互设计**: 代码可复制，在线 Playground
4. **搜索强大**: 全文搜索 + API 搜索
5. **示例丰富**: 每个接口多种语言示例

### 9.2 推荐阅读

- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Diátaxis - Documentation Framework](https://diataxis.fr/)
- [Keep a Changelog](https://keepachangelog.com/)

---

*文档规划方案完成，请按照优先级逐步实施。*
