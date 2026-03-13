"""主编排器核心"""
from typing import Dict, Any, Optional, List
from src.orchestrator.task_dag import DAGBuilder, TaskNode
from src.orchestrator.state_machine import TaskState, TaskStateMachine
from src.orchestrator.trace import TraceManager, generate_trace_id
from src.orchestrator.retry import RetryPolicy
from src.communication.streams import StreamManager
from src.communication.redis_client import RedisClient


class MainOrchestrator:
    """主编排器"""

    def __init__(self):
        self.redis = RedisClient()
        self.streams = StreamManager(self.redis)
        self.state_machine = TaskStateMachine(self.redis)
        self.trace_manager = TraceManager(self.redis)
        self.retry_policy = RetryPolicy()
        self.dag_builder = DAGBuilder()

    def parse_task(self, user_input: str) -> Dict[str, Any]:
        """解析用户任务"""
        return self.dag_builder.parse(user_input)

    def create_task(self, user_input: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建任务"""
        result = self.parse_task(user_input)
        trace_id = result.get("trace_id", generate_trace_id())

        self.trace_manager.create_trace(trace_id, metadata)
        self.state_machine.set_state(trace_id, TaskState.PENDING)

        return trace_id

    def execute_task(self, trace_id: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行任务"""
        self.state_machine.transition(trace_id, TaskState.RUNNING)

        results = {}
        for task in tasks:
            task_id = task.get("task_id")
            task_type = task.get("type")

            span_id = self.trace_manager.add_span(trace_id, task_id or task_type, task_type)

            try:
                result = self._execute_single_task(task)
                results[task_id] = {"status": "success", "data": result}
                self.trace_manager.end_span(span_id, result)
            except Exception as e:
                results[task_id] = {"status": "failed", "error": str(e)}
                self.trace_manager.end_span(span_id, {"error": str(e)})

        failed_count = sum(1 for r in results.values() if r["status"] == "failed")
        if failed_count == 0:
            self.state_machine.transition(trace_id, TaskState.COMPLETED)
        elif failed_count < len(results):
            self.state_machine.transition(trace_id, TaskState.PARTIAL_SUCCESS)
        else:
            self.state_machine.transition(trace_id, TaskState.FAILED)

        return results

    def _execute_single_task(self, task: Dict[str, Any]) -> Any:
        """执行单个任务"""
        task_type = task.get("type")
        return {"task_type": task_type, "message": "Task executed"}

    def get_task_status(self, trace_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        state = self.state_machine.get_state(trace_id)
        trace = self.trace_manager.get_trace(trace_id)
        spans = self.trace_manager.list_spans(trace_id)

        return {
            "trace_id": trace_id,
            "state": state.value if state else "unknown",
            "trace": trace,
            "spans": spans,
        }
