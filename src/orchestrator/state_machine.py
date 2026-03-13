"""任务状态机"""
from enum import Enum
from typing import Set, Optional
from datetime import datetime
from src.communication.redis_client import RedisClient


class TaskState(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


VALID_TRANSITIONS: dict[TaskState, Set[TaskState]] = {
    TaskState.PENDING: {TaskState.RUNNING, TaskState.FAILED},
    TaskState.RUNNING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.PARTIAL_SUCCESS},
    TaskState.COMPLETED: set(),
    TaskState.FAILED: {TaskState.PENDING},
    TaskState.PARTIAL_SUCCESS: {TaskState.COMPLETED, TaskState.FAILED, TaskState.PENDING},
}


class TaskStateMachine:
    """任务状态机"""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()

    @staticmethod
    def is_valid_transition(from_state: TaskState, to_state: TaskState) -> bool:
        """检查状态转换是否有效"""
        return to_state in VALID_TRANSITIONS.get(from_state, set())

    def get_state(self, trace_id: str) -> TaskState:
        """获取任务状态"""
        key = f"task:{trace_id}:status"
        state = self.redis.get(key)
        return TaskState(state) if state else TaskState.PENDING

    def set_state(self, trace_id: str, state: TaskState, error_message: Optional[str] = None):
        """设置任务状态"""
        key = f"task:{trace_id}:status"
        self.redis.set(key, state.value)

        timestamp_key = f"task:{trace_id}:updated_at"
        self.redis.set(timestamp_key, datetime.utcnow().isoformat())

        if error_message:
            error_key = f"task:{trace_id}:error"
            self.redis.set(error_key, error_message)

    def transition(
        self, trace_id: str, to_state: TaskState, error_message: Optional[str] = None
    ) -> bool:
        """执行状态转换"""
        from_state = self.get_state(trace_id)

        if not self.is_valid_transition(from_state, to_state):
            return False

        self.set_state(trace_id, to_state, error_message)

        if to_state in {TaskState.COMPLETED, TaskState.FAILED, TaskState.PARTIAL_SUCCESS}:
            completed_key = f"task:{trace_id}:completed_at"
            self.redis.set(completed_key, datetime.utcnow().isoformat())

        return True
