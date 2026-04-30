# KnowledgeBot 文档系统

本目录包含 KnowledgeBot 项目的完整文档系统。

## 文档结构

```
docs/
├── architecture/        # 架构设计文档
│   ├── adr/            # 架构决策记录
│   └── diagrams/       # 架构图资源
├── services/           # 各服务详细文档
├── api/                # API 参考文档
│   ├── rest/          # REST API
│   ├── grpc/          # gRPC 接口
│   └── websocket/     # WebSocket 接口
├── development/        # 开发指南
├── deployment/         # 部署运维文档
├── testing/            # 测试文档
├── changelog/          # 变更日志
├── reference/          # 参考资料
└── assets/             # 静态资源
```

## 本地开发

### 安装 MkDocs

```bash
pip install mkdocs-material
pip install mkdocs-git-revision-date-localized-plugin
pip install mkdocs-redirects
pip install mkdocs-mermaid2-plugin
pip install mkdocs-awesome-pages-plugin
```

### 启动本地服务器

```bash
mkdocs serve
```

访问 http://localhost:8000 查看文档。

### 构建静态站点

```bash
mkdocs build
```

生成的文件位于 `site/` 目录。

## 文档写作规范

### Markdown 格式

- 使用标准 Markdown 语法
- 代码块指定语言以便高亮
- 表格使用对齐格式

### 文件命名

- 使用小写字母和连字符
- 避免特殊字符
- 示例: `api-reference.md`, `getting-started.md`

### 标题层级

```
# 一级标题 (页面标题，仅一个)
## 二级标题 (主要章节)
### 三级标题 (子章节)
#### 四级标题 (细节)
```

### 提示块类型

```markdown
!!! note "提示"
    普通提示信息

!!! tip "技巧"
    使用技巧

!!! warning "警告"
    重要警告

!!! danger "危险"
    危险操作警告

!!! example "示例"
    代码或使用示例
```

## 文档更新流程

1. 创建或修改文档
2. 本地预览确认效果
3. 提交 PR 进行审核
4. 合并后自动部署

## 相关链接

- [MkDocs 文档](https://www.mkdocs.org/)
- [Material 主题文档](https://squidfunk.github.io/mkdocs-material/)
- [编写好的文档](https://www.writethedocs.org/guide/)
