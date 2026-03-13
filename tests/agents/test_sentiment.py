"""舆情分析Agent测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.sentiment import SentimentAnalysisAgent
from src.agents.base import AgentConfig


class TestSentimentAnalysisAgent:
    @pytest.fixture
    def config(self):
        return AgentConfig(
            name="sentiment", stream_key="tasks:sentiment", consumer_group="sentiment_group"
        )

    @pytest.fixture
    def agent(self, config):
        with patch("src.agents.sentiment.LanceDBClient"), patch("src.agents.sentiment.RedisClient"):
            return SentimentAnalysisAgent(config)

    @pytest.mark.asyncio
    async def test_collect_sentiment(self, agent):
        """测试舆情抓取"""
        agent.lancedb.search = Mock(return_value=[{"text": "茅台业绩增长", "score": 0.9}])

        result = await agent.execute({"type": "collect_sentiment", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_sentiment_score(self, agent):
        """测试情感极性打分"""
        result = await agent.execute({"type": "sentiment_score", "text": "贵州茅台业绩大幅增长"})

        assert result["status"] == "success"
        assert "score" in result

    @pytest.mark.asyncio
    async def test_calculate_heat(self, agent):
        """测试热度计算"""
        agent.lancedb.search = Mock(return_value=[{"text": "茅台"} for _ in range(10)])

        result = await agent.execute({"type": "calculate_heat", "ticker": "600519"})

        assert result["status"] == "success"
        assert "heat" in result

    @pytest.mark.asyncio
    async def test_event_clustering(self, agent):
        """测试事件聚类"""
        agent.lancedb.search = Mock(
            return_value=[{"text": "业绩预增", "cluster": 1}, {"text": "业绩公告", "cluster": 1}]
        )

        result = await agent.execute({"type": "event_clustering", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_risk_warning(self, agent):
        """测试风险预警"""
        agent.lancedb.search = Mock(
            return_value=[
                {"text": "下跌"},
                {"text": "亏损"},
                {"text": "下跌"},
            ]
        )

        result = await agent.execute({"type": "risk_warning", "ticker": "600519"})

        assert result["status"] == "success"
        assert "level" in result
