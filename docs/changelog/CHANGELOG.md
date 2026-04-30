# 变更日志

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 待发布功能

## [1.0.0] - 2025-01-XX

### 新增

#### 微服务架构
- Auth Service - 用户认证、租户管理、RBAC 权限
- Knowledge Service - 知识库、文档管理
- Embedding Service - 向量化、向量检索
- Chat Service - RAG 对话、历史管理
- Ingest Service - 文档处理、Celery 任务队列

#### 前端
- Vue 3 + Element Plus + TypeScript
- 知识库管理界面
- 文档上传进度追踪
- 实时流式对话
- 用户设置页面

#### 多模型支持
- OpenAI (GPT-4o-mini, GPT-4o)
- 通义千问 (Qwen-Max, Qwen-Plus)
- 智谱 AI (GLM-4, GLM-3-Turbo)
- SiliconFlow (多种开源模型)

#### Embedding 模型
- OpenAI text-embedding-3-small/large
- 通义千问 text-embedding-v2
- 本地模型支持

#### 文档处理
- PDF 解析（PyMuPDF）
- Word 文档（python-docx）
- Markdown 解析
- TXT/HTML 支持
- 智能分块策略

#### 向量检索
- Milvus 集成
- 混合检索（向量 + BM25）
- 重排序支持

#### 监控告警
- Prometheus 指标采集
- Grafana Dashboard
- Alertmanager 告警通知
- 邮件/Slack/Webhook 通知

#### CI/CD
- GitHub Actions 工作流
- 自动化测试
- Docker 镜像构建
- Blue-Green 部署
- 自动回滚

#### Kubernetes
- 完整 K8s 配置
- HPA 自动扩缩容
- Ingress 配置
- Secrets 管理

#### 其他
- 多租户隔离
- API 网关（Nginx）
- 完整 API 文档（Swagger）
- 单元测试覆盖

### 文档
- 完整 README
- 贡献指南
- API 参考
- 部署指南

---

## 版本说明

- **[Major]**: 不兼容的 API 更改
- **[Minor]**: 向后兼容的功能新增
- **[Patch]**: 向后兼容的问题修复

## 贡献

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md)。