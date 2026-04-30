# 贡献指南

感谢你对 KnowledgeBot 的关注！我们欢迎所有形式的贡献。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)

## 行为准则

请参阅 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/NblScript/KnowledgeBot/issues) 搜索是否已有相同问题
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（Python 版本、操作系统等）

### 提出新功能

1. 创建 Issue 描述功能需求
2. 等待维护者讨论和批准
3. 批准后开始实现

### 提交代码

见下方 [开发流程](#开发流程)。

## 开发流程

### 1. Fork 并克隆仓库

```bash
# Fork 后克隆你的仓库
git clone https://github.com/YOUR_USERNAME/KnowledgeBot.git
cd KnowledgeBot

# 添加上游仓库
git remote add upstream https://github.com/NblScript/KnowledgeBot.git
```

### 2. 创建分支

```bash
# 同步上游
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name
# 或修复分支
git checkout -b fix/your-bug-fix
```

### 3. 设置开发环境

```bash
# 安装 Python 依赖
pip install -r services/auth/requirements.txt
pip install -r services/knowledge/requirements.txt
pip install -r services/embedding/requirements.txt
pip install -r services/chat/requirements.txt
pip install -r services/ingest/requirements.txt

# 安装开发工具
pip install ruff black isort mypy pytest pytest-asyncio pytest-cov httpx

# 安装前端依赖（如需修改前端）
cd web && npm install
```

### 4. 进行开发

- 遵循 [代码规范](#代码规范)
- 添加必要的测试
- 更新相关文档

### 5. 运行测试

```bash
# 运行所有测试
make test

# 或运行单个服务测试
cd services/auth && pytest tests/ -v

# 运行代码检查
make ci-lint
```

### 6. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 7. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python 代码

- 使用 **Python 3.11+** 特性
- 遵循 **PEP 8** 规范
- 使用 **type hints**
- 函数和类添加 **docstrings**

```python
from typing import Optional


async def get_user(user_id: int) -> Optional[User]:
    """获取用户信息。
    
    Args:
        user_id: 用户 ID
        
    Returns:
        用户对象，不存在则返回 None
    """
    return await User.get_or_none(id=user_id)
```

### 格式化工具

```bash
# 代码格式化
black services/ libs/
isort services/ libs/

# Lint 检查
ruff check services/ libs/

# 类型检查
mypy services/
```

### 前端代码

- 使用 **TypeScript**
- 遵循 **Vue 3 Composition API** 风格
- 组件名使用 **PascalCase**
- 使用 **Element Plus** 组件库

```typescript
// 组件示例
<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <el-button @click="count++">{{ count }}</el-button>
</template>
```

### 目录结构

```
services/{service_name}/
├── app/
│   ├── api/v1/        # API 路由
│   ├── models/        # 数据模型
│   ├── schemas/       # Pydantic 模型
│   ├── services/      # 业务逻辑
│   ├── config.py      # 配置
│   └── main.py        # 入口
├── tests/
│   ├── test_api/
│   └── test_services/
├── Dockerfile
├── requirements.txt
└── README.md
```

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能）|
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |
| ci | CI/CD 相关 |

### 示例

```bash
# 新功能
git commit -m "feat(chat): 添加流式对话支持"

# Bug 修复
git commit -m "fix(auth): 修复 Token 过期验证错误"

# 文档更新
git commit -m "docs: 更新部署文档"

# 多行提交
git commit -m "feat(embedding): 添加多种 Embedding 模型支持

- 支持 OpenAI text-embedding-3
- 支持通义千问 embedding
- 添加模型切换配置

Closes #123"
```

## Pull Request 流程

### PR 标题

遵循提交规范：
```
feat: 添加新功能
fix: 修复某问题
```

### PR 描述模板

```markdown
## 更改类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 重构

## 更改说明
简要描述更改内容

## 相关 Issue
Closes #xxx

## 测试
- [ ] 已添加单元测试
- [ ] 已通过所有 CI 检查

## 截图（如适用）
```

### PR 检查清单

- [ ] 代码遵循项目规范
- [ ] 已添加/更新测试
- [ ] 已更新相关文档
- [ ] CI 检查通过
- [ ] 没有引入新的警告

### 审核流程

1. 自动 CI 检查通过
2. 至少 1 位维护者 Review
3. 处理 Review 意见
4. 维护者 Approve 后合并

## 发布流程

项目维护者负责：

1. 更新 `CHANGELOG.md`
2. 创建 Git Tag
3. 构建 Docker 镜像并推送
4. 发布 GitHub Release

## 获取帮助

- 提交 [Issue](https://github.com/NblScript/KnowledgeBot/issues)
- 加入讨论区（如有）

## 许可证

提交代码即表示你同意你的贡献将按照项目的 MIT 许可证进行授权。

---

再次感谢你的贡献！