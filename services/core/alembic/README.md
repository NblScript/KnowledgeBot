# Alembic 数据库迁移

## 使用方法

### 运行迁移

```bash
# 进入项目目录
cd /home/qingking/projects/knowledgebot/services/core

# 激活虚拟环境
source venv/bin/activate

# 运行所有迁移
alembic upgrade head

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 创建新迁移

```bash
# 自动生成迁移 (基于模型变化)
alembic revision --autogenerate -m "描述信息"

# 创建空迁移文件
alembic revision -m "描述信息"
```

### 回滚迁移

```bash
# 回滚到上一版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>

# 回滚所有
alembic downgrade base
```

## 配置说明

- 数据库连接从 `app.config.settings` 获取
- 支持异步 PostgreSQL (asyncpg)
- 迁移文件位于 `versions/` 目录

## 注意事项

1. 确保 PostgreSQL 服务正在运行
2. 确保 `.env` 文件中的数据库配置正确
3. 修改模型后，运行 `alembic revision --autogenerate` 生成迁移
4. 检查生成的迁移文件后再执行 `alembic upgrade head`