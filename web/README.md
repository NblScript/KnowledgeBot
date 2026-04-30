# KnowledgeBot Web UI

基于 Vue 3 + Vite + TypeScript + Element Plus 的智能知识库助手前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **TypeScript** - 类型安全的 JavaScript 超集
- **Element Plus** - 基于 Vue 3 的组件库
- **Pinia** - Vue 状态管理库
- **Vue Router** - Vue.js 官方路由
- **Axios** - HTTP 客户端

## 功能特性

### 页面
- **登录/注册页面** - 用户认证
- **知识库列表页面** - CRUD 操作
- **文档管理页面** - 文档上传与管理
- **对话页面** - RAG 智能问答
- **用户设置页面** - 个人信息与密码管理

### 组件
- **NavBar** - 导航栏组件
- **FileUpload** - 文件上传组件
- **ChatMessage** - 聊天消息组件

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
web/
├── src/
│   ├── api/              # API 接口
│   │   ├── auth.ts       # 认证 API
│   │   ├── chat.ts       # 聊天 API
│   │   ├── client.ts     # Axios 客户端
│   │   └── knowledge.ts  # 知识库 API
│   ├── components/       # 公共组件
│   │   ├── ChatMessage.vue
│   │   ├── FileUpload.vue
│   │   └── NavBar.vue
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # Pinia 状态管理
│   │   ├── auth.ts       # 认证状态
│   │   └── knowledge.ts  # 知识库状态
│   ├── views/            # 页面视图
│   │   ├── Chat.vue
│   │   ├── Documents.vue
│   │   ├── KnowledgeBases.vue
│   │   ├── Layout.vue
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   └── Settings.vue
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── vite-env.d.ts     # 类型声明
├── public/               # 静态资源
├── index.html            # HTML 入口
├── package.json          # 项目配置
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
├── Dockerfile            # Docker 构建文件
└── nginx.conf            # Nginx 配置
```

## API 端点

通过 Gateway 代理到后端服务：

- `POST /v1/auth/login` - 用户登录
- `POST /v1/auth/register` - 用户注册
- `GET /v1/knowledge-bases` - 获取知识库列表
- `POST /v1/knowledge-bases` - 创建知识库
- `GET /v1/knowledge-bases/{id}/documents` - 获取文档列表
- `POST /v1/knowledge-bases/{id}/documents` - 上传文档
- `POST /v1/chat/completions` - 发送聊天消息

## Docker 部署

```bash
# 构建镜像
docker build -t knowledgebot-web .

# 运行容器
docker run -d -p 80:80 knowledgebot-web
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | API 基础 URL | /v1 |

## 开发说明

### 代码规范

- 使用 TypeScript 严格模式
- 组件使用 Composition API + `<script setup>`
- 样式使用 scoped CSS

### 构建优化建议

当前构建产物较大，可以通过以下方式优化：

1. 按需引入 Element Plus 组件
2. 使用 `manualChunks` 分割代码
3. 启用 Gzip/Brotli 压缩

## License

MIT
