"""Agent基类测试"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.agents.base import BaseAgent, AgentConfig


class TestAgentConfig:
    """AgentConfig 测试"""

    def test_create_agent_config(self):
        """测试创建 Agent 配置"""
        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        assert config.name == "test_agent"
        assert config.stream_key == "test_stream"
        assert config.consumer_group == "test_group"
        assert config.max_retries == 3

    def test_custom_max_retries(self):
        """测试自定义重试次数"""
        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group", max_retries=5
        )

        assert config.max_retries == 5


class MockAgent(BaseAgent):
    """用于测试的 Mock Agent"""

    async def execute(self, task_data):
        return f"executed: {task_data.get('trace_id')}"


class TestBaseAgent:
    """BaseAgent 测试"""

    @patch("src.agents.base.RedisClient")
    @patch("src.agents.base.StreamManager")
    @patch("src.agents.base.TaskStateMachine")
    def test_agent_initialization(self, mock_sm, mock_stream, mock_redis):
        """测试 Agent 初始化"""
        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        agent = MockAgent(config)

        assert agent.config == config
        assert agent._running is False

    @pytest.mark.asyncio
    @patch("src.agents.base.RedisClient")
    @patch("src.agents.base.StreamManager")
    @patch("src.agents.base.TaskStateMachine")
    async def test_start_agent(self, mock_sm, mock_stream, mock_redis):
        """测试启动 Agent"""
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        agent = MockAgent(config)
        agent._running = True

        assert agent._running is True

    @pytest.mark.asyncio
    @patch("src.agents.base.RedisClient")
    @patch("src.agents.base.StreamManager")
    @patch("src.agents.base.TaskStateMachine")
    async def test_stop_agent(self, mock_sm, mock_stream, mock_redis):
        """测试停止 Agent"""
        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        agent = MockAgent(config)
        agent._running = True

        await agent.stop()

        assert agent._running is False

    @pytest.mark.asyncio
    @patch("src.agents.base.RedisClient")
    @patch("src.agents.base.StreamManager")
    @patch("src.agents.base.TaskStateMachine")
    async def test_process_message_success(self, mock_sm, mock_stream, mock_redis):
        """测试成功处理消息"""
        mock_state_machine = MagicMock()
        mock_state_machine.transition.return_value = True
        mock_sm.return_value = mock_state_machine

        mock_streams_instance = MagicMock()
        mock_stream.return_value = mock_streams_instance

        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        agent = MockAgent(config)
        agent.state_machine = mock_state_machine
        agent.streams = mock_streams_instance

        message = {"id": "msg_123", "data": {"trace_id": "trace_123", "type": "data_collection"}}

        await agent._process_message(message)

        assert mock_state_machine.transition.call_count == 2

    @pytest.mark.asyncio
    @patch("src.agents.base.RedisClient")
    @patch("src.agents.base.StreamManager")
    @patch("src.agents.base.TaskStateMachine")
    async def test_process_message_failure(self, mock_sm, mock_stream, mock_redis):
        """测试处理消息失败"""
        mock_state_machine = MagicMock()
        mock_state_machine.transition.return_value = True
        mock_sm.return_value = mock_state_machine

        mock_streams_instance = MagicMock()
        mock_stream.return_value = mock_streams_instance

        config = AgentConfig(
            name="test_agent", stream_key="test_stream", consumer_group="test_group"
        )

        class FailingAgent(BaseAgent):
            async def execute(self, task_data):
                raise Exception("Task failed")

        agent = FailingAgent(config)
        agent.state_machine = mock_state_machine
        agent.streams = mock_streams_instance

        message = {"id": "msg_123", "data": {"trace_id": "trace_123", "type": "data_collection"}}

        await agent._process_message(message)

        assert mock_state_machine.transition.call_count == 2
