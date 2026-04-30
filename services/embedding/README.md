# Embedding Service

向量嵌入服务，支持 OpenAI/Qwen/SiliconFlow API。

## 功能

- 批量文本向量化
- 向量检索 (Milvus)
- 集合管理

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /v1/embeddings/texts | 批量文本向量化 |
| POST | /v1/embeddings/search | 向量检索 |
| POST | /v1/embeddings/collections | 创建集合 |
| GET | /v1/embeddings/collections/{id} | 获取集合信息 |
| DELETE | /v1/embeddings/collections/{id} | 删除集合 |
| GET | /v1/embeddings/health | 健康检查 |

## 配置

环境变量:

- `EMBEDDING_PROVIDER`: 提供商 (openai/siliconflow/qwen/mock)
- `EMBEDDING_MODEL`: 模型名称
- `EMBEDDING_DIM`: 向量维度
- `MILVUS_HOST`: Milvus 主机
- `MILVUS_PORT`: Milvus 端口
- `OPENAI_API_KEY`: OpenAI API Key
- `SILICONFLOW_API_KEY`: SiliconFlow API Key
- `QWEN_API_KEY`: 通义千问 API Key

## 运行

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

## Docker

```bash
docker build -t embedding-service .
docker run -p 8003:8003 embedding-service
```