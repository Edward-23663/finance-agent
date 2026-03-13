"""SQLite配置管理测试"""
import pytest
import os
import tempfile
from src.data.sqlite_config import SQLiteConfigManager


class TestSQLiteConfigManager:
    """SQLite配置管理器测试"""

    @pytest.fixture
    def manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "config.db")
            yield SQLiteConfigManager(db_path)

    def test_set_and_get(self, manager):
        """测试设置和获取配置"""
        manager.set("test_key", "test_value")
        result = manager.get("test_key")
        assert result == "test_value"

    def test_get_nonexistent(self, manager):
        """测试获取不存在的配置"""
        result = manager.get("nonexistent")
        assert result is None

    def test_delete(self, manager):
        """测试删除配置"""
        manager.set("to_delete", "value")
        manager.delete("to_delete")
        result = manager.get("to_delete")
        assert result is None

    def test_get_all(self, manager):
        """测试获取所有配置"""
        manager.set("key1", "value1")
        manager.set("key2", "value2")
        result = manager.get_all()
        assert len(result) == 2
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
