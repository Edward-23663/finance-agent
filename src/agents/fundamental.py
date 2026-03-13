"""基本面分析Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class FundamentalAnalysisAgent(BaseAgent):
    """基本面分析Agent - 分析公司财务健康状况"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行基本面分析任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")

        if task_type == "analyze_financial_health":
            return await self._calculate_financial_health(ticker)
        elif task_type == "analyze_growth":
            return await self._analyze_growth(ticker)
        elif task_type == "analyze_profitability":
            return await self._analyze_profitability(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _calculate_financial_health(self, ticker: str) -> Dict[str, Any]:
        """计算财务健康得分"""
        metrics = self.db.query_financial_metrics(ticker)

        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No financial data"}

        latest = metrics[0]

        roe = latest.get("roe", 0) or 0
        current_ratio = latest.get("current_ratio", 0) or 0
        debt_ratio = latest.get("debt_ratio", 0) or 0

        score = 0
        if roe > 0.15:
            score += 40
        elif roe > 0.10:
            score += 25

        if current_ratio > 2.0:
            score += 30
        elif current_ratio > 1.5:
            score += 20

        if debt_ratio < 0.3:
            score += 30
        elif debt_ratio < 0.5:
            score += 15

        return {
            "status": "success",
            "ticker": ticker,
            "score": min(score, 100),
            "roe": roe,
            "current_ratio": current_ratio,
            "debt_ratio": debt_ratio,
        }

    async def _analyze_growth(self, ticker: str) -> Dict[str, Any]:
        """分析成长性"""
        metrics = self.db.query_financial_metrics(ticker, limit=4)

        if not metrics or len(metrics) < 2:
            return {"status": "failed", "error": "Insufficient data"}

        revenue_growth = 0.0
        profit_growth = 0.0

        if len(metrics) >= 2:
            latest = metrics[0]
            previous = metrics[1]

            latest_revenue = latest.get("revenue", 0) or 0
            prev_revenue = previous.get("revenue", 0) or 0
            if prev_revenue > 0:
                revenue_growth = (latest_revenue - prev_revenue) / prev_revenue

            latest_profit = latest.get("net_profit", 0) or 0
            prev_profit = previous.get("net_profit", 0) or 0
            if prev_profit > 0:
                profit_growth = (latest_profit - prev_profit) / prev_profit

        return {
            "status": "success",
            "ticker": ticker,
            "revenue_growth": round(revenue_growth, 4),
            "profit_growth": round(profit_growth, 4),
        }

    async def _analyze_profitability(self, ticker: str) -> Dict[str, Any]:
        """分析盈利能力"""
        metrics = self.db.query_financial_metrics(ticker)

        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No data"}

        latest = metrics[0]

        return {
            "status": "success",
            "ticker": ticker,
            "gross_margin": latest.get("gross_margin", 0),
            "net_margin": latest.get("net_margin", 0),
            "roa": latest.get("roa", 0),
        }
