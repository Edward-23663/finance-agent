"""DataCollectionAgent测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.data_collection import DataCollectionAgent
from src.agents.base import AgentConfig


class TestDataCollectionAgent:
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="data_collection",
            stream_key="tasks:data_collection",
            consumer_group="agents",
        )

    @pytest.fixture
    def agent(self, agent_config):
        with patch("src.agents.base.RedisClient"), patch("src.agents.base.StreamManager"), patch(
            "src.agents.base.TaskStateMachine"
        ), patch("src.agents.data_collection.DataWriter"):
            agent = DataCollectionAgent(agent_config)
            return agent

    def test_agent_initialization(self, agent):
        assert agent.config.name == "data_collection"
        assert agent.config.stream_key == "tasks:data_collection"
        assert "tushare" in agent.source_priority
        assert "akshare" in agent.source_priority
        assert "yfinance" in agent.source_priority

    @pytest.mark.asyncio
    async def test_execute_collect_price(self, agent):
        task_data = {
            "type": "collect_price",
            "ticker": "600519",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }

        with patch.object(agent, "_collect_price_data", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = {"status": "success", "rows": 100}
            result = await agent.execute(task_data)

            assert result["status"] == "success"
            mock_collect.assert_called_once_with("600519", "2024-01-01", "2024-12-31")

    @pytest.mark.asyncio
    async def test_execute_collect_financial(self, agent):
        task_data = {
            "type": "collect_financial",
            "ticker": "600519",
        }

        with patch.object(agent, "_collect_financial_data", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = {"status": "success", "rows": 4}
            result = await agent.execute(task_data)

            assert result["status"] == "success"
            mock_collect.assert_called_once_with("600519")

    @pytest.mark.asyncio
    async def test_execute_unknown_type(self, agent):
        task_data = {
            "type": "unknown_type",
            "ticker": "600519",
        }

        with pytest.raises(ValueError, match="Unknown task type"):
            await agent.execute(task_data)
