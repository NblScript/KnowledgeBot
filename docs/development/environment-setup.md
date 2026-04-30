# 环境搭建

本文档介绍如何搭建 KnowledgeBot 开发环境。

## 系统要求

### 操作系统

| 系统 | 版本要求 |
|------|----------|
| Linux | Ubuntu 20.04+ / CentOS 8+ |
| macOS | 12.0 (Monterey)+ |
| Windows | WSL2 + Ubuntu 20.04 |

### 开发工具

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 主要开发语言 |
| Docker | 24.0+ | 容器化运行 |
| Docker Compose | 2.20+ | 容器编排 |
| Git | 2.30+ | 版本控制 |
| Node.js | 18+ | Web UI 开发（可选） |

## 安装步骤

### 1. 安装 Python

**Linux/macOS:**
```bash
# 使用 pyenv 安装
curl https://pyenv.run | bash
pyenv install 3.11.5
pyenv global 3.11.5

# 验证
python --version
```

**Windows (WSL2):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. 安装 Docker

**Linux:**
```bash
# Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 验证
docker --version
docker compose version
```

**macOS:**
```bash
# 安装 Docker Desktop
brew install --cask docker
```

### 3. 安装 Poetry（Python 包管理）

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 配置
poetry config virtualenvs.in-project true

# 验证
poetry --version
```

### 4. 克隆项目

```bash
# 使用 SSH
git clone git@github.com:org/knowledgebot.git

# 或使用 HTTPS
git clone https://github.com/org/knowledgebot.git

cd knowledgebot
```

### 5. 安装依赖

```bash
# 安装开发依赖
poetry install --with dev

# 激活虚拟环境
poetry shell

# 或手动激活
source .venv/bin/activate
```

### 6. 配置 IDE

**VS Code:**
```bash
# 安装推荐扩展
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
```

**PyCharm:**
1. 打开项目
2. 设置 Python 解释器为 Poetry 虚拟环境
3. 启用 Ruff 作为代码检查工具

### 7. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

**开发环境配置示例:**

```bash
# 应用配置
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=DEBUG

# 数据库
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=knowledgebot
POSTGRES_PASSWORD=knowledgebot_dev
POSTGRES_DB=knowledgebot

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=knowledgebot

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 8. 启动基础服务

```bash
# 启动数据库、Redis、Milvus 等基础服务
docker-compose up -d postgres redis milvus minio kafka

# 等待服务就绪
sleep 30

# 检查服务状态
docker-compose ps
```

### 9. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用脚本
python scripts/init_db.py
```

### 10. 启动开发服务器

```bash
# 启动 API Gateway
uvicorn services.api_gateway.src.main:app --reload --port 8000

# 启动其他服务（在不同终端）
uvicorn services.auth_service.src.main:app --reload --port 8001
uvicorn services.chat_service.src.main:app --reload --port 8002
```

## 项目结构

```
knowledgebot/
├── docs/                      # 文档
├── services/                  # 微服务
│   ├── api_gateway/
│   │   ├── src/
│   │   │   ├── api/           # API 路由
│   │   │   ├── core/          # 核心配置
│   │   │   ├── models/        # 数据模型
│   │   │   ├── services/      # 业务逻辑
│   │   │   └── main.py        # 入口文件
│   │   ├── tests/             # 测试
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── auth_service/
│   ├── chat_service/
│   └── ...
├── libs/                      # 共享库
│   ├── common/
│   │   ├── auth/              # 认证工具
│   │   ├── models/            # 公共模型
│   │   └── utils/             # 工具函数
│   └── database/
├── scripts/                   # 脚本
├── docker/                    # Docker 配置
├── k8s/                       # Kubernetes 配置
├── docker-compose.yml
├── mkdocs.yml                 # 文档配置
└── pyproject.toml             # 项目配置
```

## 开发工作流

### 1. 创建功能分支

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. 开发与测试

```bash
# 运行测试
pytest services/api_gateway/tests

# 运行 lint
ruff check .
ruff format .

# 类型检查
mypy services/
```

### 3. 提交代码

```bash
# 提交（使用 conventional commits）
git add .
git commit -m "feat: add user authentication"

# 推送
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 在 GitHub 创建 PR
2. 等待 CI 通过
3. 请求代码审查
4. 合并到 develop

## 常用命令

```bash
# 安装依赖
poetry install

# 更新依赖
poetry update

# 运行测试
pytest

# 运行测试（带覆盖率）
pytest --cov=services --cov-report=html

# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy services/

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f api-gateway

# 进入容器
docker-compose exec api-gateway bash

# 数据库迁移
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 调试配置

### VS Code launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "API Gateway",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "services.api_gateway.src.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["--no-header", "-v"],
      "justMyCode": false
    }
  ]
}
```

## 下一步

- [编码规范](coding-standards.md)
- [测试指南](testing-guide.md)
- [贡献指南](contributing.md)