# 架构决策记录 (ADR)

## 概述

架构决策记录（Architecture Decision Records, ADR）是记录架构决策的轻量级文档。
每个 ADR 描述一个架构决策及其背景和后果。

## ADR 列表

| 编号 | 标题 | 状态 | 日期 |
|------|------|------|------|
| [ADR-001](ADR-001-microservices-decision.md) | 采用微服务架构 | 已接受 | 2026-04-30 |
| [ADR-002](ADR-002-vector-database-choice.md) | 选择 Milvus 作为向量数据库 | 已接受 | 2026-04-30 |
| [ADR-003](ADR-003-embedding-model-selection.md) | 选择 BGE-M3 嵌入模型 | 已接受 | 2026-04-30 |
| [ADR-004](ADR-004-message-queue-choice.md) | 选择 Kafka 消息队列 | 已接受 | 2026-04-30 |
| [ADR-005](ADR-005-caching-strategy.md) | Redis 缓存策略 | 已接受 | 2026-04-30 |

## ADR 模板

创建新 ADR 时，请使用以下模板：

```markdown
# ADR-{编号}: {决策标题}

## 状态

[提议 | 已接受 | 已废弃 | 已替代]

## 背景

描述导致此决策的背景和问题陈述。需要回答：
- 我们面临什么问题？
- 有什么约束条件？
- 谁受影响？

## 决策

描述做出的决策及其理由。需要回答：
- 我们选择什么方案？
- 为什么选择这个方案？

## 后果

描述此决策的结果。需要回答：
- 正面影响是什么？
- 负面影响是什么？
- 有什么风险？

## 替代方案

列出考虑过的替代方案及选择此方案的原因：

### 方案 A: {方案名称}
- 优点：
- 缺点：
- 不选择的原因：

### 方案 B: {方案名称}
- 优点：
- 缺点：
- 不选择的原因：

## 参考

- [相关文档链接]()
- [技术资料链接]()
```

## 如何创建新的 ADR

1. 复制模板文件 `_template.md`
2. 命名为 `ADR-{编号}-{短标题}.md`
3. 填写各部分内容
4. 提交 PR 进行评审
5. 评审通过后更新本文档列表

## 更多资源

- [ADR GitHub 仓库](https://github.com/npryce/adr-tools)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)