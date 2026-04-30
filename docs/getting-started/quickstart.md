# 快速体验

5 分钟创建你的第一个知识库并开始对话。

## 前提条件

已完成 [安装指南](installation.md) 并启动服务。

## 步骤 1：注册账户

1. 访问 http://localhost
2. 点击「注册」
3. 填写邮箱和密码

## 步骤 2：创建知识库

1. 登录后进入「知识库」页面
2. 点击「新建知识库」
3. 填写名称，如：`产品文档`
4. 选择 Embedding 模型（推荐：`text-embedding-3-small`）

## 步骤 3：上传文档

1. 进入知识库详情
2. 点击「上传文档」
3. 选择文件（支持 PDF、Word、Markdown、TXT）
4. 等待处理完成（可在「任务列表」查看进度）

## 步骤 4：开始对话

1. 进入「对话」页面
2. 选择知识库
3. 输入问题，如：「这个产品的核心功能是什么？」
4. 查看基于知识库的回答

## API 使用

### 获取 Token

```bash
curl -X POST http://localhost/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your-password"}'
```

响应：
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### 创建知识库

```bash
TOKEN="your-access-token"

curl -X POST http://localhost/v1/knowledge-bases \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "技术文档", "description": "技术文档库"}'
```

### 上传文档

```bash
curl -X POST http://localhost/v1/knowledge-bases/{kb-id}/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

### 对话

```bash
curl -X POST http://localhost/v1/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_ids": ["kb-id"],
    "message": "总结这篇文档的核心内容"
  }'
```

## 下一步

- [API 参考](../api/rest/reference.md) - 完整 API 文档
- [配置说明](../deployment/envars.md) - 自定义配置