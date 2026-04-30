# 安装指南

本指南帮助你在本地或服务器上安装 KnowledgeBot。

## 系统要求

### 最低配置

| 资源 | 要求 |
|------|------|
| CPU | 4 核 |
| 内存 | 8 GB |
| 磁盘 | 20 GB |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

### 推荐配置（生产环境）

| 资源 | 要求 |
|------|------|
| CPU | 8 核 |
| 内存 | 16 GB |
| 磁盘 | 100 GB SSD |

## 安装步骤

### 1. 安装 Docker

**Ubuntu/Debian:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**macOS:**
```bash
brew install --cask docker
```

### 2. 克隆项目

```bash
git clone https://github.com/NblScript/KnowledgeBot.git
cd KnowledgeBot
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```bash
# 必需：选择一个 LLM 提供商
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here

# 可选：配置其他模型
# LLM_PROVIDER=qwen
# QWEN_API_KEY=sk-your-key

# 可选：修改数据库密码
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
```

### 4. 启动服务

```bash
# 构建镜像
make build

# 启动所有服务
make up

# 查看服务状态
make status
```

### 5. 验证安装

```bash
# 健康检查
make health

# 预期输出：
# Auth:      OK
# Knowledge: OK
# Embedding: OK
# Chat:      OK
# Ingest:    OK
```

访问 Web UI：http://localhost

## 常见问题

### Docker 权限错误

```bash
sudo usermod -aG docker $USER
# 退出并重新登录
```

### 端口被占用

修改 `.env` 中的端口配置：

```bash
GATEWAY_PORT=8080
AUTH_PORT=8001
```

### 内存不足

Milvus 至少需要 4GB 内存。如果启动失败：

```bash
# 增加 Docker 内存限制（Docker Desktop）
# Settings > Resources > Memory > 8GB
```

## 下一步

- [快速体验](quickstart.md) - 5 分钟创建你的第一个知识库
- [配置说明](../deployment/envars.md) - 详细环境变量说明