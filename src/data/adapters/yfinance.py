"""YFinance数据源适配器"""
from typing import Dict, Any
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class YFinanceAdapter(DataSourceAdapter):
    """YFinance数据源适配器（海外）"""

    def get_price(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        try:
            import yfinance as yf

            df = yf.download(ticker, start=start_date, end=end_date)

            if df is not None and not df.empty:
                df = df.reset_index()
                df = df.rename(
                    columns={
                        "Date": "trade_date",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Volume": "volume",
                        "Adj Close": "close",
                    }
                )
                df["ticker"] = ticker
                df["amount"] = df["close"] * df["volume"]

            return df or pd.DataFrame()
        except Exception as e:
            print(f"YFinance get_price error: {e}")
            return pd.DataFrame()

    def get_financial(self, ticker: str, report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)
            financials = stock.financials

            if financials is not None and not financials.empty:
                return financials.iloc[0].to_dict()

            return {}
        except Exception as e:
            print(f"YFinance get_financial error: {e}")
            return {}

    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "name": info.get("shortName"),
                "industry": info.get("industry"),
                "list_date": info.get("firstTradeDate"),
                "market_type": info.get("exchange"),
            }
        except Exception as e:
            print(f"YFinance get_stock_info error: {e}")
            return {}
