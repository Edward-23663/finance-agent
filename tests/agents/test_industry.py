"""行业持仓分析Agent测试"""
import pytest
from unittest.mock import Mock, patch
from src.agents.industry import IndustryAnalysisAgent
from src.agents.base import AgentConfig


class TestIndustryAnalysisAgent:
    @pytest.fixture
    def config(self):
        return AgentConfig(
            name="industry", stream_key="tasks:industry", consumer_group="industry_group"
        )

    @pytest.fixture
    def agent(self, config):
        with patch("src.agents.industry.DuckDBClient"):
            return IndustryAnalysisAgent(config)

    @pytest.mark.asyncio
    async def test_get_industry_classification(self, agent):
        """测试行业分类映射"""
        agent.duckdb.execute = Mock(return_value=[{"industry": "白酒", "level": 1}])

        result = await agent.execute({"type": "get_industry", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_constituents(self, agent):
        """测试获取成分股列表"""
        agent.duckdb.execute = Mock(
            return_value=[
                {"ticker": "600519", "name": "贵州茅台"},
                {"ticker": "000858", "name": "五粮液"},
            ]
        )

        result = await agent.execute({"type": "get_constituents", "industry": "白酒"})

        assert result["status"] == "success"
        assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_calculate_trend(self, agent):
        """测试趋势计算"""
        mock_data = [
            {"trade_date": "2024-01-02", "close": 100},
            {"trade_date": "2024-01-03", "close": 105},
            {"trade_date": "2024-01-04", "close": 110},
        ]
        agent.duckdb.execute = Mock(return_value=mock_data)

        result = await agent.execute({"type": "calculate_trend", "industry": "白酒"})

        assert result["status"] == "success"
        assert "trend" in result

    @pytest.mark.asyncio
    async def test_industry_rotation_analysis(self, agent):
        """测试行业轮动周期分析"""
        agent.duckdb.execute = Mock(
            return_value=[
                {"industry": "白酒", "return_1m": 5.2},
                {"industry": "新能源", "return_1m": -2.1},
            ]
        )

        result = await agent.execute({"type": "industry_rotation"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_portfolio_analysis(self, agent):
        """测试持仓性价比分析"""
        agent.duckdb.execute = Mock(
            return_value=[{"ticker": "600519", "position_ratio": 0.3, "pe": 35, "roe": 0.25}]
        )

        result = await agent.execute({"type": "portfolio_analysis", "tickers": ["600519"]})

        assert result["status"] == "success"
