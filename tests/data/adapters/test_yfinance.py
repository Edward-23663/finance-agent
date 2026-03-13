"""YFinance适配器测试"""
import pytest
from src.data.adapters.yfinance import YFinanceAdapter


class TestYFinanceAdapter:
    """YFinance适配器测试"""

    def test_validate_ticker_international(self):
        """测试国际股票代码验证"""
        adapter = YFinanceAdapter()
        assert adapter.validate_ticker("AAPL") is False
        assert adapter.validate_ticker("MSFT") is False
