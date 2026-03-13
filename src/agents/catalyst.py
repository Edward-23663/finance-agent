"""催化剂分析Agent"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import re
from src.agents.base import BaseAgent, AgentConfig
from src.data.lancedb_client import LanceDBClient


class CatalystAnalysisAgent(BaseAgent):
    """催化剂分析Agent - 负责催化剂事件抓取、时间分类、影响评估"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.lancedb = LanceDBClient()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        task_type = task_data.get("type")

        if task_type == "collect_catalyst":
            return await self._collect_catalyst(task_data.get("ticker"))
        elif task_type == "classify_by_time":
            return await self._classify_by_time(task_data.get("ticker"))
        elif task_type == "impact_score":
            return await self._impact_score(task_data.get("event"))
        elif task_type == "extract_time_node":
            return await self._extract_time_node(task_data.get("event"))
        elif task_type == "catalyst_impact_analysis":
            return await self._catalyst_impact_analysis(task_data.get("ticker"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _collect_catalyst(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(f"{ticker} 催化剂", top_k=30)
        return {"status": "success", "data": results, "count": len(results)}

    async def _classify_by_time(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(ticker, top_k=30)

        short_term: List[Dict] = []
        mid_term: List[Dict] = []
        long_term: List[Dict] = []

        now = datetime.now()

        for item in results:
            date_str = item.get("date", "")
            if date_str:
                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                    days = (event_date - now).days
                    if 0 <= days <= 30:
                        short_term.append(item)
                    elif 30 < days <= 180:
                        mid_term.append(item)
                    else:
                        long_term.append(item)
                except ValueError:
                    long_term.append(item)
            else:
                long_term.append(item)

        return {
            "status": "success",
            "short_term": short_term,
            "mid_term": mid_term,
            "long_term": long_term,
        }

    async def _impact_score(self, event: str) -> Dict[str, Any]:
        high_impact_keywords = [
            "收购",
            "重组",
            "业绩预增",
            "业绩大幅增长",
            "订单",
            "合作",
            "中标",
            "扩产",
        ]
        medium_impact_keywords = ["增持", "回购", "分红", "扩产", "发布", "投资"]

        score = 0.3
        impact_level = "low"

        for keyword in high_impact_keywords:
            if keyword in event:
                score = 0.9
                impact_level = "high"
                break

        if impact_level == "low":
            for keyword in medium_impact_keywords:
                if keyword in event:
                    score = 0.6
                    impact_level = "medium"
                    break

        return {"status": "success", "score": score, "level": impact_level, "event": event}

    async def _extract_time_node(self, event: str) -> Dict[str, Any]:
        patterns = [
            (r"(\d{1,2})月(\d{1,2})日", "month_day"),
            (r"(\d{4})年(\d{1,2})月", "year_month"),
            (r"(\d{4})年", "year"),
            (r"(\d{1,2})月", "month"),
            (r"(\d{1,2})日", "day"),
        ]

        time_node = None
        matched_pattern = None

        for pattern, ptype in patterns:
            match = re.search(pattern, event)
            if match:
                time_node = match.group()
                matched_pattern = ptype
                break

        return {
            "status": "success",
            "time_node": time_node,
            "pattern": matched_pattern,
            "event": event,
        }

    async def _catalyst_impact_analysis(self, ticker: str) -> Dict[str, Any]:
        catalysts = await self._collect_catalyst(ticker)

        impact_analysis: Dict[str, List[Dict]] = {"positive": [], "negative": [], "neutral": []}

        positive_keywords = ["增", "利", "好", "盈", "收", "购", "合作", "订单"]
        negative_keywords = ["减", "亏", "损", "跌", "罚", "诉", "撤"]

        for catalyst in catalysts.get("data", []):
            text = catalyst.get("text", "")
            is_positive = any(kw in text for kw in positive_keywords)
            is_negative = any(kw in text for kw in negative_keywords)

            if is_positive and not is_negative:
                impact_analysis["positive"].append(catalyst)
            elif is_negative:
                impact_analysis["negative"].append(catalyst)
            else:
                impact_analysis["neutral"].append(catalyst)

        return {"status": "success", "analysis": impact_analysis}
