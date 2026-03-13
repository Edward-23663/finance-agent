"""AkShare数据源适配器"""
from typing import Dict, Any
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class AkShareAdapter(DataSourceAdapter):
    """AkShare数据源适配器（补充）"""

    def get_price(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        self.validate_ticker(ticker)

        try:
            import akshare as ak

            df = ak.stock_zh_a_hist(
                symbol=ticker,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )

            if df is not None and not df.empty:
                df = df.rename(
                    columns={
                        "日期": "trade_date",
                        "股票代码": "ticker",
                        "开盘": "open",
                        "收盘": "close",
                        "最高": "high",
                        "最低": "low",
                        "成交量": "volume",
                        "成交额": "amount",
                    }
                )
                df["ticker"] = ticker

            return df or pd.DataFrame()
        except Exception as e:
            print(f"AkShare get_price error: {e}")
            return pd.DataFrame()

    def get_financial(self, ticker: str, report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        self.validate_ticker(ticker)
        return {}

    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        self.validate_ticker(ticker)

        try:
            import akshare as ak

            df = ak.stock_individual_info_em(symbol=ticker)

            if df is not None and not df.empty:
                info = {}
                for _, row in df.iterrows():
                    info[row.get("item", "")] = row.get("value")

                return {
                    "ticker": ticker,
                    "name": info.get("股票名称"),
                    "industry": info.get("所属行业"),
                    "list_date": info.get("上市日期"),
                    "market_type": info.get("交易所"),
                }

            return {}
        except Exception as e:
            print(f"AkShare get_stock_info error: {e}")
            return {}
