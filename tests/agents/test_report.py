"""报告生成Agent测试"""
import pytest
from unittest.mock import patch, AsyncMock
from src.agents.report import ReportGenerationAgent
from src.agents.base import AgentConfig


class TestReportGenerationAgent:
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="report_generation",
            stream_key="tasks:report_generation",
            consumer_group="agents",
        )

    @pytest.fixture
    def agent(self, agent_config):
        with patch("src.agents.base.RedisClient"), patch("src.agents.base.StreamManager"), patch(
            "src.agents.base.TaskStateMachine"
        ), patch("src.agents.report.DuckDBClient"):
            return ReportGenerationAgent(agent_config)

    def test_agent_initialization(self, agent):
        assert agent.config.name == "report_generation"

    @pytest.mark.asyncio
    async def test_generate_report(self, agent):
        task_data = {
            "type": "generate_report",
            "ticker": "600519",
        }

        with patch.object(agent, "_generate_full_report", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {"status": "success", "report": "Test report"}
            result = await agent.execute(task_data)

            assert "report" in result

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        task_data = {
            "type": "unknown_type",
            "ticker": "600519",
        }

        with pytest.raises(ValueError, match="Unknown task type"):
            await agent.execute(task_data)
