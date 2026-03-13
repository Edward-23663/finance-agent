"""SSE流式推送测试"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime


class TestSSE:
    """SSE流式推送测试"""

    @pytest.fixture
    def mock_redis(self):
        with patch("src.api.sse.redis") as mock:
            mock_client = AsyncMock()
            mock.Redis.return_value = mock_client
            yield mock_client

    def test_sse_route_defined(self):
        """测试SSE路由已定义"""
        from src.api import sse

        assert hasattr(sse, "router")

    def test_event_generator_import(self):
        """测试事件生成器可导入"""
        from src.api.sse import event_generator

        assert event_generator is not None

    def test_stream_endpoint_exists(self):
        """测试流式端点存在"""
        from src.api.sse import router

        route_paths = []
        for route in router.routes:
            if hasattr(route, "path"):
                route_paths.append(route.path)
        assert any("/stream/" in p for p in route_paths)
