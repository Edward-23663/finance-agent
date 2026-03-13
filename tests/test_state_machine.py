"""状态机测试"""
import pytest
from unittest.mock import MagicMock, patch
from src.orchestrator.state_machine import TaskState, TaskStateMachine, VALID_TRANSITIONS


class TestTaskState:
    """TaskState 枚举测试"""

    def test_task_state_values(self):
        """测试状态值"""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.RUNNING.value == "running"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.FAILED.value == "failed"
        assert TaskState.PARTIAL_SUCCESS.value == "partial_success"


class TestTaskStateMachine:
    """TaskStateMachine 测试"""

    def test_valid_transitions(self):
        """测试有效转换"""
        assert TaskStateMachine.is_valid_transition(TaskState.PENDING, TaskState.RUNNING) is True
        assert TaskStateMachine.is_valid_transition(TaskState.PENDING, TaskState.FAILED) is True
        assert TaskStateMachine.is_valid_transition(TaskState.PENDING, TaskState.COMPLETED) is False

    def test_invalid_transitions(self):
        """测试无效转换"""
        assert TaskStateMachine.is_valid_transition(TaskState.COMPLETED, TaskState.PENDING) is False
        assert TaskStateMachine.is_valid_transition(TaskState.RUNNING, TaskState.PENDING) is False
        assert (
            TaskStateMachine.is_valid_transition(TaskState.PENDING, TaskState.PARTIAL_SUCCESS)
            is False
        )

    def test_get_state_from_redis(self):
        """测试从 Redis 获取状态"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "running"

        machine = TaskStateMachine(mock_redis)
        state = machine.get_state("test_trace_id")

        assert state == TaskState.RUNNING
        mock_redis.get.assert_called_once_with("task:test_trace_id:status")

    def test_get_state_default_pending(self):
        """测试默认状态为 PENDING"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        machine = TaskStateMachine(mock_redis)
        state = machine.get_state("test_trace_id")

        assert state == TaskState.PENDING

    def test_set_state(self):
        """测试设置状态"""
        mock_redis = MagicMock()
        machine = TaskStateMachine(mock_redis)

        machine.set_state("test_trace_id", TaskState.RUNNING)

        mock_redis.set.assert_called()
        call_args = mock_redis.set.call_args_list[0][0]
        assert call_args[0] == "task:test_trace_id:status"
        assert call_args[1] == "running"

    def test_set_state_with_error(self):
        """测试设置错误状态"""
        mock_redis = MagicMock()
        machine = TaskStateMachine(mock_redis)

        machine.set_state("test_trace_id", TaskState.FAILED, "Error message")

        assert mock_redis.set.call_count == 3

    def test_transition_success(self):
        """测试成功状态转换"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "pending"

        machine = TaskStateMachine(mock_redis)
        result = machine.transition("test_trace_id", TaskState.RUNNING)

        assert result is True

    def test_transition_invalid(self):
        """测试无效状态转换"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "completed"

        machine = TaskStateMachine(mock_redis)
        result = machine.transition("test_trace_id", TaskState.PENDING)

        assert result is False
