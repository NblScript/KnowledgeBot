"""健康检查 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_system_info(client: AsyncClient):
    """测试系统信息"""
    response = await client.get("/v1/system/info")
    
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "embedding_models" in data
    assert "llm_models" in data