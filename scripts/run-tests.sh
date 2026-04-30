#!/bin/bash
# KnowledgeBot 本地测试脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== KnowledgeBot 测试套件 ==="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 安装测试依赖
echo "安装测试依赖..."
pip install -q pytest pytest-asyncio pytest-cov httpx

# 运行各服务测试
SERVICES="auth knowledge embedding chat ingest"
TOTAL_PASSED=0
TOTAL_FAILED=0

for service in $SERVICES; do
    SERVICE_DIR="$PROJECT_DIR/services/$service"
    
    if [ -d "$SERVICE_DIR/tests" ]; then
        echo ""
        echo "测试 $service 服务..."
        echo "----------------------------------------"
        
        cd "$SERVICE_DIR"
        
        # 安装服务依赖
        if [ -f "requirements.txt" ]; then
            pip install -q -r requirements.txt
        fi
        
        # 运行测试
        if python3 -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing; then
            echo "✓ $service 测试通过"
            TOTAL_PASSED=$((TOTAL_PASSED + 1))
        else
            echo "✗ $service 测试失败"
            TOTAL_FAILED=$((TOTAL_FAILED + 1))
        fi
        
        cd "$PROJECT_DIR"
    else
        echo "跳过 $service (无测试目录)"
    fi
done

# 运行 Web 测试
echo ""
echo "测试 Web UI..."
echo "----------------------------------------"
if [ -d "$PROJECT_DIR/web" ]; then
    cd "$PROJECT_DIR/web"
    
    if [ -f "package.json" ]; then
        npm ci --quiet
        npm run lint
        npm run build
        
        echo "✓ Web UI 测试通过"
        TOTAL_PASSED=$((TOTAL_PASSED + 1))
    fi
    
    cd "$PROJECT_DIR"
fi

# 输出汇总
echo ""
echo "========================================"
echo "测试汇总"
echo "========================================"
echo "通过: $TOTAL_PASSED"
echo "失败: $TOTAL_FAILED"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "✓ 所有测试通过!"
    exit 0
else
    echo "✗ 有测试失败"
    exit 1
fi