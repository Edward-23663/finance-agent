"""数据源适配器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd


class DataSourceAdapter(ABC):
    """数据源适配器基类"""

    @abstractmethod
    def get_price(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取行情数据

        Args:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame包含 OHLCV 数据
        """
        pass

    @abstractmethod
    def get_financial(self, ticker: str, report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据

        Args:
            ticker: 股票代码
            report_type: 报告类型 (annual/semi/quarter)

        Returns:
            财务数据字典
        """
        pass

    @abstractmethod
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息

        Args:
            ticker: 股票代码

        Returns:
            股票信息字典
        """
        pass

    def validate_ticker(self, ticker: str) -> bool:
        """验证股票代码格式"""
        return bool(ticker and ticker.isdigit() and len(ticker) == 6)
