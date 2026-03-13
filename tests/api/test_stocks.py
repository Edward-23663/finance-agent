"""股票数据查询API测试"""
import pytest
from unittest.mock import patch, MagicMock


class TestStocksAPI:
    """股票数据查询API测试"""

    def test_router_defined(self):
        """测试路由已定义"""
        from src.api.routes import stocks

        assert hasattr(stocks, "router")

    def test_stock_info_model(self):
        """测试股票信息模型"""
        from src.api.routes.stocks import StockInfo

        info = StockInfo(ticker="600519", name="贵州茅台", industry="白酒")

        assert info.ticker == "600519"
        assert info.name == "贵州茅台"

    def test_price_data_model(self):
        """测试行情数据模型"""
        from src.api.routes.stocks import PriceData
        from datetime import date

        price = PriceData(
            ticker="600519",
            trade_date=date(2024, 1, 1),
            open=1800.0,
            high=1850.0,
            low=1790.0,
            close=1820.0,
            volume=1000000,
        )

        assert price.ticker == "600519"
        assert price.close == 1820.0
