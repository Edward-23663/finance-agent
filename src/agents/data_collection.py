"""数据采集Agent"""
import asyncio
from typing import Dict, Any
import pandas as pd
from src.agents.base import BaseAgent, AgentConfig
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.akshare import AkShareAdapter
from src.data.adapters.yfinance import YFinanceAdapter
from src.data.writer import DataWriter, WriteTask, WriteTaskType
from src.config import get_settings


class DataCollectionAgent(BaseAgent):
    """数据采集Agent - 负责从数据源采集数据并写入存储"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        settings = get_settings()

        self.tushare = TushareAdapter(settings.tushare_token)
        self.akshare = AkShareAdapter()
        self.yfinance = YFinanceAdapter()
        self.writer = DataWriter()

        self.source_priority = ["tushare", "akshare", "yfinance"]

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行数据采集任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")

        if task_type == "collect_price":
            return await self._collect_price_data(
                ticker,
                task_data.get("start_date"),
                task_data.get("end_date"),
            )
        elif task_type == "collect_financial":
            return await self._collect_financial_data(ticker)
        elif task_type == "collect_stock_info":
            return await self._collect_stock_info(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _collect_price_data(
        self, ticker: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """采集行情数据"""
        for source_name in self.source_priority:
            try:
                adapter = getattr(self, source_name)
                df = adapter.get_price(ticker, start_date, end_date)

                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        task = WriteTask(
                            task_type=WriteTaskType.PRICE_DAILY,
                            data={
                                "ticker": row.get("ticker", ticker),
                                "trade_date": row.get("trade_date"),
                                "open": row.get("open"),
                                "high": row.get("high"),
                                "low": row.get("low"),
                                "close": row.get("close"),
                                "volume": row.get("volume"),
                                "amount": row.get("amount"),
                            },
                        )
                        self.writer.enqueue(task)

                    return {
                        "status": "success",
                        "source": source_name,
                        "rows": len(df),
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue

        return {"status": "failed", "error": "All sources failed"}

    async def _collect_financial_data(self, ticker: str) -> Dict[str, Any]:
        """采集财务数据"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_financial(ticker)

                if data:
                    task = WriteTask(
                        task_type=WriteTaskType.FINANCIAL_METRIC,
                        data={
                            "ticker": ticker,
                            "report_date": data.get("report_date"),
                            "report_type": data.get("report_type", "annual"),
                            "roe": data.get("roe"),
                            "roa": data.get("roa"),
                            "gross_margin": data.get("gross_margin"),
                            "net_margin": data.get("net_margin"),
                            "current_ratio": data.get("current_ratio"),
                            "debt_ratio": data.get("debt_ratio"),
                            "eps": data.get("eps"),
                            "bps": data.get("bps"),
                        },
                    )
                    self.writer.enqueue(task)

                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue

        return {"status": "failed", "error": "All sources failed"}

    async def _collect_stock_info(self, ticker: str) -> Dict[str, Any]:
        """采集股票基本信息"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_stock_info(ticker)

                if data:
                    task = WriteTask(
                        task_type=WriteTaskType.STOCK_INFO,
                        data={
                            "ticker": data.get("ticker", ticker),
                            "name": data.get("name"),
                            "industry": data.get("industry"),
                            "list_date": data.get("list_date"),
                            "market_type": data.get("market_type"),
                        },
                    )
                    self.writer.enqueue(task)

                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue

        return {"status": "failed", "error": "All sources failed"}
