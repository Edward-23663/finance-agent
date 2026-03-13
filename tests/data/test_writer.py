"""DataWriter测试"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch
from src.data.writer import DataWriter, WriteTask, WriteTaskType


class TestWriteTask:
    """写任务测试"""

    def test_write_task_creation(self):
        """测试写任务创建"""
        task = WriteTask(
            task_type=WriteTaskType.PRICE_DAILY, data={"ticker": "600519", "close": 1800.0}
        )

        assert task.task_type == WriteTaskType.PRICE_DAILY
        assert task.data["ticker"] == "600519"

    def test_serialize(self):
        """测试任务序列化"""
        task = WriteTask(
            task_type=WriteTaskType.FINANCIAL_STATEMENT,
            data={"ticker": "600519", "revenue": 1000000},
        )

        serialized = task.serialize()
        import json

        parsed = json.loads(serialized)
        assert "task_type" in parsed
        assert parsed["task_type"] == "financial_statement"


class TestDataWriter:
    """DataWriter测试"""

    @pytest.fixture
    def writer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            with patch("src.data.writer.DuckDBClient") as mock_client:
                mock_instance = Mock()
                mock_client.return_value = mock_instance
                yield DataWriter(db_path=db_path)

    def test_enqueue(self, writer):
        """测试入队"""
        task = WriteTask(
            task_type=WriteTaskType.PRICE_DAILY, data={"ticker": "600519", "close": 1800.0}
        )

        with patch.object(writer.redis, "lpush") as mock_lpush:
            writer.enqueue(task)
            mock_lpush.assert_called_once()
