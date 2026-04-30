# 常见问题 (FAQ)

## 一般问题

### KnowledgeBot 是什么？

KnowledgeBot 是一个企业级 RAG（检索增强生成）知识库问答系统，支持多租户、多知识库、多模型接入。用户可以上传文档创建知识库，然后通过对话方式查询知识库内容。

### KnowledgeBot 支持哪些文档格式？

目前支持以下格式：
- PDF (.pdf)
- Microsoft Word (.doc, .docx)
- Markdown (.md)
- 纯文本 (.txt)
- HTML (.html, .htm)

### KnowledgeBot 支持哪些 LLM？

目前支持：
- OpenAI (GPT-4, GPT-3.5-turbo)
- Azure OpenAI
- 其他兼容 OpenAI API 的模型

### KnowledgeBot 是开源的吗？

是的，KnowledgeBot 采用 MIT 许可证开源。

---

## 部署相关

### 最小硬件配置是多少？

**开发环境：**
- CPU: 4 核
- 内存: 8 GB
- 磁盘: 50 GB

**生产环境：**
- CPU: 8 核
- 内存: 16 GB+
- 磁盘: 100 GB SSD

### 可以在 Kubernetes 上部署吗？

是的，KnowledgeBot 提供完整的 Kubernetes 部署配置，包括 Helm Charts。

### 支持本地部署 LLM 吗？

当前版本主要通过 API 调用外部 LLM 服务。未来版本将支持本地模型部署。

---

## 功能相关

### 如何创建知识库？

```bash
# API 方式
curl -X POST https://api.knowledgebot.io/v1/knowledge-bases \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "我的知识库", "description": "描述信息"}'

# 或通过 Web UI 创建
```

### 文档上传后多久可以使用？

文档上传后会自动进行解析和向量化处理，通常几秒到几分钟不等，取决于文档大小和系统负载。

### 支持多语言吗？

是的，BGE-M3 嵌入模型支持多语言，包括中文、英文、日文等。

### 如何保护数据安全？

- 租户数据隔离
- JWT 认证
- HTTPS 加密传输
- 敏感信息加密存储
- 完整的审计日志

---

## 开发相关

### 如何贡献代码？

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

详见 [贡献指南](../development/contributing.md)。

### 使用什么编程语言？

主要使用 Python 3.11+，框架为 FastAPI。

### 如何调试服务？

```bash
# 启动开发服务器（带热重载）
uvicorn services.api_gateway.src.main:app --reload

# 查看日志
docker-compose logs -f api-gateway
```

### 如何运行测试？

```bash
# 运行所有测试
pytest

# 运行特定服务测试
pytest services/chat_service/tests

# 带覆盖率报告
pytest --cov=services --cov-report=html
```

---

## 性能相关

### 如何提高检索速度？

1. 调整 Milvus 索引参数
2. 使用缓存减少重复查询
3. 优化 chunk 大小
4. 使用混合检索

### 支持多少并发用户？

取决于部署配置和硬件资源，单实例可支持数百并发。可通过水平扩展增加容量。

### 如何监控系统性能？

使用 Prometheus + Grafana 监控系统，预置了常用监控面板。

---

## 价格与许可

### 商业使用需要付费吗？

MIT 许可证允许免费商业使用。

### 有商业支持吗？

有，提供企业版和技术支持服务。请联系 support@knowledgebot.io。

---

## 其他问题

### 如何获取帮助？

- **文档**: https://docs.knowledgebot.io
- **GitHub Issues**: https://github.com/org/knowledgebot/issues
- **邮件**: support@knowledgebot.io

### 如何报告 Bug？

在 GitHub Issues 中提交 Bug 报告，请包含：
- 问题描述
- 复现步骤
- 环境信息
- 相关日志

### 有社区吗？

有，欢迎加入：
- GitHub Discussions
- Discord 社区（建设中）