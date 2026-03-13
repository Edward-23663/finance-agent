# Phase 3: 核心Agent实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现4个核心Agent：数据采集、基本面分析、估值、报告生成

**Architecture:** Agent通过Redis Streams接收任务，调用DataWriter写入数据，查询DuckDB获取数据进行计算分析

**Tech Stack:** FastAPI, Redis Streams, DuckDB, LanceDB, pytest

---

## 文件结构

```
src/agents/
├── __init__.py
├── base.py                 # 已存在
├── data_collection.py      # 数据采集Agent
├── fundamental.py          # 基本面分析Agent
├── valuation.py            # 估值Agent
└── report.py               # 报告生成Agent

tests/agents/
├── __init__.py
├── test_data_collection.py
├── test_fundamental.py
├── test_valuation.py
└── test_report.py
```

---

## Chunk 1: DataCollectionAgent 实现

### Task 1: 创建DataCollectionAgent测试

**Files:**
- Create: `tests/agents/test_data_collection.py`

- [ ] **Step 1: 编写失败的测试**

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.data_collection import DataCollectionAgent, AgentConfig


class TestDataCollectionAgent:
    
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="data_collection",
            stream_key="tasks:data_collection",
            consumer_group="agents",
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        with patch('src.agents.data_collection.RedisClient'), \
             patch('src.agents.data_collection.StreamManager'), \
             patch('src.agents.data_collection.TaskStateMachine'):
            return DataCollectionAgent(agent_config)
    
    def test_agent_initialization(self, agent):
        assert agent.config.name == "data_collection"
        assert agent.config.stream_key == "tasks:data_collection"
    
    @pytest.mark.asyncio
    async def test_execute_collect_price(self, agent):
        task_data = {
            "type": "collect_price",
            "ticker": "600519",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }
        
        with patch.object(agent, '_collect_price_data', new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = {"status": "success", "rows": 100}
            result = await agent.execute(task_data)
            
            assert result["status"] == "success"
            mock_collect.assert_called_once_with("600519", "2024-01-01", "2024-12-31")
    
    @pytest.mark.asyncio
    async def test_execute_collect_financial(self, agent):
        task_data = {
            "type": "collect_financial",
            "ticker": "600519",
        }
        
        with patch.object(agent, '_collect_financial_data', new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = {"status": "success", "rows": 4}
            result = await agent.execute(task_data)
            
            assert result["status"] == "success"
            mock_collect.assert_called_once_with("600519")
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/agents/test_data_collection.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.agents.data_collection'"

- [ ] **Step 3: 创建DataCollectionAgent实现**

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

---

### Task 2: 实现DataCollectionAgent

**Files:**
- Create: `src/agents/data_collection.py`

```python
"""数据采集Agent"""
import asyncio
from typing import Dict, Any, List
from src.agents.base import BaseAgent, AgentConfig
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.akshare import AkShareAdapter
from src.data.adapters.yfinance import YFinanceAdapter
from src.data.writer import DataWriter
from src.config import get_settings


class DataCollectionAgent(BaseAgent):
    """数据采集Agent - 负责从数据源采集数据并写入存储"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        settings = get_settings()
        
        self.tushare = TushareAdapter(settings.tushare_token)
        self.akshare = AkShareAdapter()
        self.yfinance = YFinanceAdapter()
        self.writer = DataWriter()
        
        self.source_priority = ["tushare", "akshare", "yfinance"]
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行数据采集任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "collect_price":
            return await self._collect_price_data(
                ticker,
                task_data.get("start_date"),
                task_data.get("end_date"),
            )
        elif task_type == "collect_financial":
            return await self._collect_financial_data(ticker)
        elif task_type == "collect_stock_info":
            return await self._collect_stock_info(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _collect_price_data(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """采集行情数据"""
        for source_name in self.source_priority:
            try:
                adapter = getattr(self, source_name)
                df = adapter.get_price(ticker, start_date, end_date)
                
                if df is not None and not df.empty:
                    await self.writer.write_price_data(df)
                    return {
                        "status": "success",
                        "source": source_name,
                        "rows": len(df),
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
    
    async def _collect_financial_data(self, ticker: str) -> Dict[str, Any]:
        """采集财务数据"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_financial(ticker)
                
                if data:
                    await self.writer.write_financial_metrics(ticker, data)
                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
    
    async def _collect_stock_info(self, ticker: str) -> Dict[str, Any]:
        """采集股票基本信息"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_stock_info(ticker)
                
                if data:
                    await self.writer.write_stock_info(data)
                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
```

- [ ] **Step 1: 编写失败的测试** (已完成在上一个任务)

- [ ] **Step 2: 运行测试验证失败** (已完成在上一个任务)

- [ ] **Step 3: 创建DataCollectionAgent实现**

```bash
cat > src/agents/data_collection.py << 'EOF'
"""数据采集Agent"""
import asyncio
from typing import Dict, Any, List
from src.agents.base import BaseAgent, AgentConfig
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.akshare import AkShareAdapter
from src.data.adapters.yfinance import YFinanceAdapter
from src.data.writer import DataWriter
from src.config import get_settings


class DataCollectionAgent(BaseAgent):
    """数据采集Agent - 负责从数据源采集数据并写入存储"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        settings = get_settings()
        
        self.tushare = TushareAdapter(settings.tushare_token)
        self.akshare = AkShareAdapter()
        self.yfinance = YFinanceAdapter()
        self.writer = DataWriter()
        
        self.source_priority = ["tushare", "akshare", "yfinance"]
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行数据采集任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "collect_price":
            return await self._collect_price_data(
                ticker,
                task_data.get("start_date"),
                task_data.get("end_date"),
            )
        elif task_type == "collect_financial":
            return await self._collect_financial_data(ticker)
        elif task_type == "collect_stock_info":
            return await self._collect_stock_info(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _collect_price_data(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """采集行情数据"""
        for source_name in self.source_priority:
            try:
                adapter = getattr(self, source_name)
                df = adapter.get_price(ticker, start_date, end_date)
                
                if df is not None and not df.empty:
                    await self.writer.write_price_data(df)
                    return {
                        "status": "success",
                        "source": source_name,
                        "rows": len(df),
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
    
    async def _collect_financial_data(self, ticker: str) -> Dict[str, Any]:
        """采集财务数据"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_financial(ticker)
                
                if data:
                    await self.writer.write_financial_metrics(ticker, data)
                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
    
    async def _collect_stock_info(self, ticker: str) -> Dict[str, Any]:
        """采集股票基本信息"""
        for source_name in ["tushare", "akshare"]:
            try:
                adapter = getattr(self, source_name)
                data = adapter.get_stock_info(ticker)
                
                if data:
                    await self.writer.write_stock_info(data)
                    return {
                        "status": "success",
                        "source": source_name,
                        "ticker": ticker,
                    }
            except Exception as e:
                print(f"{source_name} failed: {e}")
                continue
        
        return {"status": "failed", "error": "All sources failed"}
EOF
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/agents/test_data_collection.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add src/agents/data_collection.py tests/agents/test_data_collection.py
git commit -m "feat: 添加DataCollectionAgent实现"
```

---

## Chunk 2: FundamentalAnalysisAgent 实现

### Task 3: 创建FundamentalAnalysisAgent测试

**Files:**
- Create: `tests/agents/test_fundamental.py`

- [ ] **Step 1: 编写测试**

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.fundamental import FundamentalAnalysisAgent, AgentConfig


class TestFundamentalAnalysisAgent:
    
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="fundamental_analysis",
            stream_key="tasks:fundamental_analysis",
            consumer_group="agents",
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        with patch('src.agents.fundamental.RedisClient'), \
             patch('src.agents.fundamental.StreamManager'), \
             patch('src.agents.fundamental.TaskStateMachine'), \
             patch('src.agents.fundamental.DuckDBClient'):
            return FundamentalAnalysisAgent(agent_config)
    
    @pytest.mark.asyncio
    async def test_analyze_financial_health(self, agent):
        task_data = {
            "type": "analyze_financial_health",
            "ticker": "600519",
        }
        
        with patch.object(agent, '_calculate_financial_health', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {
                "score": 85,
                "roe": 0.32,
                "current_ratio": 2.5,
                "debt_ratio": 0.3,
            }
            result = await agent.execute(task_data)
            
            assert result["score"] == 85
            mock_calc.assert_called_once_with("600519")
```

- [ ] **Step 2: 运行测试验证失败**

- [ ] **Step 3: 实现FundamentalAnalysisAgent**

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

---

### Task 4: 实现FundamentalAnalysisAgent

**Files:**
- Create: `src/agents/fundamental.py`

```python
"""基本面分析Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class FundamentalAnalysisAgent(BaseAgent):
    """基本面分析Agent - 分析公司财务健康状况"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行基本面分析任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "analyze_financial_health":
            return await self._calculate_financial_health(ticker)
        elif task_type == "analyze_growth":
            return await self._analyze_growth(ticker)
        elif task_type == "analyze_profitability":
            return await self._analyze_profitability(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _calculate_financial_health(self, ticker: str) -> Dict[str, Any]:
        """计算财务健康得分"""
        metrics = self.db.query_financial_metrics(ticker)
        
        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No financial data"}
        
        latest = metrics[0]
        
        roe = latest.get("roe", 0) or 0
        current_ratio = latest.get("current_ratio", 0) or 0
        debt_ratio = latest.get("debt_ratio", 0) or 0
        
        score = 0
        if roe > 0.15:
            score += 40
        elif roe > 0.10:
            score += 25
        
        if current_ratio > 2.0:
            score += 30
        elif current_ratio > 1.5:
            score += 20
        
        if debt_ratio < 0.3:
            score += 30
        elif debt_ratio < 0.5:
            score += 15
        
        return {
            "status": "success",
            "ticker": ticker,
            "score": min(score, 100),
            "roe": roe,
            "current_ratio": current_ratio,
            "debt_ratio": debt_ratio,
        }
    
    async def _analyze_growth(self, ticker: str) -> Dict[str, Any]:
        """分析成长性"""
        metrics = self.db.query_financial_metrics(ticker, limit=4)
        
        if not metrics or len(metrics) < 2:
            return {"status": "failed", "error": "Insufficient data"}
        
        revenue_growth = 0
        profit_growth = 0
        
        if len(metrics) >= 2:
            latest = metrics[0]
            previous = metrics[1]
            
            revenue_growth = ((latest.get("revenue", 0) or 0) - (previous.get("revenue", 0) or 0)) / (previous.get("revenue", 1) or 1)
            profit_growth = ((latest.get("net_profit", 0) or 0) - (previous.get("net_profit", 0) or 0)) / (previous.get("net_profit", 1) or 1)
        
        return {
            "status": "success",
            "ticker": ticker,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
        }
    
    async def _analyze_profitability(self, ticker: str) -> Dict[str, Any]:
        """分析盈利能力"""
        metrics = self.db.query_financial_metrics(ticker)
        
        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No data"}
        
        latest = metrics[0]
        
        return {
            "status": "success",
            "ticker": ticker,
            "gross_margin": latest.get("gross_margin", 0),
            "net_margin": latest.get("net_margin", 0),
            "roa": latest.get("roa", 0),
        }
```

需要先在DuckDBClient中添加query_financial_metrics方法。

- [ ] **Step 1: 编写测试** (已完成)

- [ ] **Step 2: 运行测试验证失败**

- [ ] **Step 3: 创建FundamentalAnalysisAgent**

```bash
cat > src/agents/fundamental.py << 'EOF'
"""基本面分析Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class FundamentalAnalysisAgent(BaseAgent):
    """基本面分析Agent - 分析公司财务健康状况"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行基本面分析任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "analyze_financial_health":
            return await self._calculate_financial_health(ticker)
        elif task_type == "analyze_growth":
            return await self._analyze_growth(ticker)
        elif task_type == "analyze_profitability":
            return await self._analyze_profitability(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _calculate_financial_health(self, ticker: str) -> Dict[str, Any]:
        """计算财务健康得分"""
        metrics = self.db.query_financial_metrics(ticker)
        
        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No financial data"}
        
        latest = metrics[0]
        
        roe = latest.get("roe", 0) or 0
        current_ratio = latest.get("current_ratio", 0) or 0
        debt_ratio = latest.get("debt_ratio", 0) or 0
        
        score = 0
        if roe > 0.15:
            score += 40
        elif roe > 0.10:
            score += 25
        
        if current_ratio > 2.0:
            score += 30
        elif current_ratio > 1.5:
            score += 20
        
        if debt_ratio < 0.3:
            score += 30
        elif debt_ratio < 0.5:
            score += 15
        
        return {
            "status": "success",
            "ticker": ticker,
            "score": min(score, 100),
            "roe": roe,
            "current_ratio": current_ratio,
            "debt_ratio": debt_ratio,
        }
    
    async def _analyze_growth(self, ticker: str) -> Dict[str, Any]:
        """分析成长性"""
        metrics = self.db.query_financial_metrics(ticker, limit=4)
        
        if not metrics or len(metrics) < 2:
            return {"status": "failed", "error": "Insufficient data"}
        
        revenue_growth = 0
        profit_growth = 0
        
        if len(metrics) >= 2:
            latest = metrics[0]
            previous = metrics[1]
            
            revenue_growth = ((latest.get("revenue", 0) or 0) - (previous.get("revenue", 0) or 0)) / (previous.get("revenue", 1) or 1)
            profit_growth = ((latest.get("net_profit", 0) or 0) - (previous.get("net_profit", 0) or 0)) / (previous.get("net_profit", 1) or 1)
        
        return {
            "status": "success",
            "ticker": ticker,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
        }
    
    async def _analyze_profitability(self, ticker: str) -> Dict[str, Any]:
        """分析盈利能力"""
        metrics = self.db.query_financial_metrics(ticker)
        
        if not metrics or len(metrics) == 0:
            return {"status": "failed", "error": "No data"}
        
        latest = metrics[0]
        
        return {
            "status": "success",
            "ticker": ticker,
            "gross_margin": latest.get("gross_margin", 0),
            "net_margin": latest.get("net_margin", 0),
            "roa": latest.get("roa", 0),
        }
EOF
```

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

---

## Chunk 3: ValuationAgent 实现

### Task 5: 创建ValuationAgent测试和实现

**Files:**
- Create: `tests/agents/test_valuation.py`
- Create: `src/agents/valuation.py`

- [ ] **Step 1: 编写测试**

```python
import pytest
from unittest.mock import patch
from src.agents.valuation import ValuationAgent, AgentConfig


class TestValuationAgent:
    
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="valuation",
            stream_key="tasks:valuation",
            consumer_group="agents",
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        with patch('src.agents.valuation.RedisClient'), \
             patch('src.agents.valuation.StreamManager'), \
             patch('src.agents.valuation.TaskStateMachine'), \
             patch('src.agents.valuation.DuckDBClient'):
            return ValuationAgent(agent_config)
    
    @pytest.mark.asyncio
    async def test_calculate_pe_ratio(self, agent):
        task_data = {
            "type": "calculate_pe",
            "ticker": "600519",
        }
        
        with patch.object(agent, '_calculate_pe', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {"pe": 25.5, "status": "success"}
            result = await agent.execute(task_data)
            
            assert result["pe"] == 25.5
```

- [ ] **Step 2: 运行测试验证失败**

- [ ] **Step 3: 创建ValuationAgent**

```bash
cat > src/agents/valuation.py << 'EOF'
"""估值Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient
from src.data.writer import DataWriter


class ValuationAgent(BaseAgent):
    """估值Agent - 计算股票估值指标"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()
        self.writer = DataWriter()
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行估值任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "calculate_pe":
            return await self._calculate_pe(ticker)
        elif task_type == "calculate_pb":
            return await self._calculate_pb(ticker)
        elif task_type == "calculate_dcf":
            return await self._calculate_dcf(ticker)
        elif task_type == "full_valuation":
            return await self._full_valuation(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _calculate_pe(self, ticker: str) -> Dict[str, Any]:
        """计算市盈率"""
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)
        
        if not price_data or not financial:
            return {"status": "failed", "error": "Insufficient data"}
        
        price = price_data[0].get("close", 0)
        eps = financial[0].get("eps", 0) or 1
        
        pe = price / eps if eps > 0 else 0
        
        return {
            "status": "success",
            "ticker": ticker,
            "pe": round(pe, 2),
            "price": price,
            "eps": eps,
        }
    
    async def _calculate_pb(self, ticker: str) -> Dict[str, Any]:
        """计算市净率"""
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)
        
        if not price_data or not financial:
            return {"status": "failed", "error": "Insufficient data"}
        
        price = price_data[0].get("close", 0)
        bps = financial[0].get("bps", 0) or 1
        
        pb = price / bps if bps > 0 else 0
        
        return {
            "status": "success",
            "ticker": ticker,
            "pb": round(pb, 2),
            "price": price,
            "bps": bps,
        }
    
    async def _calculate_dcf(self, ticker: str) -> Dict[str, Any]:
        """简化DCF估值"""
        financial = self.db.query_financial_metrics(ticker)
        
        if not financial:
            return {"status": "failed", "error": "No financial data"}
        
        latest = financial[0]
        free_cash_flow = latest.get("net_profit", 0) or 1000000000
        
        growth_rate = 0.05
        discount_rate = 0.10
        years = 5
        
        dcf_value = 0
        for i in range(1, years + 1):
            dcf_value += free_cash_flow * (1 + growth_rate) ** i / (1 + discount_rate) ** i
        
        terminal_value = free_cash_flow * (1 + growth_rate) ** years * (1 + 0.03) / (discount_rate - 0.03)
        terminal_value /= (1 + discount_rate) ** years
        
        total_value = dcf_value + terminal_value
        
        return {
            "status": "success",
            "ticker": ticker,
            "dcf_value": round(total_value, 2),
        }
    
    async def _full_valuation(self, ticker: str) -> Dict[str, Any]:
        """完整估值"""
        pe_result = await self._calculate_pe(ticker)
        pb_result = await self._calculate_pb(ticker)
        dcf_result = await self._calculate_dcf(ticker)
        
        pe = pe_result.get("pe", 0)
        pb = pb_result.get("pb", 0)
        dcf = dcf_result.get("dcf_value", 0)
        
        fair_value = (pe * 0.3 + pb * 0.2 + dcf * 0.5) if dcf > 0 else 0
        
        await self.writer.write_valuation({
            "ticker": ticker,
            "pe": pe,
            "pb": pb,
            "dcf_value": dcf,
            "fair_value_mid": fair_value,
        })
        
        return {
            "status": "success",
            "ticker": ticker,
            "pe": pe,
            "pb": pb,
            "dcf_value": dcf,
            "fair_value": round(fair_value, 2),
        }
```

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

---

## Chunk 4: ReportGenerationAgent 实现

### Task 6: 创建ReportGenerationAgent测试和实现

**Files:**
- Create: `tests/agents/test_report.py`
- Create: `src/agents/report.py`

- [ ] **Step 1: 编写测试**

```python
import pytest
from unittest.mock import patch, AsyncMock
from src.agents.report import ReportGenerationAgent, AgentConfig


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
        with patch('src.agents.report.RedisClient'), \
             patch('src.agents.report.StreamManager'), \
             patch('src.agents.report.TaskStateMachine'), \
             patch('src.agents.report.DuckDBClient'):
            return ReportGenerationAgent(agent_config)
    
    @pytest.mark.asyncio
    async def test_generate_report(self, agent):
        task_data = {
            "type": "generate_report",
            "ticker": "600519",
        }
        
        with patch.object(agent, '_generate_text_report', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Test report"
            result = await agent.execute(task_data)
            
            assert "report" in result
```

- [ ] **Step 2: 运行测试验证失败**

- [ ] **Step 3: 创建ReportGenerationAgent**

```bash
cat > src/agents/report.py << 'EOF'
"""报告生成Agent"""
from typing import Dict, Any
from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient


class ReportGenerationAgent(BaseAgent):
    """报告生成Agent - 生成分析报告"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.db = DuckDBClient()
    
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行报告生成任务"""
        task_type = task_data.get("type")
        ticker = task_data.get("ticker")
        
        if task_type == "generate_report":
            return await self._generate_full_report(ticker)
        elif task_type == "generate_summary":
            return await self._generate_summary(ticker)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_full_report(self, ticker: str) -> Dict[str, Any]:
        """生成完整分析报告"""
        stock_info = self.db.query_stock_info(ticker)
        price_data = self.db.query_price_latest(ticker)
        financial = self.db.query_financial_metrics(ticker)
        
        if not stock_info:
            return {"status": "failed", "error": "No stock info"}
        
        info = stock_info[0]
        current_price = price_data[0].get("close") if price_data else 0
        fin = financial[0] if financial else {}
        
        report_lines = []
        report_lines.append(f"# {info.get('name', ticker)} ({ticker}) 分析报告")
        report_lines.append("")
        report_lines.append("## 基本信息")
        report_lines.append(f"- 行业: {info.get('industry', 'N/A')}")
        report_lines.append(f"- 上市日期: {info.get('list_date', 'N/A')}")
        report_lines.append(f"- 当前价格: {current_price}")
        report_lines.append("")
        
        if fin:
            report_lines.append("## 财务指标")
            report_lines.append(f"- ROE: {fin.get('roe', 'N/A')}")
            report_lines.append(f"- 毛利率: {fin.get('gross_margin', 'N/A')}")
            report_lines.append(f"- 净利率: {fin.get('net_margin', 'N/A')}")
            report_lines.append(f"- 当前比率: {fin.get('current_ratio', 'N/A')}")
            report_lines.append("")
        
        report = "\n".join(report_lines)
        
        return {
            "status": "success",
            "ticker": ticker,
            "report": report,
        }
    
    async def _generate_summary(self, ticker: str) -> Dict[str, Any]:
        """生成简短摘要"""
        stock_info = self.db.query_stock_info(ticker)
        
        if not stock_info:
            return {"status": "failed", "error": "No stock info"}
        
        info = stock_info[0]
        
        summary = f"{info.get('name', ticker)} - {info.get('industry', 'N/A')}行业"
        
        return {
            "status": "success",
            "ticker": ticker,
            "summary": summary,
        }
```

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

---

## Chunk 5: DuckDBClient查询方法补充

需要在DuckDBClient中添加缺失的查询方法。

### Task 7: 补充DuckDBClient查询方法

**Files:**
- Modify: `src/data/duckdb_client.py`

- [ ] **Step 1: 添加查询方法**

在DuckDBClient类中添加以下方法：
- `query_financial_metrics(ticker, limit=10)`
- `query_price_latest(ticker)`
- `query_stock_info(ticker)`

```python
def query_financial_metrics(self, ticker: str, limit: int = 10) -> List[Dict]:
    """查询财务指标"""
    query = f"""
        SELECT * FROM financial_metrics 
        WHERE ticker = '{ticker}'
        ORDER BY report_date DESC
        LIMIT {limit}
    """
    return self.execute(query)

def query_price_latest(self, ticker: str) -> List[Dict]:
    """查询最新价格"""
    query = f"""
        SELECT * FROM price_daily 
        WHERE ticker = '{ticker}'
        ORDER BY trade_date DESC
        LIMIT 1
    """
    return self.execute(query)

def query_stock_info(self, ticker: str) -> List[Dict]:
    """查询股票信息"""
    query = f"SELECT * FROM stock_info WHERE ticker = '{ticker}'"
    return self.execute(query)
```

- [ ] **Step 2: 运行现有测试验证通过**

- [ ] **Step 3: 提交**

---

## 最终提交

所有任务完成后，执行最终提交：

```bash
git add src/agents/ tests/agents/ src/data/duckdb_client.py
git commit -m "feat: Phase 3 - 实现4个核心Agent"
git push
```

---

## 验收标准

1. ✅ 所有测试通过
2. ✅ 4个Agent实现完整
3. ✅ DuckDBClient查询方法完整
4. ✅ 代码推送到GitHub
