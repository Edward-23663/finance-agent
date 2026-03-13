"""综合思维模型Agent测试"""
import pytest
from unittest.mock import Mock, patch
from src.agents.thinking import ThinkingAgent
from src.agents.base import AgentConfig


class TestThinkingAgent:
    @pytest.fixture
    def config(self):
        return AgentConfig(
            name="thinking", stream_key="tasks:thinking", consumer_group="thinking_group"
        )

    @pytest.fixture
    def agent(self, config):
        with patch("src.agents.thinking.LanceDBClient"):
            return ThinkingAgent(config)

    @pytest.mark.asyncio
    async def test_relative_theory_analysis(self, agent):
        """测试相对论分析因子提取"""
        result = await agent.execute({"type": "relative_theory", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_quantum_probability(self, agent):
        """测试量子概率模型"""
        result = await agent.execute({"type": "quantum_probability", "ticker": "600519"})

        assert result["status"] == "success"
        assert "probability" in result

    @pytest.mark.asyncio
    async def test_chaos_trend_fitting(self, agent):
        """测试混沌理论趋势拟合"""
        agent.lancedb.search = Mock(return_value=[{"close": 100}, {"close": 105}, {"close": 110}])

        result = await agent.execute({"type": "chaos_trend", "ticker": "600519"})

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_bayesian_validation(self, agent):
        """测试贝叶斯概率校验"""
        result = await agent.execute(
            {
                "type": "bayesian_validation",
                "ticker": "600519",
                "prior": 0.5,
                "evidence": {"PE": 30},
            }
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_thinking_fusion(self, agent):
        """测试多思维模型结果融合"""
        result = await agent.execute({"type": "thinking_fusion", "ticker": "600519"})

        assert result["status"] == "success"
        assert "final_score" in result

    @pytest.mark.asyncio
    async def test_nonlinear_conclusion(self, agent):
        """测试非线性分析结论生成"""
        result = await agent.execute({"type": "nonlinear_conclusion", "ticker": "600519"})

        assert result["status"] == "success"
        assert "conclusion" in result
