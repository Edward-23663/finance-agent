"""Tushare数据源适配器"""
from typing import Dict, Any, Optional
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class TushareAdapter(DataSourceAdapter):
    """Tushare数据源适配器（主力）"""

    def __init__(self, token: str):
        self.token = token
        self._client = None

    def _get_client(self):
        """获取Tushare客户端"""
        if self._client is None:
            try:
                import tushare as ts

                self._client = ts.pro_api(self.token)
            except ImportError:
                raise ImportError("请安装tushare: pip install tushare")
        return self._client

    def get_price(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        self.validate_ticker(ticker)

        try:
            client = self._get_client()
            df = client.daily(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                start_date=start_date,
                end_date=end_date,
            )

            if df is not None and not df.empty:
                df = df.rename(
                    columns={
                        "ts_code": "ticker",
                        "trade_date": "trade_date",
                        "open": "open",
                        "high": "high",
                        "low": "low",
                        "close": "close",
                        "vol": "volume",
                        "amount": "amount",
                    }
                )
                df["ticker"] = ticker

            return df or pd.DataFrame()
        except Exception as e:
            print(f"Tushare get_price error: {e}")
            return pd.DataFrame()

    def get_financial(self, ticker: str, report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        self.validate_ticker(ticker)

        try:
            client = self._get_client()

            report_type_map = {"annual": "410001", "semi": "410002", "quarter": "410003"}

            fin_type = report_type_map.get(report_type, "410001")

            df = client.fina_indicator(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                report_type=fin_type,
            )

            if df is not None and not df.empty:
                return df.iloc[0].to_dict()

            return {}
        except Exception as e:
            print(f"Tushare get_financial error: {e}")
            return {}

    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        self.validate_ticker(ticker)

        try:
            client = self._get_client()

            df = client.stock_basic(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                fields="ts_code,name,industry,list_date,market",
            )

            if df is not None and not df.empty:
                row = df.iloc[0]
                return {
                    "ticker": ticker,
                    "name": row.get("name"),
                    "industry": row.get("industry"),
                    "list_date": row.get("list_date"),
                    "market_type": row.get("market"),
                }

            return {}
        except Exception as e:
            print(f"Tushare get_stock_info error: {e}")
            return {}
