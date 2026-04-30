# Auth Service

JWT 认证、用户管理、多租户支持的认证服务。

## 功能

- 用户注册/登录
- JWT Token 签发/验证
- 用户 CRUD 管理
- 多租户支持
- 角色/权限管理（RBAC）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## API 文档

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API 端点

### 认证

- `POST /v1/auth/register` - 用户注册
- `POST /v1/auth/login` - 用户登录
- `POST /v1/auth/refresh` - 刷新 Token
- `POST /v1/auth/logout` - 用户登出
- `POST /v1/auth/change-password` - 修改密码
- `GET /v1/auth/me` - 获取当前用户

### 用户管理

- `POST /v1/users` - 创建用户
- `GET /v1/users` - 用户列表
- `GET /v1/users/{user_id}` - 用户详情
- `PUT /v1/users/{user_id}` - 更新用户
- `DELETE /v1/users/{user_id}` - 删除用户

### 租户管理

- `POST /v1/tenants` - 创建租户
- `GET /v1/tenants` - 租户列表
- `GET /v1/tenants/{tenant_id}` - 租户详情
- `PUT /v1/tenants/{tenant_id}` - 更新租户
- `DELETE /v1/tenants/{tenant_id}` - 删除租户

### 角色管理

- `POST /v1/roles` - 创建角色
- `GET /v1/roles` - 角色列表
- `GET /v1/roles/{role_id}` - 角色详情
- `PUT /v1/roles/{role_id}` - 更新角色
- `DELETE /v1/roles/{role_id}` - 删除角色

## Token 配置

- Access Token: 1 小时有效期
- Refresh Token: 7 天有效期
- 算法: HS256

## 数据库

使用 PostgreSQL，schema: `auth`

### 表结构

- `tenants` - 租户表
- `users` - 用户表
- `roles` - 角色表
- `permissions` - 权限表
- `refresh_tokens` - 刷新令牌表