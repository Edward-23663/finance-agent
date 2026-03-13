# 金融分析智能体 - Phase 2 数据中心实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立数据中心核心模块，包括DuckDB表结构、LanceDB向量存储、SQLite配置管理、DataWriter单线程写机制

**Architecture:** 采用分层架构，计算与解释分离，数据写入通过Redis Streams队列，由DataWriter单线程消费者串行处理

**Tech Stack:** Python 3.11+, DuckDB, LanceDB, SQLite, Redis Streams, pytest

---

## 文件结构

```
src/
├── __init__.py
├── config.py                    # 配置管理（已有，修改增加数据中心配置）
├── data/                        # 数据中心模块
│   ├── __init__.py
│   ├── duckdb_client.py        # DuckDB客户端封装
│   ├── tables.py               # 表结构定义
│   ├── lancedb_client.py       # LanceDB向量存储
│   ├── sqlite_config.py        # SQLite配置管理
│   ├── writer.py               # DataWriter单线程写机制
│   └── adapters/               # 数据源适配器
│       ├── __init__.py
│       ├── base.py             # 适配器基类
│       ├── tushare.py          # Tushare适配器
│       ├── akshare.py          # AkShare适配器
│       └── yfinance.py         # YFinance适配器
├── skills/                     # Skills模块（已有）
│   └── registry.py
tests/
├── __init__.py
├── data/                       # 数据中心测试
│   ├── __init__.py
│   ├── test_duckdb_client.py
│   ├── test_tables.py
│   ├── test_lancedb_client.py
│   ├── test_sqlite_config.py
│   ├── test_writer.py
│   └── test_adapters/
│       ├── __init__.py
│       ├── test_tushare.py
│       ├── test_akshare.py
│       └── test_yfinance.py
```

---

## Chunk 1: DuckDB核心表结构

### Task 1: 创建数据中心模块结构

**Files:**
- Create: `src/data/__init__.py`
- Create: `src/data/adapters/__init__.py`
- Create: `tests/data/__init__.py`
- Create: `tests/data/adapters/__init__.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p src/data/adapters tests/data/adapters
touch src/data/__init__.py src/data/adapters/__init__.py tests/data/__init__.py tests/data/adapters/__init__.py
```

- [ ] **Step 2: 提交代码]

```bash
git add src/data/ tests/data/
git commit -m "feat: 创建数据中心模块结构"
```

---

### Task 2: 实现DuckDB客户端

**Files:**
- Create: `src/data/duckdb_client.py`
- Modify: `tests/data/test_duckdb_client.py` (更新SQL查询)
- Create: `tests/data/test_duckdb_client.py`

- [ ] **Step 1: 编写测试 tests/data/test_duckdb_client.py**

```python
"""DuckDB客户端测试"""
import pytest
import os
import tempfile
from src.data.duckdb_client import DuckDBClient


class TestDuckDBClient:
    """DuckDB客户端测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试用DuckDB客户端"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield DuckDBClient(db_path)
    
    def test_connect(self, client):
        """测试连接"""
        result = client.execute("SELECT 1 as test")
        assert result.fetchone()[0] == 1
    
    def test_table_creation(self, client):
        """测试表创建"""
        from src.data.tables import create_all_tables
        create_all_tables(client)
        
        # DuckDB兼容的表查询
        result = client.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'main'
        """)
        tables = [row[0] for row in result.fetchall()]
        
        assert "stock_info" in tables
        assert "price_daily" in tables
        assert "financial_statements" in tables
```

- [ ] **Step 2: 运行测试验证失败**

Run: `poetry run pytest tests/data/test_duckdb_client.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现DuckDB客户端 src/data/duckdb_client.py**

```python
"""DuckDB客户端封装"""
import os
import duckdb
from typing import Any, List, Tuple, Optional
from pathlib import Path
from src.config import get_settings


class DuckDBClient:
    """DuckDB客户端封装"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "finance.duckdb")
        
        self.db_path = db_path
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """连接数据库"""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = duckdb.connect(self.db_path)
        return self._conn
    
    def execute(self, query: str, params: Tuple = ()) -> Any:
        """执行SQL"""
        conn = self.connect()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)
    
    def execute_many(self, query: str, params_list: List[Tuple]):
        """批量执行"""
        conn = self.connect()
        conn.executemany(query, params_list)
    
    def fetchall(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """查询所有结果"""
        result = self.execute(query, params)
        return result.fetchall()
    
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """查询单条结果"""
        result = self.execute(query, params)
        return result.fetchone()
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

- [ ] **Step 4: 运行测试验证失败]

Run: `poetry run pytest tests/data/test_duckdb_client.py::TestDuckDBClient::test_connect -v`
Expected: FAIL - NameError: name 'os' is not defined

- [ ] **Step 5: 修复导入问题 src/data/duckdb_client.py**

```python
import os  # 添加到导入
```

- [ ] **Step 6: 运行测试验证通过**

Run: `poetry run pytest tests/data/test_duckdb_client.py -v`
Expected: PASS

- [ ] **Step 7: 提交代码]

```bash
git add src/data/duckdb_client.py tests/data/test_duckdb_client.py
git commit -m "feat: 实现DuckDB客户端封装"
```

---

### Task 3: 实现表结构定义

**Files:**
- Create: `src/data/tables.py`
- Create: `tests/data/test_tables.py`

- [ ] **Step 1: 编写测试 tests/data/test_tables.py**

```python
"""表结构测试"""
import pytest
import os
import tempfile
from src.data.duckdb_client import DuckDBClient
from src.data.tables import create_all_tables, STOCK_INFO_COLUMNS


class TestTableCreation:
    """表创建测试"""
    
    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield DuckDBClient(db_path)
    
    def test_stock_info_columns(self, client):
        """测试stock_info表字段"""
        expected = ["ticker", "name", "industry", "list_date", "market_type"]
        assert STOCK_INFO_COLUMNS == expected
    
    def test_create_all_tables(self, client):
        """测试创建所有表"""
        create_all_tables(client)
        
        result = client.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'main'
        """)
        tables = [row[0] for row in result.fetchall()]
        
        assert "stock_info" in tables
        assert "price_daily" in tables
        assert "financial_statements" in tables
        assert "financial_metrics" in tables
        assert "valuations" in tables
        assert "news_sentiment" in tables
        assert "catalyst_events" in tables
        assert "task_history" in tables
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/test_tables.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现表结构 src/data/tables.py**

```python
"""数据表结构定义"""
from typing import List

STOCK_INFO_COLUMNS = [
    "ticker VARCHAR PRIMARY KEY",
    "name VARCHAR",
    "industry VARCHAR",
    "list_date DATE",
    "market_type VARCHAR"
]

PRICE_DAILY_COLUMNS = [
    "ticker VARCHAR",
    "trade_date DATE",
    "open DECIMAL(10,2)",
    "high DECIMAL(10,2)",
    "low DECIMAL(10,2)",
    "close DECIMAL(10,2)",
    "volume BIGINT",
    "amount DECIMAL(20,2)",
    "PRIMARY KEY (ticker, trade_date)"
]

FINANCIAL_STATEMENTS_COLUMNS = [
    "ticker VARCHAR",
    "report_date DATE",
    "report_type VARCHAR",
    "version INTEGER DEFAULT 1",
    "revenue DECIMAL(20,2)",
    "net_profit DECIMAL(20,2)",
    "total_assets DECIMAL(20,2)",
    "total_liabilities DECIMAL(20,2)",
    "equity DECIMAL(20,2)",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "PRIMARY KEY (ticker, report_date, report_type, version)"
]

FINANCIAL_METRICS_COLUMNS = [
    "ticker VARCHAR",
    "report_date DATE",
    "report_type VARCHAR",
    "roe DECIMAL(10,4)",
    "roa DECIMAL(10,4)",
    "gross_margin DECIMAL(10,4)",
    "net_margin DECIMAL(10,4)",
    "current_ratio DECIMAL(10,4)",
    "debt_ratio DECIMAL(10,4)",
    "eps DECIMAL(10,4)",
    "bps DECIMAL(10,4)",
    "PRIMARY KEY (ticker, report_date, report_type)"
]

VALUATIONS_COLUMNS = [
    "ticker VARCHAR",
    "valuation_date DATE",
    "pe DECIMAL(10,2)",
    "pb DECIMAL(10,2)",
    "ps DECIMAL(10,2)",
    "peg DECIMAL(10,2)",
    "dcf_value DECIMAL(20,2)",
    "ddm_value DECIMAL(20,2)",
    "fair_value_low DECIMAL(20,2)",
    "fair_value_mid DECIMAL(20,2)",
    "fair_value_high DECIMAL(20,2)",
    "PRIMARY KEY (ticker, valuation_date)"
]

NEWS_SENTIMENT_COLUMNS = [
    "id VARCHAR PRIMARY KEY",
    "ticker VARCHAR",
    "title TEXT",
    "content TEXT",
    "publish_date TIMESTAMP",
    "sentiment_score DECIMAL(5,4)",
    "sentiment_label VARCHAR",
    "source VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

CATALYST_EVENTS_COLUMNS = [
    "id VARCHAR PRIMARY KEY",
    "ticker VARCHAR",
    "event_type VARCHAR",
    "event_date DATE",
    "title TEXT",
    "description TEXT",
    "impact_score DECIMAL(5,2)",
    "impact_direction VARCHAR",
    "source VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

TASK_HISTORY_COLUMNS = [
    "trace_id VARCHAR PRIMARY KEY",
    "user_input TEXT",
    "status VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "updated_at TIMESTAMP",
    "completed_at TIMESTAMP",
    "result JSON",
    "error_message TEXT"
]


def create_all_tables(client) -> None:
    """创建所有表"""
    tables = {
        "stock_info": STOCK_INFO_COLUMNS,
        "price_daily": PRICE_DAILY_COLUMNS,
        "financial_statements": FINANCIAL_STATEMENTS_COLUMNS,
        "financial_metrics": FINANCIAL_METRICS_COLUMNS,
        "valuations": VALUATIONS_COLUMNS,
        "news_sentiment": NEWS_SENTIMENT_COLUMNS,
        "catalyst_events": CATALYST_EVENTS_COLUMNS,
        "task_history": TASK_HISTORY_COLUMNS,
    }
    
    for table_name, columns in tables.items():
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        client.execute(query)
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/test_tables.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码]

```bash
git add src/data/tables.py tests/data/test_tables.py
git commit -m "feat: 实现DuckDB表结构定义"
```

---

## Chunk 2: SQLite配置管理

### Task 4: 实现SQLite配置管理

**Files:**
- Create: `src/data/sqlite_config.py`
- Create: `tests/data/test_sqlite_config.py`

- [ ] **Step 1: 编写测试 tests/data/test_sqlite_config.py**

```python
"""SQLite配置管理测试"""
import pytest
import os
import tempfile
from src.data.sqlite_config import SQLiteConfigManager


class TestSQLiteConfigManager:
    """SQLite配置管理器测试"""
    
    @pytest.fixture
    def manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "config.db")
            yield SQLiteConfigManager(db_path)
    
    def test_set_and_get(self, manager):
        """测试设置和获取配置"""
        manager.set("test_key", "test_value")
        result = manager.get("test_key")
        assert result == "test_value"
    
    def test_get_nonexistent(self, manager):
        """测试获取不存在的配置"""
        result = manager.get("nonexistent")
        assert result is None
    
    def test_delete(self, manager):
        """测试删除配置"""
        manager.set("to_delete", "value")
        manager.delete("to_delete")
        result = manager.get("to_delete")
        assert result is None
    
    def test_get_all(self, manager):
        """测试获取所有配置"""
        manager.set("key1", "value1")
        manager.set("key2", "value2")
        result = manager.get_all()
        assert len(result) == 2
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/test_sqlite_config.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现SQLite配置管理 src/data/sqlite_config.py**

```python
"""SQLite配置管理模块"""
import os
import sqlite3
import json
from typing import Any, Optional, Dict
from pathlib import Path
from src.config import get_settings


class SQLiteConfigManager:
    """SQLite配置管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "config.db")
        
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self.get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key VARCHAR PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    def get_conn(self) -> sqlite3.Connection:
        """获取连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def set(self, key: str, value: Any) -> None:
        """设置配置"""
        conn = self.get_conn()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        conn = self.get_conn()
        cursor = conn.execute(
            "SELECT value FROM config WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        if row is None:
            return default
        
        value = row[0]
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def delete(self, key: str) -> None:
        """删除配置"""
        conn = self.get_conn()
        conn.execute("DELETE FROM config WHERE key = ?", (key,))
        conn.commit()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        conn = self.get_conn()
        cursor = conn.execute("SELECT key, value FROM config")
        result = {}
        for row in cursor.fetchall():
            try:
                result[row[0]] = json.loads(row[1])
            except (json.JSONDecodeError, TypeError):
                result[row[0]] = row[1]
        return result
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/test_sqlite_config.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码]

```bash
git add src/data/sqlite_config.py tests/data/test_sqlite_config.py
git commit -m "feat: 实现SQLite配置管理"
```

---

## Chunk 3: LanceDB向量存储

### Task 5: 实现LanceDB向量存储

**Files:**
- Create: `src/data/lancedb_client.py`
- Create: `tests/data/test_lancedb_client.py`

- [ ] **Step 1: 编写测试 tests/data/test_lancedb_client.py**

```python
"""LanceDB客户端测试"""
import pytest
import os
import tempfile
import numpy as np
from src.data.lancedb_client import LanceDBClient


class TestLanceDBClient:
    """LanceDB客户端测试"""
    
    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "vectors")
            yield LanceDBClient(db_path)
    
    @pytest.mark.asyncio
    async def test_add_and_search(self, client):
        """测试添加和搜索向量"""
        # 添加向量
        vectors = [[0.1] * 384, [0.2] * 384]
        metadatas = [{"text": "test1"}, {"text": "test2"}]
        
        await client.add("test_table", vectors, metadatas)
        
        # 搜索
        results = await client.search("test_table", [0.1] * 384, limit=2)
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_delete_table(self, client):
        """测试删除表"""
        await client.add("to_delete", [[0.1] * 384], [{"text": "test"}])
        await client.delete_table("to_delete")
        
        tables = client.list_tables()
        assert "to_delete" not in tables
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/test_lancedb_client.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现LanceDB客户端 src/data/lancedb_client.py**

```python
"""LanceDB向量存储客户端"""
from typing import List, Dict, Any, Optional
import numpy as np
import lancedb
from pathlib import Path
from src.config import get_settings


class LanceDBClient:
    """LanceDB向量存储客户端"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "vectors")
        
        self.db_path = db_path
        self._db: Optional[lancedb.LanceDB] = None
    
    def get_db(self) -> lancedb.LanceDB:
        """获取数据库连接"""
        if self._db is None:
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(self.db_path)
        return self._db
    
    async def add(self, table_name: str, vectors: List[List[float]], 
                  metadatas: List[Dict[str, Any]]) -> None:
        """添加向量数据"""
        import asyncio
        db = self.get_db()
        
        data = [
            {"vector": vec, **meta}
            for vec, meta in zip(vectors, metadatas)
        ]
        
        def _add_sync():
            try:
                tbl = db.open_table(table_name)
                tbl.add(data)
            except Exception:
                db.create_table(table_name, data)
        
        await asyncio.get_event_loop().run_in_executor(None, _add_sync)
    
    async def search(self, table_name: str, query_vector: List[float],
                    limit: int = 10) -> List[Dict[str, Any]]:
        """搜索向量"""
        import asyncio
        db = self.get_db()
        
        def _search_sync():
            try:
                tbl = db.open_table(table_name)
                results = tbl.search(query_vector).limit(limit).to_list()
                return results
            except Exception:
                return []
        
        return await asyncio.get_event_loop().run_in_executor(None, _search_sync)
    
    def list_tables(self) -> List[str]:
        """列出所有表"""
        db = self.get_db()
        return db.table_names()
    
    async def delete_table(self, table_name: str) -> None:
        """删除表"""
        import asyncio
        db = self.get_db()
        
        def _delete_sync():
            try:
                db.drop_table(table_name)
            except Exception:
                pass
        
        await asyncio.get_event_loop().run_in_executor(None, _delete_sync)
    
    async def get_table_count(self, table_name: str) -> int:
        """获取表的向量数量"""
        import asyncio
        db = self.get_db()
        
        def _count_sync():
            try:
                tbl = db.open_table(table_name)
                return tbl.count_rows()
            except Exception:
                return 0
        
        return await asyncio.get_event_loop().run_in_executor(None, _count_sync)
    
    def close(self):
        """关闭连接"""
        self._db = None
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/test_lancedb_client.py -v`
Expected: PASS (或跳过如果lancedb未安装)

- [ ] **Step 5: 提交代码]

```bash
git add src/data/lancedb_client.py tests/data/test_lancedb_client.py
git commit -m "feat: 实现LanceDB向量存储客户端"
```

---

## Chunk 4: DataWriter单线程写机制

### Task 6: 实现DataWriter单线程写机制

**Files:**
- Create: `src/data/writer.py`
- Create: `tests/data/test_writer.py`

- [ ] **Step 1: 编写测试 tests/data/test_writer.py**

```python
"""DataWriter测试"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch
from src.data.writer import DataWriter, WriteTask, WriteTaskType


class TestWriteTask:
    """写任务测试"""
    
    def test_write_task_creation(self):
        """测试写任务创建"""
        task = WriteTask(
            task_type=WriteTaskType.PRICE_DAILY,
            data={"ticker": "600519", "close": 1800.0}
        )
        
        assert task.task_type == WriteTaskType.PRICE_DAILY
        assert task.data["ticker"] == "600519"
    
    def test_serialize(self):
        """测试任务序列化"""
        task = WriteTask(
            task_type=WriteTaskType.FINANCIAL_STATEMENT,
            data={"ticker": "600519", "revenue": 1000000}
        )
        
        serialized = task.serialize()
        assert "task_type" in serialized
        assert serialized["task_type"] == "financial_statement"


class TestDataWriter:
    """DataWriter测试"""
    
    @pytest.fixture
    def writer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            with patch('src.data.writer.DuckDBClient') as mock_client:
                mock_instance = Mock()
                mock_client.return_value = mock_instance
                yield DataWriter(db_path=db_path)
    
    def test_enqueue(self, writer):
        """测试入队"""
        task = WriteTask(
            task_type=WriteTaskType.PRICE_DAILY,
            data={"ticker": "600519", "close": 1800.0}
        )
        
        with patch.object(writer.redis, 'lpush') as mock_lpush:
            writer.enqueue(task)
            mock_lpush.assert_called_once()
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/test_writer.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现DataWriter src/data/writer.py**

```python
"""DataWriter单线程写机制"""
import json
import asyncio
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from src.communication.redis_client import RedisClient  # Phase 1已实现
from src.data.duckdb_client import DuckDBClient
from src.data.tables import create_all_tables


class WriteTaskType(str, Enum):
    """写任务类型"""
    PRICE_DAILY = "price_daily"
    FINANCIAL_STATEMENT = "financial_statement"
    FINANCIAL_METRIC = "financial_metric"
    VALUATION = "valuation"
    NEWS_SENTIMENT = "news_sentiment"
    CATALYST_EVENT = "catalyst_event"
    STOCK_INFO = "stock_info"


@dataclass
class WriteTask:
    """写任务"""
    task_type: WriteTaskType
    data: Dict[str, Any]
    trace_id: Optional[str] = None
    
    def serialize(self) -> str:
        """序列化任务"""
        return json.dumps(asdict(self))
    
    @classmethod
    def deserialize(cls, data: str) -> "WriteTask":
        """反序列化任务"""
        obj = json.loads(data)
        return cls(
            task_type=WriteTaskType(obj["task_type"]),
            data=obj["data"],
            trace_id=obj.get("trace_id")
        )


class DataWriter:
    """DataWriter单线程消费者"""
    
    QUEUE_KEY = "data:write:queue"
    
    def __init__(self, db_path: Optional[str] = None):
        self.redis = RedisClient()
        self.db = DuckDBClient(db_path)
        self._running = False
    
    def enqueue(self, task: WriteTask) -> None:
        """将写任务加入队列"""
        self.redis.lpush(self.QUEUE_KEY, task.serialize())
    
    async def run(self) -> None:
        """运行消费者循环"""
        self._running = True
        create_all_tables(self.db)
        
        while self._running:
            try:
                result = self.redis.brpop(self.QUEUE_KEY)
                if result:
                    _, task_data = result
                    task = WriteTask.deserialize(task_data)
                    await self.execute_write(task)
            except Exception as e:
                print(f"DataWriter error: {e}")
                await asyncio.sleep(1)
    
    async def execute_write(self, task: WriteTask) -> None:
        """执行写任务"""
        if task.task_type == WriteTaskType.PRICE_DAILY:
            await self._write_price_daily(task)
        elif task.task_type == WriteTaskType.FINANCIAL_STATEMENT:
            await self._write_financial_statement(task)
        elif task.task_type == WriteTaskType.FINANCIAL_METRIC:
            await self._write_financial_metric(task)
        elif task.task_type == WriteTaskType.VALUATION:
            await self._write_valuation(task)
        elif task.task_type == WriteTaskType.NEWS_SENTIMENT:
            await self._write_news_sentiment(task)
        elif task.task_type == WriteTaskType.CATALYST_EVENT:
            await self._write_catalyst_event(task)
        elif task.task_type == WriteTaskType.STOCK_INFO:
            await self._write_stock_info(task)
    
    async def _write_price_daily(self, task: WriteTask) -> None:
        """写入行情数据"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO price_daily 
            (ticker, trade_date, open, high, low, close, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["ticker"], data["trade_date"], data.get("open"),
            data.get("high"), data.get("low"), data.get("close"),
            data.get("volume"), data.get("amount")
        ))
    
    async def _write_financial_statement(self, task: WriteTask) -> None:
        """写入财务报表"""
        data = task.data
        self.db.execute("""
            INSERT INTO financial_statements 
            (ticker, report_date, report_type, version, revenue, net_profit, 
             total_assets, total_liabilities, equity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["ticker"], data["report_date"], data["report_type"],
            data.get("version", 1), data.get("revenue"), data.get("net_profit"),
            data.get("total_assets"), data.get("total_liabilities"), data.get("equity")
        ))
    
    async def _write_financial_metric(self, task: WriteTask) -> None:
        """写入财务指标"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO financial_metrics 
            (ticker, report_date, report_type, roe, roa, gross_margin, 
             net_margin, current_ratio, debt_ratio, eps, bps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["ticker"], data["report_date"], data["report_type"],
            data.get("roe"), data.get("roa"), data.get("gross_margin"),
            data.get("net_margin"), data.get("current_ratio"), data.get("debt_ratio"),
            data.get("eps"), data.get("bps")
        ))
    
    async def _write_valuation(self, task: WriteTask) -> None:
        """写入估值数据"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO valuations 
            (ticker, valuation_date, pe, pb, ps, peg, dcf_value, ddm_value,
             fair_value_low, fair_value_mid, fair_value_high)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["ticker"], data["valuation_date"], data.get("pe"), data.get("pb"),
            data.get("ps"), data.get("peg"), data.get("dcf_value"), data.get("ddm_value"),
            data.get("fair_value_low"), data.get("fair_value_mid"), data.get("fair_value_high")
        ))
    
    async def _write_news_sentiment(self, task: WriteTask) -> None:
        """写入舆情数据"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO news_sentiment 
            (id, ticker, title, content, publish_date, sentiment_score, 
             sentiment_label, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"], data["ticker"], data.get("title"), data.get("content"),
            data.get("publish_date"), data.get("sentiment_score"),
            data.get("sentiment_label"), data.get("source")
        ))
    
    async def _write_catalyst_event(self, task: WriteTask) -> None:
        """写入催化剂事件"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO catalyst_events 
            (id, ticker, event_type, event_date, title, description,
             impact_score, impact_direction, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"], data["ticker"], data.get("event_type"), data.get("event_date"),
            data.get("title"), data.get("description"), data.get("impact_score"),
            data.get("impact_direction"), data.get("source")
        ))
    
    async def _write_stock_info(self, task: WriteTask) -> None:
        """写入股票信息"""
        data = task.data
        self.db.execute("""
            INSERT OR REPLACE INTO stock_info 
            (ticker, name, industry, list_date, market_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["ticker"], data.get("name"), data.get("industry"),
            data.get("list_date"), data.get("market_type")
        ))
    
    def stop(self) -> None:
        """停止消费者"""
        self._running = False
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/test_writer.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码]

```bash
git add src/data/writer.py tests/data/test_writer.py
git commit -m "feat: 实现DataWriter单线程写机制"
```

---

## Chunk 5: 数据源适配器

### Task 7: 实现数据源适配器基类

**Files:**
- Create: `src/data/adapters/base.py`
- Create: `tests/data/adapters/test_base.py`

- [ ] **Step 1: 编写测试**

```python
"""数据源适配器基类测试"""
import pytest
from src.data.adapters.base import DataSourceAdapter


class TestDataSourceAdapter:
    """数据源适配器测试"""
    
    def test_abstract_methods(self):
        """测试抽象方法"""
        with pytest.raises(TypeError):
            DataSourceAdapter()
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/adapters/test_base.py -v`
Expected: FAIL

- [ ] **Step 3: 实现基类 src/data/adapters/base.py**

```python
"""数据源适配器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd


class DataSourceAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def get_price(self, ticker: str, start_date: str, 
                  end_date: str) -> pd.DataFrame:
        """获取行情数据
        
        Args:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame包含 OHLCV 数据
        """
        pass
    
    @abstractmethod
    def get_financial(self, ticker: str, 
                      report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据
        
        Args:
            ticker: 股票代码
            report_type: 报告类型 (annual/semi/quarter)
            
        Returns:
            财务数据字典
        """
        pass
    
    @abstractmethod
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息
        
        Args:
            ticker: 股票代码
            
        Returns:
            股票信息字典
        """
        pass
    
    def validate_ticker(self, ticker: str) -> bool:
        """验证股票代码格式"""
        return bool(ticker and ticker.isdigit() and len(ticker) == 6)
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/adapters/test_base.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码]

```bash
git add src/data/adapters/base.py tests/data/adapters/test_base.py
git commit -m "feat: 实现数据源适配器基类"
```

---

### Task 8: 实现Tushare适配器

**Files:**
- Create: `src/data/adapters/tushare.py`
- Create: `tests/data/adapters/test_tushare.py`

- [ ] **Step 1: 编写测试**

```python
"""Tushare适配器测试"""
import pytest
from unittest.mock import Mock, patch
from src.data.adapters.tushare import TushareAdapter


class TestTushareAdapter:
    """Tushare适配器测试"""
    
    @pytest.fixture
    def adapter(self):
        with patch('src.data.adapters.tushare.Tushare') as mock_tushare:
            mock_instance = Mock()
            mock_tushare.return_value = mock_instance
            return TushareAdapter("test_token")
    
    def test_init(self, adapter):
        """测试初始化"""
        assert adapter.token == "test_token"
    
    def test_validate_ticker(self, adapter):
        """测试股票代码验证"""
        assert adapter.validate_ticker("600519") is True
        assert adapter.validate_ticker("123456") is True
        assert adapter.validate_ticker("12345") is False
        assert adapter.validate_ticker("abc") is False
    
    @pytest.mark.asyncio
    async def test_get_price_mock(self, adapter):
        """测试获取行情数据"""
        import pandas as pd
        mock_df = pd.DataFrame({
            "trade_date": ["20240101"],
            "open": [100.0],
            "high": [110.0],
            "low": [90.0],
            "close": [105.0],
            "vol": [1000000],
            "amount": [105000000]
        })
        
        with patch.object(adapter, 'get_price', return_value=mock_df):
            result = await adapter.get_price("600519", "20240101", "20240131")
            assert len(result) == 1
```

- [ ] **Step 2: 运行测试验证失败]

Run: `poetry run pytest tests/data/adapters/test_tushare.py -v`
Expected: FAIL

- [ ] **Step 3: 实现Tushare适配器 src/data/adapters/tushare.py**

```python
"""Tushare数据源适配器"""
from typing import Dict, Any, Optional
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class TushareAdapter(DataSourceAdapter):
    """Tushare数据源适配器（主力）"""
    
    def __init__(self, token: str):
        self.token = token
        self._client = None
    
    def _get_client(self):
        """获取Tushare客户端"""
        if self._client is None:
            try:
                import tushare as ts
                self._client = ts.pro_api(self.token)
            except ImportError:
                raise ImportError("请安装tushare: pip install tushare")
        return self._client
    
    def get_price(self, ticker: str, start_date: str, 
                  end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        self.validate_ticker(ticker)
        
        try:
            client = self._get_client()
            df = client.daily(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None and not df.empty:
                df = df.rename(columns={
                    "ts_code": "ticker",
                    "trade_date": "trade_date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "vol": "volume",
                    "amount": "amount"
                })
                df["ticker"] = ticker
            
            return df or pd.DataFrame()
        except Exception as e:
            print(f"Tushare get_price error: {e}")
            return pd.DataFrame()
    
    def get_financial(self, ticker: str, 
                      report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        self.validate_ticker(ticker)
        
        try:
            client = self._get_client()
            
            report_type_map = {
                "annual": "410001",
                "semi": "410002", 
                "quarter": "410003"
            }
            
            fin_type = report_type_map.get(report_type, "410001")
            
            df = client.fina_indicator(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                report_type=fin_type
            )
            
            if df is not None and not df.empty:
                return df.iloc[0].to_dict()
            
            return {}
        except Exception as e:
            print(f"Tushare get_financial error: {e}")
            return {}
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        self.validate_ticker(ticker)
        
        try:
            client = self._get_client()
            
            df = client.stock_basic(
                ts_code=f"{ticker}.SH" if ticker.startswith("6") else f"{ticker}.SZ",
                fields="ts_code,name,industry,list_date,market"
            )
            
            if df is not None and not df.empty:
                row = df.iloc[0]
                return {
                    "ticker": ticker,
                    "name": row.get("name"),
                    "industry": row.get("industry"),
                    "list_date": row.get("list_date"),
                    "market_type": row.get("market")
                }
            
            return {}
        except Exception as e:
            print(f"Tushare get_stock_info error: {e}")
            return {}
```

- [ ] **Step 4: 运行测试验证通过]

Run: `poetry run pytest tests/data/adapters/test_tushare.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码]

```bash
git add src/data/adapters/tushare.py tests/data/adapters/test_tushare.py
git commit -m "feat: 实现Tushare数据源适配器"
```

---

### Task 9: 实现AkShare和YFinance适配器

**Files:**
- Create: `src/data/adapters/akshare.py`
- Create: `src/data/adapters/yfinance.py`
- Create: `tests/data/adapters/test_akshare.py`
- Create: `tests/data/adapters/test_yfinance.py`

- [ ] **Step 1: 编写AkShare测试 tests/data/adapters/test_akshare.py**

```python
"""AkShare适配器测试"""
import pytest
from src.data.adapters.akshare import AkShareAdapter


class TestAkShareAdapter:
    """AkShare适配器测试"""
    
    def test_validate_ticker(self):
        """测试股票代码验证"""
        adapter = AkShareAdapter()
        assert adapter.validate_ticker("600519") is True
        assert adapter.validate_ticker("000001") is True
```

- [ ] **Step 2: 运行AkShare测试验证失败]

Run: `poetry run pytest tests/data/adapters/test_akshare.py -v`
Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现AkShare适配器 src/data/adapters/akshare.py**

```python
"""AkShare数据源适配器"""
from typing import Dict, Any
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class AkShareAdapter(DataSourceAdapter):
    """AkShare数据源适配器（补充）"""
    
    def get_price(self, ticker: str, start_date: str, 
                  end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        self.validate_ticker(ticker)
        
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(
                symbol=ticker,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", "")
            )
            
            if df is not None and not df.empty:
                df = df.rename(columns={
                    "日期": "trade_date",
                    "股票代码": "ticker",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount"
                })
                df["ticker"] = ticker
            
            return df or pd.DataFrame()
        except Exception as e:
            print(f"AkShare get_price error: {e}")
            return pd.DataFrame()
    
    def get_financial(self, ticker: str, 
                      report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        self.validate_ticker(ticker)
        return {}
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        self.validate_ticker(ticker)
        
        try:
            import akshare as ak
            df = ak.stock_individual_info_em(symbol=ticker)
            
            if df is not None and not df.empty:
                info = {}
                for _, row in df.iterrows():
                    info[row.get("item", "")] = row.get("value")
                
                return {
                    "ticker": ticker,
                    "name": info.get("股票名称"),
                    "industry": info.get("所属行业"),
                    "list_date": info.get("上市日期"),
                    "market_type": info.get("交易所")
                }
            
            return {}
        except Exception as e:
            print(f"AkShare get_stock_info error: {e}")
            return {}
```

- [ ] **Step 4: 运行AkShare测试验证通过]

Run: `poetry run pytest tests/data/adapters/test_akshare.py -v`
Expected: PASS

- [ ] **Step 5: 编写YFinance测试 tests/data/adapters/test_yfinance.py**

```python
"""YFinance适配器测试"""
import pytest
from src.data.adapters.yfinance import YFinanceAdapter


class TestYFinanceAdapter:
    """YFinance适配器测试"""
    
    def test_validate_ticker_international(self):
        """测试国际股票代码验证"""
        adapter = YFinanceAdapter()
        # YFinance使用国际代码，如AAPL, MSFT等
        # 基类的6位数字验证不适用
        assert adapter.validate_ticker("AAPL") is False
        assert adapter.validate_ticker("MSFT") is False
```

- [ ] **Step 6: 运行YFinance测试验证失败]

Run: `poetry run pytest tests/data/adapters/test_yfinance.py -v`
Expected: FAIL

- [ ] **Step 7: 实现YFinance适配器 src/data/adapters/yfinance.py**

```python
"""YFinance数据源适配器"""
from typing import Dict, Any
import pandas as pd
from src.data.adapters.base import DataSourceAdapter


class YFinanceAdapter(DataSourceAdapter):
    """YFinance数据源适配器（海外）"""
    
    def get_price(self, ticker: str, start_date: str, 
                  end_date: str) -> pd.DataFrame:
        """获取行情数据"""
        try:
            import yfinance as yf
            
            df = yf.download(ticker, start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                df = df.reset_index()
                df = df.rename(columns={
                    "Date": "trade_date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                    "Adj Close": "close"
                })
                df["ticker"] = ticker
                df["amount"] = df["close"] * df["volume"]
            
            return df or pd.DataFrame()
        except Exception as e:
            print(f"YFinance get_price error: {e}")
            return pd.DataFrame()
    
    def get_financial(self, ticker: str, 
                      report_type: str = "annual") -> Dict[str, Any]:
        """获取财务数据"""
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            financials = stock.financials
            
            if financials is not None and not financials.empty:
                return financials.iloc[0].to_dict()
            
            return {}
        except Exception as e:
            print(f"YFinance get_financial error: {e}")
            return {}
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "name": info.get("shortName"),
                "industry": info.get("industry"),
                "list_date": info.get("firstTradeDate"),
                "market_type": info.get("exchange")
            }
        except Exception as e:
            print(f"YFinance get_stock_info error: {e}")
            return {}
```

- [ ] **Step 8: 运行YFinance测试验证通过]

Run: `poetry run pytest tests/data/adapters/test_yfinance.py -v`
Expected: PASS

- [ ] **Step 9: 提交代码]

```bash
git add src/data/adapters/akshare.py src/data/adapters/yfinance.py tests/data/adapters/test_akshare.py tests/data/adapters/test_yfinance.py
git commit -m "feat: 实现AkShare和YFinance数据源适配器"
```

---

## Chunk 6: 更新配置与集成测试

### Task 10: 更新pyproject.toml添加依赖

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: 添加数据中心依赖**

```toml
# 添加到 [tool.poetry.dependencies]
duckdb = "^1.0.0"
lancedb = "^0.1.0"
pandas = "^2.0.0"
numpy = "^1.24.0"

# Redis已在Phase 1中添加

# 数据源（可选）
tushare = {version = "^1.4.0", optional = true}
akshare = {version = "^1.12.0", optional = true}
yfinance = {version = "^0.2.0", optional = true}

[tool.poetry.extras]
all = ["tushare", "akshare", "yfinance"]
data = ["tushare", "akshare", "yfinance"]
```

- [ ] **Step 2: 运行poetry lock]

```bash
poetry lock --no-update
```

- [ ] **Step 3: 安装新依赖]

```bash
poetry install --extras data
```

- [ ] **Step 4: 提交代码]

```bash
git add pyproject.toml poetry.lock
git commit -m "chore: 添加数据中心依赖"
```

---

### Task 11: 运行所有Phase 2测试

- [ ] **Step 1: 运行所有数据中心测试]

```bash
poetry run pytest tests/data/ -v --tb=short
```

Expected: 全部PASS

- [ ] **Step 2: 提交代码]

```bash
git add .
git commit -m "feat: 完成Phase 2数据中心模块"
```

---

## 验收标准

Phase 2完成后，系统应满足：

1. ✅ 可创建DuckDB数据库和所有表结构
2. ✅ 可通过SQLite管理配置
3. ✅ 可使用LanceDB存储和搜索向量
4. ✅ DataWriter可从Redis队列消费写任务
5. ✅ 可使用Tushare/AkShare/YFinance获取数据
6. ✅ 所有测试通过

---

## 后续Phase

- **Phase 3**: 核心4个Agent（数据采集、基本面、估值、报告）
- **Phase 4**: 后端API + TUI
- **Phase 5**: 补充Agent + RAG
- **Phase 6**: 集成测试与部署
