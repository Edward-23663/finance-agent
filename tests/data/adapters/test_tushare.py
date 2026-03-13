"""Tushare适配器测试"""
import pytest
from src.data.adapters.tushare import TushareAdapter


class TestTushareAdapter:
    """Tushare适配器测试"""

    def test_init(self):
        """测试初始化"""
        adapter = TushareAdapter("test_token")
        assert adapter.token == "test_token"

    def test_validate_ticker(self):
        """测试股票代码验证"""
        adapter = TushareAdapter("test_token")
        assert adapter.validate_ticker("600519") is True
        assert adapter.validate_ticker("123456") is True
        assert adapter.validate_ticker("12345") is False
        assert adapter.validate_ticker("abc") is False
