# 术语表

本文档定义 KnowledgeBot 项目中使用的专业术语。

## A

### API Gateway (API 网关)
系统统一入口，负责请求路由、认证、限流等功能。

### ADR (Architecture Decision Record)
架构决策记录，用于记录和跟踪重要的架构决策。

### Async (异步)
不阻塞主线程执行的操作，常用于长时间任务处理。

## B

### BGE-M3
BAAI 开源的多语言嵌入模型，支持多粒度和多功能检索。

### Batch Processing (批处理)
将多个任务或数据项批量处理，提高效率。

## C

### Chat Service (对话服务)
处理用户对话请求，编排检索和 LLM 调用的核心服务。

### Chunk (文档切片)
将长文档分割成较小的文本片段，用于向量检索。

### Collection (集合)
Milvus 中存储向量的逻辑容器，类似于数据库中的表。

### Context Window (上下文窗口)
LLM 一次能处理的最大 token 数量。

## D

### Document Service (文档服务)
负责文档上传、解析、存储管理的服务。

### Docker
容器化平台，用于打包和运行应用程序。

## E

### Embedding (嵌入)
将文本转换为向量表示的过程。

### Embedding Service (嵌入服务)
负责文本向量化的微服务。

### E2E Testing (端到端测试)
测试完整用户流程的测试方法。

## F

### FastAPI
高性能 Python Web 框架，支持异步和自动 API 文档生成。

### Few-shot Learning (少样本学习)
通过少量示例让模型快速适应新任务的技术。

## G

### gRPC
高性能 RPC 框架，用于服务间通信。

## H

### Hallucination (幻觉)
LLM 生成不准确或虚构信息的现象。

### Hybrid Search (混合检索)
结合向量检索和关键词检索的方法。

## K

### Kafka
分布式消息队列，用于异步任务处理。

### Knowledge Base (知识库)
存储和管理企业知识的容器，支持文档上传和检索。

### Knowledge Base Service (知识库服务)
管理知识库 CRUD 操作的微服务。

## L

### LangChain
LLM 应用开发框架，提供模型调用、链式处理等功能。

### LLM (Large Language Model)
大型语言模型，如 GPT-4、Claude 等。

### LLM Service (大模型服务)
负责调用外部 LLM API 的微服务。

## M

### Microservices (微服务)
将应用拆分为小型、独立服务的架构模式。

### Milvus
开源向量数据库，用于向量存储和相似性搜索。

### MinIO
对象存储服务，用于文件存储。

### Multi-tenancy (多租户)
支持多个租户共享同一系统实例的架构模式。

## N

### NLP (Natural Language Processing)
自然语言处理，让计算机理解人类语言的技术。

## O

### OpenAPI
API 规范标准，用于描述 REST API 接口。

## P

### PostgreSQL
开源关系型数据库，存储结构化数据。

### Prompt Engineering (提示工程)
设计和优化 LLM 输入提示的技术。

## R

### RAG (Retrieval-Augmented Generation)
检索增强生成，结合检索和生成的问答技术。

### Rate Limiting (限流)
限制 API 请求频率的机制。

### Redis
内存数据库，用于缓存和会话存储。

### Retrieval Service (检索服务)
执行向量检索的微服务。

## S

### Semantic Search (语义搜索)
理解查询意图进行检索，而非仅关键词匹配。

### Streaming (流式输出)
逐步返回生成内容，而非等待完全生成后返回。

## T

### Tenant (租户)
多租户架构中的独立客户或组织实体。

### Token
LLM 处理的最小文本单元，也是认证凭证。

## U

### User Service (用户服务)
管理用户信息的微服务。

## V

### Vector (向量)
文本的数值化表示，用于相似性计算。

### Vector Database (向量数据库)
专门存储和检索向量的数据库，如 Milvus。

## W

### WebSocket
双向通信协议，用于实时数据传输。

## Z

### Zero-shot Learning (零样本学习)
模型在没有示例的情况下完成任务的能力。