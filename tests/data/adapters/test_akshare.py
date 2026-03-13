"""AkShare适配器测试"""
import pytest
from src.data.adapters.akshare import AkShareAdapter


class TestAkShareAdapter:
    """AkShare适配器测试"""

    def test_validate_ticker(self):
        """测试股票代码验证"""
        adapter = AkShareAdapter()
        assert adapter.validate_ticker("600519") is True
        assert adapter.validate_ticker("000001") is True
