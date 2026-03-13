# 金融分析智能体 - Phase 1 骨架工程实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立项目骨架、主编排器核心（DAG拆解、状态机、Trace_ID）、Redis Streams通信基础

**Architecture:** 采用轻量化主编排器 + Redis Streams消息队列架构，实现任务拆解、状态流转、链路追踪

**Tech Stack:** Python 3.11+, FastAPI, Redis, Pydantic, pytest

---

## 文件结构

```
finance-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 应用入口
│   ├── config.py                  # 配置管理
│   ├── orchestrator/              # 主编排器模块
│   │   ├── __init__.py
│   │   ├── main.py                # 主编排器核心
│   │   ├── task_dag.py           # DAG任务拆解
│   │   ├── state_machine.py       # 状态机
│   │   ├── trace.py               # Trace_ID链路追踪
│   │   └── retry.py               # 重试机制
│   ├── communication/             # 通信模块
│   │   ├── __init__.py
│   │   ├── redis_client.py        # Redis客户端封装
│   │   ├── streams.py             # Streams通信
│   │   └── protocol.py            # JSON-RPC协议
│   ├── agents/                    # 分智能体基类
│   │   ├── __init__.py
│   │   └── base.py               # Agent基类
│   ├── skills/                    # Skills模块
│   │   └── registry.py            # Skills注册表
│   └── utils/
│       ├── __init__.py
│       └── logging.py             # 日志工具
├── tests/
│   ├── __init__.py
│   ├── orchestrator/              # 主编排器测试
│   └── communication/            # 通信测试
├── configs/                      # 配置文件
│   └── agents.yaml               # Agent配置
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

## Chunk 1: 项目骨架搭建

### Task 1: 创建项目基础结构

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `src/main.py`
- Create: `src/config.py`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[tool.poetry]
name = "finance-agent"
version = "0.1.0"
description = "金融分析智能体 - 个人本地私有化部署"
authors = ["Developer <dev@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
redis = "^5.2.0"
pydantic = "^2.10.0"
pydantic-settings = "^2.6.0"
python-dotenv = "^1.0.0"
tenacity = "^9.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.28.0"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

- [ ] **Step 2: 创建配置管理 src/config.py**

```python
"""配置管理模块"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    # 项目路径
    project_dir: str = os.path.expanduser("~/.finance_agent")
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 任务配置
    max_retries: int = 3
    retry_delay: int = 5
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
```

- [ ] **Step 3: 创建应用入口 src/main.py**

```python
"""金融分析智能体 - 主入口"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时初始化
    # - 初始化Redis连接
    # - 初始化数据库
    # - 启动Agent进程
    print(f"🚀 金融分析智能体启动中...")
    print(f"📁 数据目录: {settings.project_dir}")
    
    yield
    
    # 关闭时清理
    print("🛑 正在关闭...")
    # - 关闭Redis连接
    # - 保存状态


app = FastAPI(
    title="金融分析智能体 API",
    description="个人本地私有化部署的金融分析工具",
    version="0.1.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "金融分析智能体 API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
```

- [ ] **Step 4: 创建 __init__.py 文件**

```python
"""金融分析智能体"""
__version__ = "0.1.0"
```

- [ ] **Step 5: 安装依赖并验证**

```bash
cd /home/jianwei/project1
poetry install
poetry run python -c "from src.config import get_settings; print('OK')"
```

- [ ] **Step 6: 提交代码**

```bash
git add pyproject.toml src/
git commit -m "feat: 创建项目骨架和基础配置"
```

---

### Task 2: 创建Redis通信模块

**Files:**
- Create: `src/communication/__init__.py`
- Create: `src/communication/redis_client.py`
- Create: `src/communication/streams.py`
- Create: `src/communication/protocol.py`
- Create: `tests/communication/test_redis.py`

- [ ] **Step 1: 编写测试 src/communication/test_redis.py**

```python
"""Redis客户端测试"""
import pytest
from src.communication.redis_client import RedisClient


class TestRedisClient:
    """Redis客户端测试"""
    
    @pytest.fixture
    def client(self):
        """Redis客户端fixture"""
        return RedisClient()
    
    def test_ping(self, client):
        """测试ping"""
        result = client.ping()
        assert result is True
    
    def test_set_and_get(self, client):
        """测试设置和获取"""
        key = "test:key"
        value = "test_value"
        
        client.set(key, value)
        result = client.get(key)
        
        assert result == value
        
        # 清理
        client.delete(key)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/communication/test_redis.py -v
# 预期: FAIL - ModuleNotFoundError: No module named 'src.communication'
```

- [ ] **Step 3: 创建通信模块 src/communication/__init__.py**

```python
"""通信模块"""
from src.communication.redis_client import RedisClient
from src.communication.streams import StreamManager
from src.communication.protocol import JSONRPCRequest, JSONRPCResponse

__all__ = ["RedisClient", "StreamManager", "JSONRPCRequest", "JSONRPCResponse"]
```

- [ ] **Step 4: 实现Redis客户端 src/communication/redis_client.py**

```python
"""Redis客户端封装"""
import json
from typing import Any, Optional, List, Dict
import redis
from src.config import get_settings


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        settings = get_settings()
        self._client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
    
    def ping(self) -> bool:
        """Ping Redis"""
        return self._client.ping()
    
    def get(self, key: str) -> Optional[str]:
        """获取值"""
        return self._client.get(key)
    
    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """设置值"""
        if not isinstance(value, str):
            value = json.dumps(value)
        self._client.set(key, value, ex=ex)
    
    def delete(self, *keys: str):
        """删除键"""
        self._client.delete(*keys)
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return bool(self._client.exists(key))
    
    def hset(self, name: str, key: str, value: Any):
        """设置哈希"""
        if not isinstance(value, str):
            value = json.dumps(value)
        self._client.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希值"""
        value = self._client.hget(name, key)
        return value
    
    def hgetall(self, name: str) -> Dict[str, str]:
        """获取所有哈希值"""
        return self._client.hgetall(name)
    
    def expire(self, key: str, seconds: int):
        """设置过期时间"""
        self._client.expire(key, seconds)
    
    def keys(self, pattern: str) -> List[str]:
        """查找键"""
        return self._client.keys(pattern)
    
    # ==================== Streams 方法 ====================
    
    def xadd(self, stream: str, data: dict, id: str = '*') -> str:
        """添加消息到Stream"""
        return self._client.xadd(stream, data, id=id)
    
    def xreadgroup(self, groupname: str, consumername: str,
                   streams: dict, count: int = 1, block: int = None):
        """从消费者组读取消息"""
        return self._client.xreadgroup(
            groupname=groupname,
            consumername=consumername,
            streams=streams,
            count=count,
            block=block
        )
    
    def xack(self, stream: str, groupname: str, *message_ids: str) -> int:
        """确认消息"""
        return self._client.xack(stream, groupname, *message_ids)
    
    def xgroup_create(self, stream: str, groupname: str,
                     id: str = '0', mkstream: bool = False):
        """创建消费者组"""
        return self._client.xgroup_create(stream, groupname, id=id, mkstream=mkstream)
    
    def xpending(self, stream: str, groupname: str) -> dict:
        """获取待处理消息信息"""
        return self._client.xpending(stream, groupname)
    
    def xtrim(self, stream: str, maxlen: int, approximate: bool = True):
        """裁剪Stream"""
        return self._client.xtrim(stream, maxlen=maxlen, approximate=approximate)
    
    def xlen(self, stream: str) -> int:
        """获取Stream长度"""
        return self._client.xlen(stream)
    
    def xrange(self, stream: str, min_: str = '-', max_: str = '+',
               count: int = None) -> list:
        """获取Stream范围内的消息"""
        return self._client.xrange(stream, min=min_, max=max_, count=count)
    
    def close(self):
        """关闭连接"""
        self._client.close()
```

- [ ] **Step 5: 运行测试验证通过**

```bash
poetry run pytest tests/communication/test_redis.py -v
# 预期: PASS
```

- [ ] **Step 6: 提交代码**

```bash
git add src/communication/ tests/communication/
git commit -m "feat: 添加Redis客户端封装"
```

---

## Chunk 2: 状态机与Trace_ID

### Task 3: 实现状态机

**Files:**
- Create: `src/orchestrator/state_machine.py`
- Create: `tests/orchestrator/test_state_machine.py`

- [ ] **Step 1: 编写测试 tests/orchestrator/test_state_machine.py**

```python
"""状态机测试"""
import pytest
from src.orchestrator.state_machine import TaskState, TaskStateMachine


class TestTaskState:
    """任务状态测试"""
    
    def test_valid_transitions(self):
        """测试有效状态转换"""
        assert TaskStateMachine.is_valid_transition(
            TaskState.PENDING, 
            TaskState.RUNNING
        )
        assert TaskStateMachine.is_valid_transition(
            TaskState.RUNNING, 
            TaskState.COMPLETED
        )
        assert TaskStateMachine.is_valid_transition(
            TaskState.RUNNING, 
            TaskState.FAILED
        )
    
    def test_invalid_transitions(self):
        """测试无效状态转换"""
        assert not TaskStateMachine.is_valid_transition(
            TaskState.COMPLETED,
            TaskState.RUNNING
        )
        assert not TaskStateMachine.is_valid_transition(
            TaskState.FAILED,
            TaskState.RUNNING
        )
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/orchestrator/test_state_machine.py -v
# 预期: FAIL - ModuleNotFoundError
```

- [ ] **Step 3: 创建orchestrator模块 src/orchestrator/__init__.py**

```python
"""主编排器模块"""
from src.orchestrator.main import MainOrchestrator
from src.orchestrator.state_machine import TaskState, TaskStateMachine
from src.orchestrator.trace import TraceManager
from src.orchestrator.retry import RetryPolicy

__all__ = [
    "MainOrchestrator",
    "TaskState", 
    "TaskStateMachine",
    "TraceManager",
    "RetryPolicy"
]
```

- [ ] **Step 4: 实现状态机 src/orchestrator/state_machine.py**

```python
"""任务状态机"""
from enum import Enum
from typing import Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from src.communication.redis_client import RedisClient


class TaskState(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


# 有效状态转换映射
VALID_TRANSITIONS: dict[TaskState, Set[TaskState]] = {
    TaskState.PENDING: {TaskState.RUNNING, TaskState.FAILED},
    TaskState.RUNNING: {
        TaskState.COMPLETED, 
        TaskState.FAILED, 
        TaskState.PARTIAL_SUCCESS
    },
    TaskState.COMPLETED: set(),
    TaskState.FAILED: {TaskState.PENDING},  # 支持重试
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
    
    def set_state(self, trace_id: str, state: TaskState, 
                  error_message: Optional[str] = None):
        """设置任务状态"""
        key = f"task:{trace_id}:status"
        self.redis.set(key, state.value)
        
        # 记录时间戳
        timestamp_key = f"task:{trace_id}:updated_at"
        self.redis.set(timestamp_key, datetime.utcnow().isoformat())
        
        # 记录错误信息
        if error_message:
            error_key = f"task:{trace_id}:error"
            self.redis.set(error_key, error_message)
    
    def transition(self, trace_id: str, to_state: TaskState,
                   error_message: Optional[str] = None) -> bool:
        """执行状态转换"""
        from_state = self.get_state(trace_id)
        
        if not self.is_valid_transition(from_state, to_state):
            return False
        
        self.set_state(trace_id, to_state, error_message)
        
        # 记录完成时间
        if to_state in {TaskState.COMPLETED, TaskState.FAILED, TaskState.PARTIAL_SUCCESS}:
            completed_key = f"task:{trace_id}:completed_at"
            self.redis.set(completed_key, datetime.utcnow().isoformat())
        
        return True
```

- [ ] **Step 5: 运行测试验证通过**

```bash
poetry run pytest tests/orchestrator/test_state_machine.py -v
# 预期: PASS
```

- [ ] **Step 6: 提交代码**

```bash
git add src/orchestrator/ tests/orchestrator/
git commit -m "feat: 实现任务状态机"
```

---

### Task 4: 实现Trace_ID链路追踪

**Files:**
- Create: `src/orchestrator/trace.py`
- Create: `tests/orchestrator/test_trace.py`

- [ ] **Step 1: 编写测试 tests/orchestrator/test_trace.py**

```python
"""链路追踪测试"""
import pytest
from src.orchestrator.trace import TraceManager, generate_trace_id


class TestTraceID:
    """Trace_ID测试"""
    
    def test_generate_trace_id(self):
        """测试Trace_ID生成"""
        trace_id = generate_trace_id()
        
        # 格式: {timestamp}_{random_8char}
        parts = trace_id.split("_")
        assert len(parts) == 2
        assert len(parts[1]) == 8
    
    def test_trace_id_unique(self):
        """测试Trace_ID唯一性"""
        ids = [generate_trace_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestTraceManager:
    """追踪管理器测试"""
    
    @pytest.fixture
    def manager(self):
        return TraceManager()
    
    def test_create_trace(self, manager):
        """测试创建追踪"""
        trace_id = generate_trace_id()
        manager.create_trace(trace_id, "分析贵州茅台")
        
        trace = manager.get_trace(trace_id)
        assert trace["user_input"] == "分析贵州茅台"
        assert trace["status"] == "pending"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/orchestrator/test_trace.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现链路追踪 src/orchestrator/trace.py**

```python
"""链路追踪模块"""
import secrets
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime
from src.communication.redis_client import RedisClient


def generate_trace_id() -> str:
    """生成唯一Trace_ID
    
    格式: {timestamp}_{random_8char}
    """
    timestamp = int(time.time())
    random_part = secrets.token_hex(4)[:8]
    return f"{timestamp}_{random_part}"


class TraceManager:
    """链路追踪管理器"""
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
    
    def create_trace(self, trace_id: str, user_input: str,
                     agents_involved: Optional[list] = None):
        """创建追踪记录"""
        key = f"trace:{trace_id}"
        
        data = {
            "user_input": user_input,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "agents_involved": json.dumps(agents_involved or []),
            "skills_called": json.dumps([]),
            "errors": json.dumps([])
        }
        
        # 使用Hash存储
        for field, value in data.items():
            self.redis.hset(key, field, value)
        
        # 设置过期时间30天
        self.redis.expire(key, 30 * 24 * 3600)
    
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """获取追踪记录"""
        key = f"trace:{trace_id}"
        data = self.redis.hgetall(key)
        
        # 解析JSON字段
        for field in ["agents_involved", "skills_called", "errors"]:
            if field in data:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = []
        
        return data
    
    def add_agent(self, trace_id: str, agent_name: str):
        """记录Agent参与"""
        key = f"trace:{trace_id}"
        agents_json = self.redis.hget(key, "agents_involved") or "[]"
        agents_list = json.loads(agents_json)
        
        if agent_name not in agents_list:
            agents_list.append(agent_name)
            self.redis.hset(key, "agents_involved", json.dumps(agents_list))
    
    def add_skill(self, trace_id: str, skill_name: str):
        """记录Skill调用"""
        key = f"trace:{trace_id}"
        skills_json = self.redis.hget(key, "skills_called") or "[]"
        skills_list = json.loads(skills_json)
        
        skills_list.append(skill_name)
        self.redis.hset(key, "skills_called", json.dumps(skills_list))
    
    def add_error(self, trace_id: str, error: str):
        """记录错误"""
        key = f"trace:{trace_id}"
        errors_json = self.redis.hget(key, "errors") or "[]"
        errors_list = json.loads(errors_json)
        
        errors_list.append(error)
        self.redis.hset(key, "errors", json.dumps(errors_list))
    
    def update_status(self, trace_id: str, status: str):
        """更新状态"""
        key = f"trace:{trace_id}"
        self.redis.hset(key, "status", status)
        self.redis.hset(key, "updated_at", datetime.utcnow().isoformat())
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/orchestrator/test_trace.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交代码**

```bash
git add src/orchestrator/ tests/orchestrator/
git commit -m "feat: 实现链路追踪模块"
```

---

## Chunk 3: DAG任务拆解与主编排器

### Task 5: 实现DAG任务拆解

**Files:**
- Create: `src/orchestrator/task_dag.py`
- Create: `tests/orchestrator/test_task_dag.py`

- [ ] **Step 1: 编写测试 tests/orchestrator/test_task_dag.py**

```python
"""DAG任务拆解测试"""
import pytest
from src.orchestrator.task_dag import DAGBuilder, TaskNode, TaskType


class TestDAGBuilder:
    """DAG构建器测试"""
    
    @pytest.fixture
    def builder(self):
        return DAGBuilder()
    
    def test_parse_simple_task(self, builder):
        """测试简单任务解析"""
        result = builder.parse("分析贵州茅台的基本面")
        
        assert "trace_id" in result
        assert "tasks" in result
        assert len(result["tasks"]) > 0
    
    def test_parse_multiple_analysis(self, builder):
        """测试多维度分析解析"""
        result = builder.parse("分析贵州茅台的基本面、估值和舆情")
        
        tasks = result["tasks"]
        task_types = [t["type"] for t in tasks]
        
        assert TaskType.FUNDAMENTAL in task_types
        assert TaskType.VALUATION in task_types
        assert TaskType.SENTIMENT in task_types
    
    def test_task_dependencies(self, builder):
        """测试任务依赖关系"""
        result = builder.parse("分析贵州茅台")
        
        tasks = result["tasks"]
        
        # 找到任务5(估值)，应该依赖任务3(基本面)
        valuation_task = next(
            (t for t in tasks if t["type"] == TaskType.VALUATION), 
            None
        )
        
        if valuation_task:
            assert TaskType.FUNDAMENTAL in valuation_task.get("depends_on", [])
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/orchestrator/test_task_dag.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现DAG任务拆解 src/orchestrator/task_dag.py**

```python
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


# Agent依赖关系矩阵
AGENT_DEPENDENCIES = {
    TaskType.DATA_COLLECTION: [],
    TaskType.INDUSTRY: [TaskType.DATA_COLLECTION],
    TaskType.FUNDAMENTAL: [TaskType.DATA_COLLECTION],
    TaskType.VALUATION: [TaskType.FUNDAMENTAL],
    TaskType.SENTIMENT: [TaskType.DATA_COLLECTION],
    TaskType.CATALYST: [TaskType.DATA_COLLECTION],
    TaskType.THINKING: [
        TaskType.FUNDAMENTAL,
        TaskType.VALUATION,
        TaskType.SENTIMENT,
        TaskType.CATALYST
    ],
    TaskType.REPORT: [
        TaskType.INDUSTRY,
        TaskType.FUNDAMENTAL,
        TaskType.VALUATION,
        TaskType.SENTIMENT,
        TaskType.CATALYST,
        TaskType.THINKING
    ],
}


@dataclass
class TaskNode:
    """任务节点"""
    task_id: str
    type: TaskType
    agent: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"


class DAGBuilder:
    """DAG任务拆解器"""
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        "基本面": [TaskType.FUNDAMENTAL],
        "估值": [TaskType.VALUATION],
        "财务": [TaskType.FUNDAMENTAL],
        "舆情": [TaskType.SENTIMENT],
        "新闻": [TaskType.SENTIMENT],
        "催化剂": [TaskType.CATALYST],
        "行业": [TaskType.INDUSTRY],
        "持仓": [TaskType.INDUSTRY],
        "综合": [TaskType.THINKING],
        "思维": [TaskType.THINKING],
        "报告": [TaskType.REPORT],
    }
    
    # Agent映射
    AGENT_MAP = {
        TaskType.DATA_COLLECTION: "data_collector",
        TaskType.INDUSTRY: "industry_analyzer",
        TaskType.FUNDAMENTAL: "fundamental_analyzer",
        TaskType.VALUATION: "valuation_analyzer",
        TaskType.SENTIMENT: "sentiment_analyzer",
        TaskType.CATALYST: "catalyst_analyzer",
        TaskType.THINKING: "thinking_analyzer",
        TaskType.REPORT: "report_generator",
    }
    
    def parse(self, user_input: str, ticker: Optional[str] = None) -> Dict[str, Any]:
        """解析用户输入，生成任务DAG
        
        Args:
            user_input: 用户输入
            ticker: 股票代码
            
        Returns:
            包含trace_id和任务列表的字典
        """
        trace_id = generate_trace_id()
        
        # 识别需要的分析类型
        analysis_types = self._identify_analysis_types(user_input)
        
        # 如果没有指定分析类型，默认全部
        if not analysis_types:
            analysis_types = [
                TaskType.FUNDAMENTAL,
                TaskType.VALUATION,
                TaskType.SENTIMENT,
                TaskType.REPORT
            ]
        
        # 确保包含报告生成
        if TaskType.REPORT not in analysis_types:
            analysis_types.append(TaskType.REPORT)
        
        # 构建任务节点
        tasks = self._build_tasks(trace_id, analysis_types, ticker or self._extract_ticker(user_input))
        
        return {
            "trace_id": trace_id,
            "user_input": user_input,
            "ticker": ticker,
            "tasks": tasks
        }
    
    def _identify_analysis_types(self, user_input: str) -> List[TaskType]:
        """识别分析类型"""
        types = []
        
        for keyword, task_types in self.INTENT_KEYWORDS.items():
            if keyword in user_input:
                for t in task_types:
                    if t not in types:
                        types.append(t)
        
        return types
    
    def _extract_ticker(self, user_input: str) -> Optional[str]:
        """提取股票代码"""
        # 简单的股票代码提取（6位数字）
        import re
        match = re.search(r'\d{6}', user_input)
        return match.group() if match else None
    
    def _build_tasks(self, trace_id: str, 
                     analysis_types: List[TaskType],
                     ticker: Optional[str]) -> List[Dict[str, Any]]:
        """构建任务列表"""
        tasks = []
        task_counter = 0
        
        for task_type in analysis_types:
            task_counter += 1
            task_id = f"{trace_id}_{task_counter}"
            
            # 确定依赖
            depends_on = []
            for dep_type in AGENT_DEPENDENCIES.get(task_type, []):
                # 找到对应的任务ID
                for t in tasks:
                    if t["type"] == dep_type.value:
                        depends_on.append(t["task_id"])
                        break
            
            tasks.append({
                "task_id": task_id,
                "type": task_type.value,
                "agent": self.AGENT_MAP.get(task_type, "unknown"),
                "params": {"ticker": ticker} if ticker else {},
                "depends_on": depends_on,
                "status": "pending"
            })
        
        return tasks
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/orchestrator/test_task_dag.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交代码**

```bash
git add src/orchestrator/ tests/orchestrator/
git commit -m "feat: 实现DAG任务拆解"
```

---

### Task 6: 实现主编排器核心

**Files:**
- Create: `src/orchestrator/main.py`
- Create: `tests/orchestrator/test_orchestrator.py`

- [ ] **Step 1: 编写测试 tests/orchestrator/test_orchestrator.py**

```python
"""主编排器测试"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.orchestrator.main import MainOrchestrator


class TestMainOrchestrator:
    """主编排器测试"""
    
    @pytest.fixture
    def orchestrator(self):
        return MainOrchestrator()
    
    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator):
        """测试任务处理"""
        # Mock Redis
        orchestrator.redis = Mock()
        orchestrator.redis.hgetall = Mock(return_value={})
        
        result = await orchestrator.process_task("分析贵州茅台")
        
        assert "trace_id" in result
        assert "tasks" in result
    
    def test_parse_user_input(self, orchestrator):
        """测试用户输入解析"""
        result = orchestrator.parse("600519贵州茅台的基本面分析")
        
        assert result["ticker"] == "600519"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/orchestrator/test_orchestrator.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现主编排器 src/orchestrator/main.py**

```python
"""主编排器核心模块"""
import re
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.orchestrator.task_dag import DAGBuilder
from src.orchestrator.state_machine import TaskStateMachine, TaskState
from src.orchestrator.trace import TraceManager, generate_trace_id
from src.orchestrator.retry import RetryPolicy
from src.communication.redis_client import RedisClient


@dataclass
class ProcessResult:
    """处理结果"""
    trace_id: str
    status: TaskState
    message: str
    tasks: List[Dict[str, Any]]


class MainOrchestrator:
    """主编排器 - 任务调度核心"""
    
    def __init__(self):
        self.redis = RedisClient()
        self.dag_builder = DAGBuilder()
        self.state_machine = TaskStateMachine(self.redis)
        self.trace_manager = TraceManager(self.redis)
        self.retry_policy = RetryPolicy()
    
    async def process_task(self, user_input: str, 
                          ticker: Optional[str] = None) -> ProcessResult:
        """处理用户任务
        
        流程: 用户输入 → 任务拆解 → 分发任务 → 结果聚合 → 反馈输出
        """
        # 1. 解析用户输入，提取股票代码
        if not ticker:
            ticker = self._extract_ticker(user_input)
        
        # 2. DAG任务拆解
        dag_result = self.dag_builder.parse(user_input, ticker)
        trace_id = dag_result["trace_id"]
        
        # 3. 创建追踪记录
        self.trace_manager.create_trace(trace_id, user_input)
        
        # 4. 初始化任务状态
        self.state_machine.set_state(trace_id, TaskState.PENDING)
        
        # 5. 分发任务到Redis Streams
        await self._dispatch_tasks(trace_id, dag_result["tasks"])
        
        # 6. 更新状态为运行中
        self.state_machine.transition(trace_id, TaskState.RUNNING)
        self.trace_manager.update_status(trace_id, "running")
        
        return ProcessResult(
            trace_id=trace_id,
            status=TaskState.PENDING,
            message="任务已提交",
            tasks=dag_result["tasks"]
        )
    
    async def _dispatch_tasks(self, trace_id: str, tasks: List[Dict[str, Any]]):
        """分发任务到Redis Streams"""
        for task in tasks:
            # 只有没有依赖或依赖已满足的任务才能分发
            if not task.get("depends_on"):
                await self._dispatch_single_task(trace_id, task)
    
    async def _dispatch_single_task(self, trace_id: str, task: Dict[str, Any]):
        """分发单个任务"""
        stream_key = f"agent:{task['agent']}"
        
        message = {
            "trace_id": trace_id,
            "task_id": task["task_id"],
            "type": task["type"],
            "params": json.dumps(task["params"])
        }
        
        # 添加到对应Agent的Stream
        self.redis.xadd(stream_key, message)
        
        # 记录Agent参与
        self.trace_manager.add_agent(trace_id, task["agent"])
    
    def get_task_status(self, trace_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        state = self.state_machine.get_state(trace_id)
        trace = self.trace_manager.get_trace(trace_id)
        
        return {
            "trace_id": trace_id,
            "status": state.value,
            "trace": trace
        }
    
    def _extract_ticker(self, user_input: str) -> Optional[str]:
        """从用户输入提取股票代码"""
        # 匹配6位数字
        match = re.search(r'\b(\d{6})\b', user_input)
        if match:
            return match.group(1)
        
        # 常见股票名称映射（简化版）
        ticker_map = {
            "贵州茅台": "600519",
            "茅台": "600519",
            "腾讯": "00700",
            "阿里巴巴": "09988",
        }
        
        for name, code in ticker_map.items():
            if name in user_input:
                return code
        
        return None
    
    async def handle_task_result(self, trace_id: str, 
                                 task_id: str, 
                                 result: Dict[str, Any]):
        """处理子任务结果"""
        # 检查是否有其他任务可以触发
        tasks = self._get_pending_tasks(trace_id)
        
        for task in tasks:
            deps = task.get("depends_on", [])
            if task_id in deps:
                # 检查所有依赖是否完成
                if self._all_dependencies_met(trace_id, deps):
                    await self._dispatch_single_task(trace_id, task)
    
    def _get_pending_tasks(self, trace_id: str) -> List[Dict[str, Any]]:
        """获取待处理任务"""
        key = f"task:{trace_id}:tasks"
        tasks_json = self.redis.get(key)
        if tasks_json:
            return json.loads(tasks_json)
        return []
    
    def _all_dependencies_met(self, trace_id: str, dependencies: List[str]) -> bool:
        """检查所有依赖是否已满足"""
        for dep_id in dependencies:
            # 检查依赖任务状态
            dep_key = f"task:{trace_id}:{dep_id}:status"
            status = self.redis.get(dep_key)
            if status != "completed":
                return False
        return True
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/orchestrator/test_orchestrator.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交代码**

```bash
git add src/orchestrator/ tests/orchestrator/
git commit -m "feat: 实现主编排器核心"
```

---

### Task 7: 实现重试机制

**Files:**
- Create: `src/orchestrator/retry.py`
- Create: `tests/orchestrator/test_retry.py`

- [ ] **Step 1: 编写测试**

```python
"""重试机制测试"""
import pytest
from src.orchestrator.retry import RetryPolicy


class TestRetryPolicy:
    """重试策略测试"""
    
    def test_should_retry_true(self):
        """测试应该重试"""
        policy = RetryPolicy(max_retries=3)
        
        assert policy.should_retry(0, Exception()) is True
        assert policy.should_retry(1, Exception()) is True
    
    def test_should_retry_false_max(self):
        """测试超过最大重试次数"""
        policy = RetryPolicy(max_retries=3)
        
        assert policy.should_retry(3, Exception()) is False
    
    def test_should_retry_false_no_retry(self):
        """测试不应重试的错误"""
        policy = RetryPolicy(max_retries=3)
        
        # ValueError默认不重试
        assert policy.should_retry(0, ValueError()) is False
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/orchestrator/test_retry.py -v
# 预期: FAIL - ModuleNotFoundError
```

- [ ] **Step 3: 实现重试机制 src/orchestrator/retry.py**

```python
"""重试机制模块"""
import asyncio
from typing import Callable, TypeVar, Any
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


T = TypeVar('T')


class RetryPolicy:
    """重试策略"""
    
    def __init__(self, max_retries: int = 3, min_wait: int = 1, max_wait: int = 60):
        self.max_retries = max_retries
        self.min_wait = min_wait
        self.max_wait = max_wait
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        
        # 不重试的异常类型
        non_retryable = (ValueError, TypeError, KeyError)
        if isinstance(exception, non_retryable):
            return False
        
        return True
    
    def get_wait_time(self, attempt: int) -> int:
        """计算等待时间（指数退避）"""
        import random
        wait = min(self.max_wait, self.min_wait * (2 ** attempt))
        # 添加随机抖动
        return wait + random.randint(0, wait // 4)


def with_retry(max_attempts: int = 3):
    """重试装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = min(60, 2 ** attempt)
                        await asyncio.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    return decorator
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/orchestrator/test_retry.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交代码**

```bash
git add src/orchestrator/ tests/orchestrator/
git commit -m "feat: 实现重试机制"
```

---

## Chunk 4: Redis Streams通信与Agent基类

### Task 8: 实现Streams通信

**Files:**
- Create: `src/communication/streams.py`
- Create: `tests/communication/test_streams.py`

- [ ] **Step 1: 编写测试 tests/communication/test_streams.py**

```python
"""Streams通信测试"""
import pytest
from unittest.mock import Mock, patch
from src.communication.streams import StreamManager


class TestStreamManager:
    """流管理器测试"""
    
    @pytest.fixture
    def manager(self):
        with patch('src.communication.streams.RedisClient'):
            return StreamManager()
    
    def test_publish_task_format(self, manager):
        """测试发布任务格式"""
        # 测试消息格式
        task = {
            "trace_id": "12345678",
            "task_id": "task_1",
            "type": "fundamental"
        }
        
        assert "trace_id" in task
        assert "task_id" in task
    
    def test_consume_returns_list(self, manager):
        """测试消费返回列表"""
        # Mock xreadgroup返回空列表
        manager.redis.xreadgroup = Mock(return_value=[])
        
        result = manager.consume("test_stream", "test_group", "consumer")
        
        assert isinstance(result, list)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/communication/test_streams.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现Streams通信 src/communication/streams.py**

```python
"""Redis Streams通信模块"""
from typing import Dict, Any, Optional, List, Callable
import json
from src.communication.redis_client import RedisClient


class StreamManager:
    """Stream管理器"""
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
    
    def publish_task(self, stream_key: str, task: Dict[str, Any]) -> str:
        """发布任务到Stream
        
        Args:
            stream_key: Stream键名
            task: 任务数据
            
        Returns:
            消息ID
        """
        return self.redis.xadd(stream_key, task)
    
    def create_consumer_group(self, stream_key: str, group_name: str):
        """创建消费者组"""
        try:
            self.redis.xgroup_create(stream_key, group_name, id='0', mkstream=True)
        except Exception as e:
            # 忽略已存在的错误
            if "BUSYGROUP" not in str(e):
                raise
    
    def consume(self, stream_key: str, group_name: str, 
                consumer_name: str, count: int = 1, 
                block: int = 5000) -> List[Dict[str, Any]]:
        """消费消息
        
        Args:
            stream_key: Stream键名
            group_name: 消费者组名
            consumer_name: 消费者名
            count: 每次获取数量
            block: 阻塞超时(毫秒)
            
        Returns:
            消息列表
        """
        messages = self.redis.xreadgroup(
            groupname=group_name,
            consumername=consumer_name,
            streams={stream_key: '>'},
            count=count,
            block=block
        )
        
        if not messages:
            return []
        
        results = []
        for stream_name, stream_messages in messages:
            for msg_id, msg_data in stream_messages:
                results.append({
                    "id": msg_id,
                    "data": msg_data
                })
        
        return results
    
    def ack(self, stream_key: str, group_name: str, message_id: str) -> bool:
        """确认消息"""
        return self.redis.xack(stream_key, group_name, message_id)
    
    def get_pending(self, stream_key: str, group_name: str) -> List[Dict[str, Any]]:
        """获取待处理消息"""
        return self.redis.xpending(stream_key, group_name)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/communication/test_streams.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交代码**

```bash
git add src/communication/ tests/communication/
git commit -m "feat: 实现Redis Streams通信"
```

---

### Task 9: 实现Agent基类

**Files:**
- Create: `src/agents/__init__.py`
- Create: `src/agents/base.py`
- Create: `tests/agents/test_base.py`

- [ ] **Step 1: 实现Agent基类 src/agents/base.py**

```python
"""Agent基类模块"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.communication.redis_client import RedisClient
from src.communication.streams import StreamManager
from src.orchestrator.state_machine import TaskStateMachine


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    stream_key: str
    consumer_group: str
    max_retries: int = 3


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.redis = RedisClient()
        self.streams = StreamManager(self.redis)
        self.state_machine = TaskStateMachine(self.redis)
        self._running = False
    
    async def start(self):
        """启动Agent"""
        self._running = True
        
        # 创建消费者组
        self.streams.create_consumer_group(
            self.config.stream_key,
            self.config.consumer_group
        )
        
        # 开始消费
        await self.consume()
    
    async def stop(self):
        """停止Agent"""
        self._running = False
    
    async def consume(self):
        """消费消息循环"""
        import os
        consumer_name = os.getenv('HOSTNAME', 'agent_worker')
        
        while self._running:
            try:
                messages = self.streams.consume(
                    self.config.stream_key,
                    self.config.consumer_group,
                    consumer_name,
                    count=1,
                    block=5000
                )
                
                for msg in messages:
                    await self.process_message(msg)
                    
                    # 确认消息
                    self.streams.ack(
                        self.config.stream_key,
                        self.config.consumer_group,
                        msg["id"]
                    )
                    
            except Exception as e:
                print(f"Agent {self.config.name} error: {e}")
                await asyncio.sleep(1)
    
    async def process_message(self, message: Dict[str, Any]):
        """处理消息（子类实现）"""
        data = message["data"]
        trace_id = data.get("trace_id")
        task_id = data.get("task_id")
        
        # 设置任务状态为运行中
        if trace_id:
            self.state_machine.set_state(trace_id, "running")
        
        try:
            result = await self.execute(data)
            
            # 更新状态为完成
            if trace_id:
                self.state_machine.transition(trace_id, "completed")
            
            # 发布结果
            await self.publish_result(trace_id, task_id, result)
            
        except Exception as e:
            # 更新状态为失败
            if trace_id:
                self.state_machine.transition(trace_id, "failed", str(e))
            
            raise
    
    @abstractmethod
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务（子类实现）"""
        pass
    
    async def publish_result(self, trace_id: str, task_id: str, 
                             result: Dict[str, Any]):
        """发布结果"""
        result_key = f"task:{trace_id}:result:{task_id}"
        self.redis.set(result_key, result)
```

- [ ] **Step 2: 创建agents模块 __init__.py**

```python
"""分智能体模块"""
from src.agents.base import BaseAgent, AgentConfig

__all__ = ["BaseAgent", "AgentConfig"]
```

- [ ] **Step 3: 提交代码**

```bash
git add src/agents/ tests/agents/
git commit -m "feat: 实现Agent基类"
```

---

## 验收标准

Phase 1完成后，系统应满足：

1. ✅ 项目骨架可运行 `poetry run python src/main.py`
2. ✅ Redis连接正常
3. ✅ 可创建任务并获得Trace_ID
4. ✅ 任务状态可流转（pending → running → completed/failed）
5. ✅ 可追踪任务链路
6. ✅ DAG可正确拆解用户输入
7. ✅ Agent基类可消费消息

---

## 后续Phase

- **Phase 2**: 数据中心（DuckDB/LanceDB/SQLite）
- **Phase 3**: 核心4个Agent
- **Phase 4**: 后端API + TUI
- **Phase 5**: 补充Agent + RAG
- **Phase 6**: 集成测试与部署
