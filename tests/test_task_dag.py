"""DAG任务拆解测试"""
import pytest
from src.orchestrator.task_dag import TaskType, DAGBuilder, TASK_DEPENDENCIES, TaskNode


class TestTaskType:
    """TaskType 枚举测试"""

    def test_task_type_values(self):
        """测试任务类型值"""
        assert TaskType.DATA_COLLECTION.value == "data_collection"
        assert TaskType.FUNDAMENTAL.value == "fundamental"
        assert TaskType.VALUATION.value == "valuation"
        assert TaskType.REPORT.value == "report"


class TestTaskDependencies:
    """TASK_DEPENDENCIES 测试"""

    def test_dependencies_structure(self):
        """测试依赖结构"""
        assert TaskType.FUNDAMENTAL in TASK_DEPENDENCIES
        assert TaskType.DATA_COLLECTION in TASK_DEPENDENCIES[TaskType.FUNDAMENTAL]

    def test_data_collection_no_dependencies(self):
        """测试数据收集任务无依赖"""
        assert TASK_DEPENDENCIES[TaskType.DATA_COLLECTION] == []

    def test_report_depends_on_all(self):
        """测试报告任务依赖"""
        deps = TASK_DEPENDENCIES[TaskType.REPORT]
        assert TaskType.THINKING in deps


class TestDAGBuilder:
    """DAGBuilder 测试"""

    def test_parse_returns_trace_id(self):
        """测试解析返回 trace_id"""
        builder = DAGBuilder()
        result = builder.parse("分析股票")

        assert "trace_id" in result
        assert "user_input" in result
        assert "tasks" in result

    def test_parse_fundamental_analysis(self):
        """测试基本面分析"""
        builder = DAGBuilder()
        result = builder.parse("分析基本面")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.DATA_COLLECTION in task_types
        assert TaskType.FUNDAMENTAL in task_types

    def test_parse_with_valuation(self):
        """测试带估值分析"""
        builder = DAGBuilder()
        result = builder.parse("分析基本面和估值")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.VALUATION in task_types

    def test_parse_with_sentiment(self):
        """测试带舆情分析"""
        builder = DAGBuilder()
        result = builder.parse("分析舆情")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.SENTIMENT in task_types

    def test_parse_with_catalyst(self):
        """测试带催化剂分析"""
        builder = DAGBuilder()
        result = builder.parse("分析催化剂")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.CATALYST in task_types

    def test_parse_with_industry(self):
        """测试带行业分析"""
        builder = DAGBuilder()
        result = builder.parse("分析行业")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.INDUSTRY in task_types

    def test_parse_always_has_report(self):
        """测试始终包含报告任务"""
        builder = DAGBuilder()
        result = builder.parse("分析")

        task_types = [t["type"] for t in result["tasks"]]

        assert TaskType.REPORT in task_types

    def test_parse_default_fallback(self):
        """测试默认输入"""
        builder = DAGBuilder()
        result = builder.parse("")

        assert len(result["tasks"]) > 0


class TestTaskNode:
    """TaskNode 测试"""

    def test_create_task_node(self):
        """测试创建任务节点"""
        node = TaskNode(task_id="test_1", type=TaskType.DATA_COLLECTION, depends_on=["task_0"])

        assert node.task_id == "test_1"
        assert node.type == TaskType.DATA_COLLECTION
        assert node.depends_on == ["task_0"]
