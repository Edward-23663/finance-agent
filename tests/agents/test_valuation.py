"""估值Agent测试"""
import pytest
from unittest.mock import patch, AsyncMock
from src.agents.valuation import ValuationAgent
from src.agents.base import AgentConfig


class TestValuationAgent:
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="valuation",
            stream_key="tasks:valuation",
            consumer_group="agents",
        )

    @pytest.fixture
    def agent(self, agent_config):
        with patch("src.agents.base.RedisClient"), patch("src.agents.base.StreamManager"), patch(
            "src.agents.base.TaskStateMachine"
        ), patch("src.agents.valuation.DuckDBClient"), patch("src.agents.valuation.DataWriter"):
            return ValuationAgent(agent_config)

    def test_agent_initialization(self, agent):
        assert agent.config.name == "valuation"

    @pytest.mark.asyncio
    async def test_calculate_pe(self, agent):
        task_data = {
            "type": "calculate_pe",
            "ticker": "600519",
        }

        with patch.object(agent, "_calculate_pe", new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {"pe": 25.5, "status": "success"}
            result = await agent.execute(task_data)

            assert result["pe"] == 25.5

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        task_data = {
            "type": "unknown_type",
            "ticker": "600519",
        }

        with pytest.raises(ValueError, match="Unknown task type"):
            await agent.execute(task_data)
