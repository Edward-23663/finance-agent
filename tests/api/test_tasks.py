"""任务管理API测试"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime


class TestTasksAPI:
    """任务管理API测试"""

    @pytest.fixture
    def mock_settings(self):
        with patch("src.api.deps.get_settings") as mock:
            settings = MagicMock()
            settings.api_key = ""
            mock.return_value = settings
            yield settings

    @pytest.fixture
    def mock_orchestrator(self):
        with patch("src.api.routes.tasks.get_orchestrator") as mock:
            orch = AsyncMock()
            orch.submit_task = AsyncMock(
                return_value={"trace_id": "20260313_test123", "status": "pending"}
            )
            orch.get_task_result = AsyncMock(
                return_value={
                    "trace_id": "20260313_test123",
                    "status": "running",
                    "progress": 50,
                    "created_at": datetime.now().isoformat(),
                }
            )
            mock.return_value = orch
            yield orch

    @pytest.mark.asyncio
    async def test_create_task(self, mock_settings, mock_orchestrator):
        """测试创建任务"""
        from src.api.routes.tasks import create_task, TaskRequest

        request = TaskRequest(
            ticker="600519", user_input="分析贵州茅台", dimensions=["fundamental", "valuation"]
        )

        with patch("src.api.routes.tasks.verify_api_key", return_value="dev_key"):
            result = await create_task(request, api_key="dev_key")

        assert result.trace_id.startswith("20260313_")
        assert result.status == "pending"
        mock_orchestrator.submit_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_status(self, mock_settings, mock_orchestrator):
        """测试获取任务状态"""
        from src.api.routes.tasks import get_task

        with patch("src.api.routes.tasks.verify_api_key", return_value="dev_key"):
            result = await get_task("20260313_test123", api_key="dev_key")

        assert result["trace_id"] == "20260313_test123"
        assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, mock_settings, mock_orchestrator):
        """测试任务不存在"""
        from src.api.routes.tasks import get_task
        from fastapi import HTTPException

        mock_orchestrator.get_task_result = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            with patch("src.api.routes.tasks.verify_api_key", return_value="dev_key"):
                await get_task("nonexistent", api_key="dev_key")

        assert exc_info.value.status_code == 404

    def test_task_request_model(self):
        """测试请求模型"""
        from src.api.routes.tasks import TaskRequest

        request = TaskRequest(
            ticker="600519",
            user_input="分析贵州茅台",
            dimensions=["fundamental", "valuation"],
            options={"report_format": "markdown"},
        )

        assert request.ticker == "600519"
        assert request.dimensions == ["fundamental", "valuation"]
        assert request.options["report_format"] == "markdown"

    def test_task_response_model(self):
        """测试响应模型"""
        from src.api.routes.tasks import TaskResponse

        response = TaskResponse(
            trace_id="20260313_test123", status="pending", created_at=datetime.now()
        )

        assert response.trace_id == "20260313_test123"
        assert response.status == "pending"
