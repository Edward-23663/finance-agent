"""报告生成Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class ReportGenerationAgent(BaseAgent):
    """报告生成Agent - 生成分析报告"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行报告生成任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")

        if task_type == "generate_report":
            return await self._generate_full_report(ticker)
        elif task_type == "generate_summary":
            return await self._generate_summary(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _generate_full_report(self, ticker: str) -> Dict[str, Any]:
        """生成完整分析报告"""
        stock_info = self.db.query_stock_info(ticker)
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)

        if not stock_info:
            return {"status": "failed", "error": "No stock info"}

        info = stock_info[0]
        current_price = price_data[0].get("close") if price_data else 0
        fin = financial[0] if financial else {}

        report_lines = []
        report_lines.append(f"# {info.get('name', ticker)} ({ticker}) 分析报告")
        report_lines.append("")
        report_lines.append("## 基本信息")
        report_lines.append(f"- 行业: {info.get('industry', 'N/A')}")
        report_lines.append(f"- 上市日期: {info.get('list_date', 'N/A')}")
        report_lines.append(f"- 当前价格: {current_price}")
        report_lines.append("")

        if fin:
            report_lines.append("## 财务指标")
            report_lines.append(f"- ROE: {fin.get('roe', 'N/A')}")
            report_lines.append(f"- 毛利率: {fin.get('gross_margin', 'N/A')}")
            report_lines.append(f"- 净利率: {fin.get('net_margin', 'N/A')}")
            report_lines.append(f"- 当前比率: {fin.get('current_ratio', 'N/A')}")
            report_lines.append("")

        report = "\n".join(report_lines)

        return {
            "status": "success",
            "ticker": ticker,
            "report": report,
        }

    async def _generate_summary(self, ticker: str) -> Dict[str, Any]:
        """生成简短摘要"""
        stock_info = self.db.query_stock_info(ticker)

        if not stock_info:
            return {"status": "failed", "error": "No stock info"}

        info = stock_info[0]

        summary = f"{info.get('name', ticker)} - {info.get('industry', 'N/A')}行业"

        return {
            "status": "success",
            "ticker": ticker,
            "summary": summary,
        }
