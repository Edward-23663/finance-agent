"""舆情分析Agent"""
from typing import Dict, Any, List
from src.agents.base import BaseAgent, AgentConfig
from src.data.lancedb_client import LanceDBClient
from src.communication.redis_client import RedisClient


class SentimentAnalysisAgent(BaseAgent):
    """舆情分析Agent - 负责舆情抓取、情感极性打分、热度计算、事件聚类、风险预警"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.lancedb = LanceDBClient()
        self.redis = RedisClient()

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        task_type = task_data.get("type")

        if task_type == "collect_sentiment":
            return await self._collect_sentiment(task_data.get("ticker"))
        elif task_type == "sentiment_score":
            return await self._sentiment_score(task_data.get("text"))
        elif task_type == "calculate_heat":
            return await self._calculate_heat(task_data.get("ticker"))
        elif task_type == "event_clustering":
            return await self._event_clustering(task_data.get("ticker"))
        elif task_type == "risk_warning":
            return await self._risk_warning(task_data.get("ticker"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _collect_sentiment(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(ticker, top_k=50)
        return {"status": "success", "data": results, "count": len(results)}

    async def _sentiment_score(self, text: str) -> Dict[str, Any]:
        positive_words = ["增长", "盈利", "上涨", "突破", "利好", "推荐", "买入", "增持"]
        negative_words = ["下跌", "亏损", "风险", "利空", "违规", "减持", "卖出", "警告"]

        score = 0.5
        for word in positive_words:
            if word in text:
                score += 0.1
        for word in negative_words:
            if word in text:
                score -= 0.1

        score = max(0.0, min(1.0, score))

        sentiment = "positive" if score > 0.6 else "negative" if score < 0.4 else "neutral"

        return {"status": "success", "score": score, "sentiment": sentiment, "text": text}

    async def _calculate_heat(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(ticker, top_k=100)
        heat = len(results) * 0.1
        return {"status": "success", "heat": heat, "ticker": ticker}

    async def _event_clustering(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(ticker, top_k=50)

        clusters: Dict[int, List[Dict]] = {}
        keywords = ["业绩", "分红", "收购", "减持", "重组"]

        for i, item in enumerate(results):
            text = item.get("text", "")
            cluster_id = 0
            for j, kw in enumerate(keywords):
                if kw in text:
                    cluster_id = j + 1
                    break
            clusters.setdefault(cluster_id, []).append(item)

        return {"status": "success", "clusters": clusters}

    async def _risk_warning(self, ticker: str) -> Dict[str, Any]:
        results = self.lancedb.search(ticker, top_k=20)

        negative_keywords = ["跌", "亏", "损", "风险", "违规", "处罚", "诉讼", "减持"]
        positive_keywords = ["涨", "增", "盈", "利", "分红", "回购"]

        negative_count = 0
        positive_count = 0

        for item in results:
            text = item.get("text", "")
            for kw in negative_keywords:
                if kw in text:
                    negative_count += 1
                    break
            for kw in positive_keywords:
                if kw in text:
                    positive_count += 1
                    break

        if negative_count > positive_count + 3:
            level = "high"
        elif negative_count > positive_count:
            level = "medium"
        else:
            level = "low"

        reasons = []
        if negative_count > 5:
            reasons.append("负面舆情较多")
        if positive_count > 5:
            reasons.append("正面舆情较多")

        return {
            "status": "success",
            "level": level,
            "negative_count": negative_count,
            "positive_count": positive_count,
            "reasons": reasons,
        }
