#!/bin/bash
# KnowledgeBot Kubernetes 部署脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== KnowledgeBot Kubernetes 部署 ==="
echo ""

# 检查 kubectl
if ! command -v kubectl &> /dev/null; then
    echo "错误: kubectl 未安装"
    exit 1
fi

# 检查集群连接
echo "检查 Kubernetes 集群连接..."
kubectl cluster-info &> /dev/null || {
    echo "错误: 无法连接到 Kubernetes 集群"
    exit 1
}
echo "集群连接成功 ✓"
echo ""

# 命令选项
case "$1" in
    "deploy")
        echo "部署基础设施..."
        kubectl apply -f "$SCRIPT_DIR/infrastructure.yaml"
        echo ""
        echo "等待基础设施就绪..."
        kubectl wait --for=condition=ready pod -l app=postgres -n knowledgebot --timeout=120s || true
        kubectl wait --for=condition=ready pod -l app=redis -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=milvus -n knowledgebot --timeout=180s || true
        kubectl wait --for=condition=ready pod -l app=minio -n knowledgebot --timeout=60s || true
        echo ""
        echo "构建服务镜像..."
        cd "$PROJECT_DIR"
        docker build -t knowledgebot-auth:latest -f services/auth/Dockerfile services/auth
        docker build -t knowledgebot-knowledge:latest -f services/knowledge/Dockerfile services/knowledge
        docker build -t knowledgebot-embedding:latest -f services/embedding/Dockerfile services/embedding
        docker build -t knowledgebot-chat:latest -f services/chat/Dockerfile services/chat
        docker build -t knowledgebot-ingest:latest -f services/ingest/Dockerfile services/ingest
        docker build -t knowledgebot-web:latest -f web/Dockerfile web
        echo ""
        echo "部署微服务..."
        kubectl apply -f "$SCRIPT_DIR/services.yaml"
        kubectl apply -f "$SCRIPT_DIR/hpa.yaml"
        echo ""
        echo "等待服务就绪..."
        kubectl wait --for=condition=ready pod -l app=auth -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=knowledge -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=embedding -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=chat -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=ingest -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=gateway -n knowledgebot --timeout=60s || true
        kubectl wait --for=condition=ready pod -l app=web -n knowledgebot --timeout=60s || true
        echo ""
        echo "部署完成 ✓"
        echo ""
        echo "访问地址:"
        echo "  Web UI:    http://knowledgebot.local (需配置 DNS 或添加到 /etc/hosts)"
        echo "  API:       http://knowledgebot.local/v1/"
        echo ""
        echo "查看状态:"
        echo "  kubectl get pods -n knowledgebot"
        echo "  kubectl get services -n knowledgebot"
        ;;
    
    "delete")
        echo "删除所有资源..."
        kubectl delete -f "$SCRIPT_DIR/hpa.yaml" || true
        kubectl delete -f "$SCRIPT_DIR/services.yaml" || true
        kubectl delete -f "$SCRIPT_DIR/infrastructure.yaml" || true
        echo "删除完成 ✓"
        ;;
    
    "status")
        echo "Pod 状态:"
        kubectl get pods -n knowledgebot
        echo ""
        echo "Service 状态:"
        kubectl get services -n knowledgebot
        echo ""
        echo "HPA 状态:"
        kubectl get hpa -n knowledgebot
        echo ""
        echo "Ingress 状态:"
        kubectl get ingress -n knowledgebot
        ;;
    
    "logs")
        SERVICE="$2"
        if [ -z "$SERVICE" ]; then
            echo "用法: $0 logs <service-name>"
            echo "可用服务: auth, knowledge, embedding, chat, ingest, ingest-worker, gateway, web"
            exit 1
        fi
        kubectl logs -f -l app="$SERVICE" -n knowledgebot --all-containers=true
        ;;
    
    "scale")
        SERVICE="$2"
        REPLICAS="$3"
        if [ -z "$SERVICE" ] || [ -z "$REPLICAS" ]; then
            echo "用法: $0 scale <service-name> <replicas>"
            exit 1
        fi
        kubectl scale deployment "$SERVICE" --replicas="$REPLICAS" -n knowledgebot
        echo "已将 $SERVICE 扩缩到 $REPLICAS副本"
        ;;
    
    *)
        echo "用法: $0 <command>"
        echo ""
        echo "命令:"
        echo "  deploy    - 部署所有资源"
        echo "  delete    - 删除所有资源"
        echo "  status    - 查看部署状态"
        echo "  logs      - 查看服务日志 (需指定服务名)"
        echo "  scale     - 手动扩缩容 (需指定服务名和副本数)"
        echo ""
        echo "示例:"
        echo "  $0 deploy"
        echo "  $0 logs auth"
        echo "  $0 scale chat 5"
        ;;
esac