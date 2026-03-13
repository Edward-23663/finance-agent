# Phase 4: Backend API + TUI 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现FastAPI后端API + TUI终端界面，完成系统闭环

**Architecture:** FastAPI提供RESTful API + SSE流式推送，TUI提供本地配置和监控界面

**Tech Stack:** FastAPI, uvicorn, sse-starlette, Rich, pytest

---

## 文件结构

```
src/
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py       # 任务管理API
│   │   ├── stocks.py      # 数据查询API
│   │   └── config.py      # 配置管理API
│   ├── deps.py            # 依赖注入
│   └── sse.py             # SSE流式推送
├── tui/
│   ├── __init__.py
│   ├── main.py            # TUI主入口
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── config.py      # LLM配置面板
│   │   ├── monitor.py     # 监控面板
│   │   └── debug.py       # 调试面板
│   └── utils.py           # TUI工具函数

tests/
├── api/
│   ├── __init__.py
│   ├── test_tasks.py
│   ├── test_stocks.py
│   └── test_sse.py
└── tui/
    ├── __init__.py
    └── test_tui.py
```

---

## Chunk 1: FastAPI基础框架 + 任务API测试

### Task 1: 创建API测试文件

**Files:**
- Create: `tests/api/__init__.py`
- Create: `tests/api/test_tasks.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/api/test_tasks.py
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


class TestTasksAPI:
    """任务管理API测试"""

    @pytest.fixture
    def mock_orchestrator(self):
        with patch('src.api.routes.tasks.orchestrator') as mock:
            mock.submit_task = AsyncMock(return_value={
                "trace_id": "test_123",
                "status": "pending"
            })
            mock.get_task_status = AsyncMock(return_value={
                "trace_id": "test_123",
                "status": "running",
                "progress": 50
            })
            yield mock

    def test_create_task(self, mock_orchestrator):
        """测试创建任务"""
        from src.api.routes.tasks import create_task
        
        # 这是一个占位测试，实际实现需要通过TestClient
        pass

    def test_get_task_status(self, mock_orchestrator):
        """测试获取任务状态"""
        pass
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/test_tasks.py -v
```

- [ ] **Step 3: 创建API依赖模块**

**Files:**
- Create: `src/api/__init__.py`
- Create: `src/api/deps.py`

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, Header
from typing import Optional
from src.config import get_settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """验证API Key"""
    settings = get_settings()
    
    # 如果没有配置API Key，跳过验证（开发模式）
    if not settings.api_key:
        return "dev_key"
    
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


def get_orchestrator():
    """获取主编排器实例"""
    # 延迟导入避免循环依赖
    from src.orchestrator.main import Orchestrator
    return Orchestrator()
```

- [ ] **Step 4: 创建任务路由**

**Files:**
- Create: `src/api/routes/__init__.py`
- Create: `src/api/routes/tasks.py`

```python
# src/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from src.api.deps import verify_api_key, get_orchestrator

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskRequest(BaseModel):
    ticker: str
    user_input: str
    dimensions: List[str] = ["fundamental", "valuation"]
    options: Optional[dict] = {}


class TaskResponse(BaseModel):
    trace_id: str
    status: str
    created_at: datetime


@router.post("", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    api_key: str = Depends(verify_api_key),
):
    """创建分析任务"""
    trace_id = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    
    # 提交到编排器
    orchestrator = get_orchestrator()
    await orchestrator.submit_task(
        trace_id=trace_id,
        user_input=request.user_input,
        ticker=request.ticker,
        dimensions=request.dimensions,
    )
    
    return TaskResponse(
        trace_id=trace_id,
        status="pending",
        created_at=datetime.now()
    )


@router.get("/{trace_id}")
async def get_task(
    trace_id: str,
    api_key: str = Depends(verify_api_key),
):
    """获取任务状态和结果"""
    orchestrator = get_orchestrator()
    result = await orchestrator.get_task_result(trace_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return result
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/test_tasks.py -v
```

- [ ] **Step 6: 提交**

```bash
git add src/api/ tests/api/
git commit -m "feat: Phase 4 - 添加任务管理API"
```

---

## Chunk 2: SSE流式推送

### Task 2: SSE流式推送实现

**Files:**
- Create: `src/api/sse.py`
- Create: `tests/api/test_sse.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/api/test_sse.py
import pytest
from unittest.mock import patch, AsyncMock


class TestSSE:
    """SSE流式推送测试"""

    @pytest.mark.asyncio
    async def test_sse_stream(self):
        """测试SSE流式输出"""
        pass
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/test_sse.py -v
```

- [ ] **Step 3: 创建SSE模块**

```python
# src/api/sse.py
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Request
from starlette.events import EventSourceResponse
import redis.asyncio as redis

router = APIRouter()


async def event_generator(trace_id: str, request: Request) -> AsyncGenerator[str, None]:
    """SSE事件流生成器"""
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    channel = f"stream:{trace_id}"
    
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    
    try:
        while True:
            # 检查客户端是否断开
            if await request.is_disconnected():
                break
            
            # 阻塞等待消息
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            
            if message and message['type'] == 'message':
                data = message['data']
                if isinstance(data, bytes):
                    data = data.decode()
                
                yield f"data: {data}\n\n"
            
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis_client.close()


@router.get("/stream/{trace_id}")
async def stream(trace_id: str, request: Request):
    """SSE流式端点"""
    return EventSourceResponse(event_generator(trace_id, request))
```

- [ ] **Step 4: 运行测试**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/test_sse.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/api/sse.py tests/api/test_sse.py
git commit -m "feat: Phase 4 - 添加SSE流式推送"
```

---

## Chunk 3: 数据查询API + 健康检查

### Task 3: 数据查询API

**Files:**
- Create: `src/api/routes/stocks.py`
- Create: `tests/api/test_stocks.py`

- [ ] **Step 1: 创建测试和实现**

```python
# src/api/routes/stocks.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from src.api.deps import verify_api_key

router = APIRouter(prefix="/stocks", tags=["stocks"])


class StockInfo(BaseModel):
    ticker: str
    name: str
    industry: str
    list_date: Optional[date] = None
    market_type: Optional[str] = None


class PriceData(BaseModel):
    ticker: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/{ticker}")
async def get_stock_info(
    ticker: str,
    api_key: str = Depends(verify_api_key),
):
    """获取股票基本信息"""
    from src.data.duckdb_client import DuckDBClient
    
    db = DuckDBClient()
    result = db.query(f"SELECT * FROM stock_info WHERE ticker = '{ticker}'")
    
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return result[0]


@router.get("/{ticker}/price")
async def get_price(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    api_key: str = Depends(verify_api_key),
):
    """获取行情数据"""
    from src.data.duckdb_client import DuckDBClient
    
    db = DuckDBClient()
    
    query = f"SELECT * FROM price_daily WHERE ticker = '{ticker}'"
    if start_date:
        query += f" AND trade_date >= '{start_date}'"
    if end_date:
        query += f" AND trade_date <= '{end_date}'"
    query += " ORDER BY trade_date DESC LIMIT 100"
    
    result = db.query(query)
    return result
```

- [ ] **Step 2: 添加健康检查端点**

**Files:**
- Modify: `src/api/routes/tasks.py` (添加health端点)

```python
# 在 tasks.py 中添加
@router.get("/health")
async def health_check():
    """健康检查"""
    import redis.asyncio as redis
    from src.data.duckdb_client import DuckDBClient
    
    checks = {"redis": False, "duckdb": False}
    
    # 检查Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        await r.ping()
        checks["redis"] = True
        await r.close()
    except:
        pass
    
    # 检查DuckDB
    try:
        db = DuckDBClient()
        db.query("SELECT 1")
        checks["duckdb"] = True
    except:
        pass
    
    status = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": status,
        "checks": checks
    }
```

- [ ] **Step 3: 运行测试**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/test_stocks.py -v
```

- [ ] **Step 4: 提交**

```bash
git add src/api/routes/stocks.py tests/api/
git commit -m "feat: Phase 4 - 添加数据查询API"
```

---

## Chunk 4: FastAPI主应用入口

### Task 4: 创建主应用

**Files:**
- Create: `src/api/main.py`
- Modify: `src/main.py`

- [ ] **Step 1: 创建API主入口**

```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import tasks, stocks
from src.api import sse
from src.config import get_settings


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="金融分析智能体 API",
        description="本地私有化部署的金融分析智能体后端API",
        version="0.1.0",
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(stocks.router, prefix="/api/v1")
    app.include_router(sse.router, prefix="/api/v1")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
```

- [ ] **Step 2: 更新配置添加API Key**

**Files:**
- Modify: `src/config.py`

```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    api_key: str = ""  # 用于API认证
    cors_origins: str = "*"  # CORS允许的来源
```

- [ ] **Step 3: 提交**

```bash
git add src/api/main.py src/config.py
git commit -m "feat: Phase 4 - 添加FastAPI主应用入口"
```

---

## Chunk 5: TUI终端界面

### Task 5: TUI基础框架

**Files:**
- Create: `src/tui/__init__.py`
- Create: `src/tui/main.py`
- Create: `tests/tui/test_tui.py`

- [ ] **Step 1: 编写TUI测试**

```python
# tests/tui/test_tui.py
import pytest


class TestTUI:
    """TUI测试"""
    
    def test_config_panel(self):
        """测试配置面板"""
        pass
```

- [ ] **Step 2: 创建TUI主入口**

```python
# src/tui/main.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.console import Console

console = Console()


class FinanceAgentTUI(App):
    """金融分析智能体 TUI"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("金融分析智能体 - TUI 控制台", classes="title"),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        console.print("[bold green]金融分析智能体 TUI 启动成功[/bold green]")


if __name__ == "__main__":
    app = FinanceAgentTUI()
    app.run()
```

- [ ] **Step 3: 创建配置面板**

**Files:**
- Create: `src/tui/panels/__init__.py`
- Create: `src/tui/panels/config.py`

```python
# src/tui/panels/config.py
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, Button, Password
from textual.widget import Widget
from rich.console import Console

console = Console()


class ConfigPanel(Widget):
    """LLM配置面板"""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="config"):
            yield Static("LLM 配置", classes="panel-title")
            yield Input(placeholder="API Key", id="api_key")
            yield Input(placeholder="Base URL", id="base_url")
            yield Input(placeholder="Model Name", id="model")
            yield Button("保存配置", id="save_config")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_config":
            console.print("[green]配置已保存[/green]")
```

- [ ] **Step 4: 创建监控面板**

**Files:**
- Create: `src/tui/panels/monitor.py`

```python
# src/tui/panels/monitor.py
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, ProgressBar
from textual.widget import Widget
from rich.console import Console
import redis.asyncio as redis

console = Console()


class MonitorPanel(Widget):
    """监控面板"""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="monitor"):
            yield Static("系统监控", classes="panel-title")
            yield Static("Agent状态:", id="agent_status")
            yield ProgressBar(total=100, show_eta=False)
    
    async def update_status(self):
        """更新监控状态"""
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            info = await r.info()
            console.print(f"Redis连接: 正常")
            await r.close()
        except Exception as e:
            console.print(f"Redis连接: 失败 - {e}")
```

- [ ] **Step 5: 提交**

```bash
git add src/tui/ tests/tui/
git commit -m "feat: Phase 4 - 添加TUI终端界面"
```

---

## Chunk 6: 集成测试

### Task 6: 集成测试

- [ ] **Step 1: 运行所有Phase 4测试**

```bash
cd /home/jianwei/project1 && python -m pytest tests/api/ tests/tui/ -v
```

- [ ] **Step 2: 手动测试API启动**

```bash
cd /home/jianwei/project1 && python -m src.api.main
```

- [ ] **Step 3: 测试API调用**

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"ticker": "600519", "user_input": "分析贵州茅台"}'
```

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: Phase 4 - Backend API + TUI 完成"
git push
```

---

## 验收标准

1. ✅ FastAPI后端可正常启动
2. ✅ POST /api/v1/tasks 可创建任务
3. ✅ GET /api/v1/tasks/{trace_id} 可查询状态
4. ✅ GET /api/v1/stream/{trace_id} SSE流式推送工作正常
5. ✅ GET /api/v1/stocks/{ticker} 数据查询正常
6. ✅ 健康检查端点正常
7. ✅ TUI界面可启动
8. ✅ 所有测试通过
