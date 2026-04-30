"""测试任务 API"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    return TestClient(app)


class TestTaskAPI:
    """测试任务 API"""
    
    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ingest-service"
        assert data["status"] == "running"
    
    def test_health(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ingest"
    
    @patch("app.api.v1.tasks.process_document_task")
    def test_create_task(self, mock_task, client):
        """测试创建任务"""
        # Mock Celery task
        mock_result = MagicMock()
        mock_result.id = "test-task-id"
        mock_task.delay.return_value = mock_result
        
        response = client.post(
            "/v1/tasks",
            json={
                "task_type": "document_process",
                "doc_id": "doc_123",
                "kb_id": "kb_456",
                "file_path": "documents/test.pdf",
                "file_name": "test.pdf",
                "file_type": "pdf",
            },
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "pending"
    
    def test_create_task_invalid_type(self, client):
        """测试创建任务 - 无效类型"""
        response = client.post(
            "/v1/tasks",
            json={
                "task_type": "invalid_type",
                "doc_id": "doc_123",
                "kb_id": "kb_456",
                "file_path": "documents/test.pdf",
                "file_name": "test.pdf",
                "file_type": "pdf",
            },
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch("app.api.v1.tasks.AsyncResult")
    def test_get_task_status_pending(self, mock_async_result, client):
        """测试获取任务状态 - 等待中"""
        mock_result = MagicMock()
        mock_result.ready.return_value = False
        mock_result.state = MagicMock(value="PENDING")
        mock_result.info = {}
        mock_async_result.return_value = mock_result
        
        response = client.get("/v1/tasks/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "pending"
    
    @patch("app.api.v1.tasks.AsyncResult")
    def test_get_task_status_completed(self, mock_async_result, client):
        """测试获取任务状态 - 已完成"""
        mock_result = MagicMock()
        mock_result.ready.return_value = True
        mock_result.get.return_value = {
            "status": "completed",
            "chunk_count": 10,
            "total_tokens": 5000,
        }
        mock_async_result.return_value = mock_result
        
        response = client.get("/v1/tasks/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "completed"
    
    @patch("app.api.v1.tasks.celery_app.control.inspect")
    def test_get_queue_stats(self, mock_inspect, client):
        """测试获取队列统计"""
        mock_inspect_instance = MagicMock()
        mock_inspect_instance.active.return_value = {"worker-1": []}
        mock_inspect_instance.reserved.return_value = {"worker-1": []}
        mock_inspect_instance.registered.return_value = {"worker-1": ["task1"]}
        mock_inspect.return_value = mock_inspect_instance
        
        response = client.get("/v1/queue/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_tasks" in data
        assert "reserved_tasks" in data
        assert "workers" in data