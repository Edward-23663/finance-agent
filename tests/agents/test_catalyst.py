"""催化剂分析Agent测试"""
import pytest
from unittest.mock import Mock, patch
from src.agents.catalyst import CatalystAnalysisAgent
from src.agents.base import AgentConfig


class TestCatalystAnalysisAgent:
    @pytest.fixture
    def config(self):
        return AgentConfig(
            name="catalyst", stream_key="tasks:catalyst", consumer_group="catalyst_group"
        )

    @pytest.fixture
    def agent(self, config):
        with patch("src.agents.catalyst.LanceDBClient"):
            return CatalystAnalysisAgent(config)

    @pytest.mark.asyncio
    async def test_collect_catalyst(self, agent):
        """测试催化剂事件抓取"""
        agent.lancedb.search = Mock(return_value=[{"text": "业绩预增公告", "date": "2024-01-15"}])

        result = await agent.execute({"type": "collect_catalyst", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_classify_by_time(self, agent):
        """测试时间维度分类"""
        agent.lancedb.search = Mock(
            return_value=[
                {"text": "业绩预告", "date": "2024-01-15"},
                {"text": "产能规划", "date": "2024-06-15"},
                {"text": "战略合作", "date": "2025-01-15"},
            ]
        )

        result = await agent.execute({"type": "classify_by_time", "ticker": "600519"})

        assert result["status"] == "success"
        assert "short_term" in result

    @pytest.mark.asyncio
    async def test_impact_score(self, agent):
        """测试影响力度打分"""
        result = await agent.execute({"type": "impact_score", "event": "业绩大幅预增"})

        assert result["status"] == "success"
        assert "score" in result

    @pytest.mark.asyncio
    async def test_extract_time_node(self, agent):
        """测试时间节点提取"""
        result = await agent.execute(
            {"type": "extract_time_node", "event": "2024年4月30日发布年报"}
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_catalyst_impact_analysis(self, agent):
        """测试催化剂-估值影响关联"""
        agent.lancedb.search = Mock(
            return_value=[{"text": "业绩预增"}, {"text": "下跌"}, {"text": "分红"}]
        )

        result = await agent.execute({"type": "catalyst_impact_analysis", "ticker": "600519"})

        assert result["status"] == "success"
        assert "analysis" in result
