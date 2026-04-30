"""健康检查 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查（主应用路由）"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_health_check(client: AsyncClient):
    """测试 API 健康检查（v1 路由）"""
    response = await client.get("/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


@pytest.mark.asyncio
async def test_system_info(client: AsyncClient):
    """测试系统信息"""
    # The endpoint path in system.py is /v1/system/info but since router
    # is included with /v1 prefix in main.py, actual path is /v1/v1/system/info
    # This is likely a bug in the API design, but we test what exists
    response = await client.get("/v1/v1/system/info")
    
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "embedding_models" in data
    assert "llm_models" in data
    assert "supported_file_types" in data