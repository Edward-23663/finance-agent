"""基本面分析Agent测试"""
import pytest
from unittest.mock import patch, AsyncMock
from src.agents.fundamental import FundamentalAnalysisAgent
from src.agents.base import AgentConfig


class TestFundamentalAnalysisAgent:
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="fundamental_analysis",
            stream_key="tasks:fundamental_analysis",
            consumer_group="agents",
        )

    @pytest.fixture
    def agent(self, agent_config):
        with patch("src.agents.base.RedisClient"), patch("src.agents.base.StreamManager"), patch(
            "src.agents.base.TaskStateMachine"
        ), patch("src.agents.fundamental.DuckDBClient"):
            return FundamentalAnalysisAgent(agent_config)

    def test_agent_initialization(self, agent):
        assert agent.config.name == "fundamental_analysis"

    @pytest.mark.asyncio
    async def test_analyze_financial_health(self, agent):
        task_data = {
            "type": "analyze_financial_health",
            "ticker": "600519",
        }

        with patch.object(
            agent, "_calculate_financial_health", new_callable=AsyncMock
        ) as mock_calc:
            mock_calc.return_value = {
                "score": 85,
                "roe": 0.32,
                "current_ratio": 2.5,
                "debt_ratio": 0.3,
            }
            result = await agent.execute(task_data)

            assert result["score"] == 85
            mock_calc.assert_called_once_with("600519")

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        task_data = {
            "type": "unknown_type",
            "ticker": "600519",
        }

        with pytest.raises(ValueError, match="Unknown task type"):
            await agent.execute(task_data)
