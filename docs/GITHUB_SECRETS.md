# GitHub Secrets 配置指南

CI/CD 流水线需要配置以下 Secrets。

## 配置方法

1. 进入仓库 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 输入 Name 和 Value
4. 点击 **Add secret**

---

## 必需 Secrets

### LLM API Keys

| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `OPENAI_API_KEY` | OpenAI API Key | `sk-proj-xxx` |
| `QWEN_API_KEY` | 通义千问 API Key | `sk-xxx` |
| `ZHIPU_API_KEY` | 智谱 AI API Key | `xxx.xxx` |
| `SILICONFLOW_API_KEY` | SiliconFlow API Key | `sk-xxx` |

### 容器镜像

| Secret Name | 说明 |
|-------------|------|
| `GITHUB_TOKEN` | GitHub 自动提供，用于推送镜像到 GHCR |

---

## Kubernetes 部署 Secrets

### Staging 环境

| Secret Name | 说明 |
|-------------|------|
| `KUBE_CONFIG_STAGING` | Staging 集群的 kubeconfig（base64 编码） |

获取方法：
```bash
cat ~/.kube/config | base64 -w 0
```

### Production 环境

| Secret Name | 说明 |
|-------------|------|
| `KUBE_CONFIG_PRODUCTION` | Production 集群的 kubeconfig（base64 编码） |

---

## 可选 Secrets

### 通知集成

| Secret Name | 说明 |
|-------------|------|
| `SLACK_WEBHOOK_URL` | Slack 通知 Webhook |
| `DISCORD_WEBHOOK_URL` | Discord 通知 Webhook |

### 监控告警

| Secret Name | 说明 |
|-------------|------|
| `SMTP_PASSWORD` | SMTP 邮件密码 |
| `PAGERDUTY_ROUTING_KEY` | PagerDuty 集成密钥 |

---

## Secrets 模板

复制以下内容到 GitHub Secrets：

```yaml
# LLM API Keys
OPENAI_API_KEY: sk-proj-your-openai-key
QWEN_API_KEY: sk-your-qwen-key
ZHIPU_API_KEY: your-zhipu-key
SILICONFLOW_API_KEY: sk-your-siliconflow-key

# Kubernetes
KUBE_CONFIG_STAGING: LS0tLS1CRUdJTi... (base64 encoded)
KUBE_CONFIG_PRODUCTION: LS0tLS1CRUdJTi... (base64 encoded)

# 可选
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/xxx
```

---

## 环境变量（Variables）

除了 Secrets，还可以配置 **Variables**（非敏感信息）：

| Variable Name | 说明 | 默认值 |
|---------------|------|--------|
| `STAGING_HOST` | Staging 环境地址 | `staging.knowledgebot.example.com` |
| `PRODUCTION_HOST` | Production 环境地址 | `knowledgebot.example.com` |
| `DOCKER_REGISTRY` | Docker 镜像仓库 | `ghcr.io` |

---

## 安全注意事项

1. **定期轮换** API Keys
2. 不要在代码中硬编码 Secrets
3. 使用最小权限原则配置 kubeconfig
4. Production 和 Staging 使用不同的凭证
5. 启用仓库的 Secret scanning

---

## 验证配置

配置完成后，可以手动触发 CI/CD：

```bash
gh workflow run ci-cd.yml -f environment=staging
```

或在 GitHub Actions 页面点击 **Run workflow**。