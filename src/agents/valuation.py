"""估值Agent"""
from typing import Dict, Any
from datetime import date
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient
from src.data.writer import DataWriter, WriteTask, WriteTaskType


class ValuationAgent(BaseAgent):
    """估值Agent - 计算股票估值指标"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()
        self.writer = DataWriter()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行估值任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")

        if task_type == "calculate_pe":
            return await self._calculate_pe(ticker)
        elif task_type == "calculate_pb":
            return await self._calculate_pb(ticker)
        elif task_type == "calculate_dcf":
            return await self._calculate_dcf(ticker)
        elif task_type == "full_valuation":
            return await self._full_valuation(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _calculate_pe(self, ticker: str) -> Dict[str, Any]:
        """计算市盈率"""
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)

        if not price_data or not financial:
            return {"status": "failed", "error": "Insufficient data"}

        price = price_data[0].get("close", 0)
        eps = financial[0].get("eps", 0) or 1

        pe = price / eps if eps > 0 else 0

        return {
            "status": "success",
            "ticker": ticker,
            "pe": round(pe, 2),
            "price": price,
            "eps": eps,
        }

    async def _calculate_pb(self, ticker: str) -> Dict[str, Any]:
        """计算市净率"""
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)

        if not price_data or not financial:
            return {"status": "failed", "error": "Insufficient data"}

        price = price_data[0].get("close", 0)
        bps = financial[0].get("bps", 0) or 1

        pb = price / bps if bps > 0 else 0

        return {
            "status": "success",
            "ticker": ticker,
            "pb": round(pb, 2),
            "price": price,
            "bps": bps,
        }

    async def _calculate_dcf(self, ticker: str) -> Dict[str, Any]:
        """简化DCF估值"""
        financial = self.db.query_financial_metrics(ticker)

        if not financial:
            return {"status": "failed", "error": "No financial data"}

        latest = financial[0]
        free_cash_flow = latest.get("net_profit", 0) or 1000000000

        growth_rate = 0.05
        discount_rate = 0.10
        years = 5

        dcf_value = 0
        for i in range(1, years + 1):
            dcf_value += free_cash_flow * (1 + growth_rate) ** i / (1 + discount_rate) ** i

        terminal_value = (
            free_cash_flow * (1 + growth_rate) ** years * (1 + 0.03) / (discount_rate - 0.03)
        )
        terminal_value /= (1 + discount_rate) ** years

        total_value = dcf_value + terminal_value

        return {
            "status": "success",
            "ticker": ticker,
            "dcf_value": round(total_value, 2),
        }

    async def _full_valuation(self, ticker: str) -> Dict[str, Any]:
        """完整估值"""
        pe_result = await self._calculate_pe(ticker)
        pb_result = await self._calculate_pb(ticker)
        dcf_result = await self._calculate_dcf(ticker)

        pe = pe_result.get("pe", 0)
        pb = pb_result.get("pb", 0)
        dcf = dcf_result.get("dcf_value", 0)

        fair_value = (pe * 0.3 + pb * 0.2 + dcf * 0.5) if dcf > 0 else 0

        task = WriteTask(
            task_type=WriteTaskType.VALUATION,
            data={
                "ticker": ticker,
                "valuation_date": str(date.today()),
                "pe": pe,
                "pb": pb,
                "dcf_value": dcf,
                "fair_value_mid": fair_value,
            },
        )
        self.writer.enqueue(task)

        return {
            "status": "success",
            "ticker": ticker,
            "pe": pe,
            "pb": pb,
            "dcf_value": dcf,
            "fair_value": round(fair_value, 2),
        }
