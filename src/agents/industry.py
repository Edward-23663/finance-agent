"""行业持仓分析Agent"""
from typing import Dict, Any, List
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class IndustryAnalysisAgent(BaseAgent):
    """行业持仓分析Agent - 负责行业分类、成分股、轮动分析、持仓性价比分析"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.duckdb = DuckDBClient()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        task_type = task_data.get("type")

        if task_type == "get_industry":
            return await self._get_industry_classification(task_data.get("ticker"))
        elif task_type == "get_constituents":
            return await self._get_constituents(task_data.get("industry"))
        elif task_type == "calculate_trend":
            return await self._calculate_trend(task_data.get("industry"))
        elif task_type == "industry_rotation":
            return await self._industry_rotation_analysis()
        elif task_type == "portfolio_analysis":
            return await self._portfolio_analysis(task_data.get("tickers"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _get_industry_classification(self, ticker: str) -> Dict[str, Any]:
        query = "SELECT industry, level FROM stock_info WHERE ticker = ?"
        result = self.duckdb.execute(query, [ticker])
        data = [dict(row) for row in result]
        return {"status": "success", "data": data}

    async def _get_constituents(self, industry: str) -> Dict[str, Any]:
        query = "SELECT ticker, name FROM stock_info WHERE industry = ?"
        result = self.duckdb.execute(query, [industry])
        data = [dict(row) for row in result]
        return {"status": "success", "data": data, "count": len(data)}

    async def _calculate_trend(self, industry: str) -> Dict[str, Any]:
        query = """
            SELECT p.trade_date, p.close
            FROM price_daily p
            JOIN stock_info s ON p.ticker = s.ticker
            WHERE s.industry = ?
            ORDER BY p.trade_date DESC
            LIMIT 30
        """
        result = self.duckdb.execute(query, [industry])
        data = [dict(row) for row in result]

        if len(data) >= 2:
            trend = "up" if data[0]["close"] > data[-1]["close"] else "down"
        else:
            trend = "neutral"

        return {"status": "success", "trend": trend, "data": data}

    async def _industry_rotation_analysis(self) -> Dict[str, Any]:
        query = """
            SELECT 
                s.industry,
                AVG(p.close) as avg_price
            FROM price_daily p
            JOIN stock_info s ON p.ticker = s.ticker
            WHERE p.trade_date >= date('now', '-30 days')
            GROUP BY s.industry
            ORDER BY avg_price DESC
        """
        result = self.duckdb.execute(query)
        data = [dict(row) for row in result]
        return {"status": "success", "data": data}

    async def _portfolio_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        if not tickers:
            return {"status": "success", "data": []}

        placeholders = ",".join(["?"] * len(tickers))
        query = f"""
            SELECT 
                s.ticker,
                s.name,
                s.industry,
                f.roe,
                f.pe
            FROM stock_info s
            LEFT JOIN financial_metrics f ON s.ticker = f.ticker
            WHERE s.ticker IN ({placeholders})
        """
        result = self.duckdb.execute(query, tickers)
        data = [dict(row) for row in result]

        for item in data:
            pe = item.get("pe", 0)
            roe = item.get("roe", 0)
            if pe and roe and pe > 0:
                item["value_score"] = roe / pe
            else:
                item["value_score"] = 0

        data.sort(key=lambda x: x.get("value_score", 0), reverse=True)

        return {"status": "success", "data": data}
