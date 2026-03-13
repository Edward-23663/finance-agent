"""DAG任务拆解模块"""
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from src.orchestrator.trace import generate_trace_id


class TaskType(str, Enum):
    """任务类型枚举"""

    DATA_COLLECTION = "data_collection"
    FUNDAMENTAL = "fundamental"
    VALUATION = "valuation"
    SENTIMENT = "sentiment"
    CATALYST = "catalyst"
    INDUSTRY = "industry"
    THINKING = "thinking"
    REPORT = "report"


@dataclass
class TaskNode:
    """任务节点"""

    task_id: str
    type: TaskType
    depends_on: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


TASK_DEPENDENCIES = {
    TaskType.DATA_COLLECTION: [],
    TaskType.FUNDAMENTAL: [TaskType.DATA_COLLECTION],
    TaskType.VALUATION: [TaskType.FUNDAMENTAL],
    TaskType.SENTIMENT: [TaskType.DATA_COLLECTION],
    TaskType.CATALYST: [TaskType.DATA_COLLECTION],
    TaskType.INDUSTRY: [TaskType.DATA_COLLECTION],
    TaskType.THINKING: [TaskType.FUNDAMENTAL, TaskType.VALUATION],
    TaskType.REPORT: [TaskType.THINKING],
}


class DAGBuilder:
    """DAG任务拆解构建器"""

    def __init__(self):
        self.task_counter = 0

    def parse(self, user_input: str) -> Dict[str, Any]:
        """解析用户输入为任务DAG"""
        trace_id = generate_trace_id()

        tasks = self._analyze_input(user_input)

        return {"trace_id": trace_id, "user_input": user_input, "tasks": tasks}

    def _analyze_input(self, user_input: str) -> List[Dict[str, Any]]:
        """分析用户输入，确定需要的任务类型"""
        tasks = []
        input_lower = user_input.lower()

        if "分析" in user_input or "基本面" in input_lower:
            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.DATA_COLLECTION,
                    "depends_on": [],
                }
            )

            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.FUNDAMENTAL,
                    "depends_on": [f"task_{self.task_counter - 1}"],
                }
            )

        if "估值" in input_lower:
            self.task_counter += 1
            fundamental_task = f"task_{self.task_counter - 1}" if tasks else "task_1"
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.VALUATION,
                    "depends_on": [fundamental_task],
                }
            )

        if "舆情" in input_lower or " sentiment" in input_lower:
            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.SENTIMENT,
                    "depends_on": [],
                }
            )

        if "催化剂" in input_lower or "catalyst" in input_lower:
            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.CATALYST,
                    "depends_on": [],
                }
            )

        if "行业" in input_lower or "industry" in input_lower:
            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.INDUSTRY,
                    "depends_on": [],
                }
            )

        if not tasks:
            self.task_counter += 1
            tasks.append(
                {
                    "task_id": f"task_{self.task_counter}",
                    "type": TaskType.DATA_COLLECTION,
                    "depends_on": [],
                }
            )

        self.task_counter += 1
        tasks.append(
            {
                "task_id": f"task_{self.task_counter}",
                "type": TaskType.REPORT,
                "depends_on": [t["task_id"] for t in tasks if t["type"] != TaskType.REPORT],
            }
        )

        return tasks
