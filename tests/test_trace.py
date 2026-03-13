"""链路追踪测试"""
import pytest
from unittest.mock import MagicMock
from src.orchestrator.trace import generate_trace_id, TraceManager


class TestGenerateTraceID:
    """generate_trace_id 测试"""

    def test_generate_trace_id_format(self):
        """测试生成 Trace ID 格式"""
        trace_id = generate_trace_id()

        assert isinstance(trace_id, str)
        parts = trace_id.split("-")
        assert len(parts) == 2
        assert len(parts[0]) == 13
        assert len(parts[1]) == 8

    def test_generate_trace_id_unique(self):
        """测试生成的 ID 是唯一的"""
        ids = [generate_trace_id() for _ in range(100)]

        assert len(set(ids)) == 100


class TestTraceManager:
    """TraceManager 测试"""

    def test_create_trace(self):
        """测试创建追踪"""
        mock_redis = MagicMock()
        manager = TraceManager(mock_redis)

        manager.create_trace("test_trace", {"user": "test_user"})

        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()

    def test_add_span(self):
        """测试添加 Span"""
        mock_redis = MagicMock()
        manager = TraceManager(mock_redis)

        span_id = manager.add_span("test_trace", "data_collection", "agent", {"stock": "AAPL"})

        assert "test_trace" in span_id
        assert "data_collection" in span_id
        mock_redis.hset.assert_called()
        mock_redis.expire.assert_called()

    def test_end_span(self):
        """测试结束 Span"""
        mock_redis = MagicMock()
        manager = TraceManager(mock_redis)

        manager.end_span("span_123", {"status": "success"})

        assert mock_redis.hset.call_count == 2

    def test_get_trace(self):
        """测试获取追踪"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {"trace_id": "test_trace", "status": "started"}

        manager = TraceManager(mock_redis)
        trace = manager.get_trace("test_trace")

        assert trace["trace_id"] == "test_trace"

    def test_list_spans(self):
        """测试列出 Spans"""
        mock_redis = MagicMock()
        mock_redis.keys.return_value = ["span:1", "span:2"]
        mock_redis.hgetall.side_effect = [
            {"span_id": "span:1", "name": "data"},
            {"span_id": "span:2", "name": "analysis"},
        ]

        manager = TraceManager(mock_redis)
        spans = manager.list_spans("test_trace")

        assert len(spans) == 2
