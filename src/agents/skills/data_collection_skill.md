# 数据采集Agent技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

数据采集Agent负责从多个数据源采集金融数据，并将其写入本地存储。该Agent支持故障转移和数据源优先级调度。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    DataCollectionAgent                  │
├─────────────────────────────────────────────────────────┤
│  数据源层                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │ Tushare │  │ AkShare │  │ YFinance│                 │
│  └────┬────┘  └────┬────┘  └────┬────┘                 │
│       │            │            │                       │
│       └────────────┼────────────┘                       │
│                    ▼                                    │
│           ┌────────────────┐                            │
│           │ Source Priority│                            │
│           │ 1. Tushare     │                            │
│           │ 2. AkShare     │                            │
│           │ 3. YFinance    │                            │
│           └────────┬───────┘                            │
│                    ▼                                    │
│           ┌────────────────┐                            │
│           │   DataWriter   │                            │
│           └────────┬───────┘                            │
│                    ▼                                    │
│              DuckDB/LanceDB                             │
└─────────────────────────────────────────────────────────┘
```

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `collect_price` | 采集行情数据 | ticker, start_date, end_date |
| `collect_financial` | 采集财务数据 | ticker |
| `collect_stock_info` | 采集股票基本信息 | ticker |

---

## 原子级功能

### 1. 行情数据采集

从指定数据源获取股票行情数据。

**API:**
```
task_data = {
    "type": "collect_price",
    "ticker": "600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

**返回值:**
```json
{
    "status": "success",
    "source": "tushare",
    "rows": 250,
    "ticker": "600519"
}
```

**数据字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| ticker | string | 股票代码 |
| trade_date | string | 交易日期 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | float | 成交量 |
| amount | float | 成交额 |

### 2. 财务数据采集

获取公司财务报表数据。

**API:**
```
task_data = {
    "type": "collect_financial",
    "ticker": "600519"
}
```

**返回值:**
```json
{
    "status": "success",
    "source": "tushare",
    "ticker": "600519"
}
```

**数据字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| ticker | string | 股票代码 |
| report_date | string | 报告期 |
| report_type | string | 报告类型 |
| roe | float | 净资产收益率 |
| roa | float | 总资产收益率 |
| gross_margin | float | 毛利率 |
| net_margin | float | 净利率 |
| current_ratio | float | 流动比率 |
| debt_ratio | float | 资产负债率 |
| eps | float | 每股收益 |
| bps | float | 每股净资产 |

### 3. 股票基本信息采集

获取股票基础信息。

**API:**
```
task_data = {
    "type": "collect_stock_info",
    "ticker": "600519"
}
```

**返回值:**
```json
{
    "status": "success",
    "source": "tushare",
    "ticker": "600519"
}
```

**数据字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| ticker | string | 股票代码 |
| name | string | 股票名称 |
| industry | string | 所属行业 |
| list_date | string | 上市日期 |
| market_type | string | 市场类型 |

### 4. 数据源状态检查

检查各数据源的可用性。

**方法:** `_check_source_status()`

**返回值:**
```json
{
    "tushare": "available",
    "akshare": "available", 
    "yfinance": "available"
}
```

---

## 组合级功能

### 1. 全量数据采集

一次性采集股票的所有基础数据。

**实现:**
```python
async def collect_full_data(ticker: str) -> Dict[str, Any]:
    """采集股票全量数据"""
    results = {}
    
    # 并行采集各类数据
    price_task = self.execute({
        "type": "collect_price",
        "ticker": ticker,
        "start_date": "2020-01-01",
        "end_date": "2024-12-31"
    })
    
    financial_task = self.execute({
        "type": "collect_financial",
        "ticker": ticker
    })
    
    info_task = self.execute({
        "type": "collect_stock_info", 
        "ticker": ticker
    })
    
    results["price"] = await price_task
    results["financial"] = await financial_task
    results["info"] = await info_task
    
    return results
```

### 2. 多股票批量采集

对多只股票进行批量数据采集。

**实现:**
```python
async def batch_collect(tickers: List[str], data_types: List[str]) -> Dict[str, Any]:
    """批量采集多只股票数据"""
    results = {}
    
    for ticker in tickers:
        results[ticker] = {}
        for data_type in data_types:
            task = {
                "type": data_type,
                "ticker": ticker
            }
            if data_type == "collect_price":
                task["start_date"] = "2024-01-01"
                task["end_date"] = "2024-12-31"
            
            result = await self.execute(task)
            results[ticker][data_type] = result
    
    return results
```

### 3. 数据一致性校验

校验采集数据的完整性和一致性。

**实现:**
```python
async def validate_collected_data(ticker: str) -> Dict[str, Any]:
    """校验已采集数据"""
    db = DuckDBClient()
    
    # 检查各表数据量
    price_count = db.execute("SELECT COUNT(*) FROM price_daily WHERE ticker = ?", [ticker])
    financial_count = db.execute("SELECT COUNT(*) FROM financial_metrics WHERE ticker = ?", [ticker])
    info = db.execute("SELECT COUNT(*) FROM stock_info WHERE ticker = ?", [ticker])
    
    return {
        "ticker": ticker,
        "price_records": price_count[0]["count"],
        "financial_records": financial_count[0]["count"],
        "has_basic_info": info[0]["count"] > 0,
        "data_complete": info[0]["count"] > 0 and price_count[0]["count"] > 0
    }
```

---

## 业务级功能

### 1. 指定标的全量基础数据采集任务

完整采集单只股票的所有基础数据。

**任务模板:**
```python
# 单只股票全量采集
task = {
    "type": "collect_full",
    "ticker": "600519",
    "include": ["price", "financial", "info"],
    "price_range": {
        "start": "2020-01-01",
        "end": "2024-12-31"
    }
}
```

**执行流程:**
```
1. 检查数据源可用性
   ↓
2. 采集股票基本信息 (collect_stock_info)
   ↓
3. 采集财务数据 (collect_financial)  
   ↓
4. 采集历史行情 (collect_price)
   ↓
5. 数据一致性校验
   ↓
6. 返回采集结果
```

**返回结果:**
```json
{
    "status": "success",
    "ticker": "600519",
    "collected": {
        "stock_info": true,
        "financial": true,
        "price": true
    },
    "records": {
        "price": 1250,
        "financial": 16,
        "info": 1
    },
    "sources_used": ["tushare"],
    "duration_seconds": 2.5
}
```

### 2. 投资组合批量采集

对投资组合中的多只股票进行批量采集。

**任务模板:**
```python
task = {
    "type": "portfolio_collect",
    "tickers": ["600519", "000858", "600036"],
    "data_types": ["stock_info", "financial"],
    "priority": "high"  # high: 并行执行, low: 串行执行
}
```

### 3. 数据增量更新

增量更新已有股票数据。

**任务模板:**
```python
task = {
    "type": "incremental_update",
    "ticker": "600519",
    "last_update": "2024-12-01"
}
```

**执行逻辑:**
1. 查询最近更新日期
2. 仅采集该日期之后的新数据
3. 合并到现有数据库

---

## 错误处理

### 错误码

| 错误码 | 说明 | 处理策略 |
|--------|------|----------|
| E001 | 数据源不可用 | 切换到下一个数据源 |
| E002 | 股票代码无效 | 返回错误，跳过该股票 |
| E003 | 网络超时 | 重试3次后切换数据源 |
| E004 | 数据格式错误 | 记录错误，继续处理 |

### 重试机制

```python
# 数据源失败时的重试策略
source_priority = ["tushare", "akshare", "yfinance"]

for source in source_priority:
    try:
        result = adapter.get_data(ticker)
        if result:
            return result
    except Exception as e:
        print(f"{source} failed: {e}")
        continue  # 尝试下一个数据源

return {"status": "failed", "error": "All sources failed"}
```

---

## 配置

### 数据源优先级

默认优先级可在配置文件中修改:

```yaml
# config.yaml
data_collection:
  source_priority:
    - tushare    # 国内A股首选
    - akshare    # 备用
    - yfinance   # 海外股票
```

### Tushare Token

需要配置Tushare token:

```bash
# .env
TUSHARE_TOKEN=your_token_here
```

---

## 测试

### 单元测试

```python
# tests/agents/test_data_collection.py
import pytest
from src.agents.data_collection import DataCollectionAgent

class TestDataCollectionAgent:
    
    @pytest.mark.asyncio
    async def test_collect_price_success(self):
        agent = DataCollectionAgent(config)
        result = await agent.execute({
            "type": "collect_price",
            "ticker": "600519",
            "start_date": "2024-01-01",
            "end_date": "2024-01-10"
        })
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_collect_price_source_fallback(self):
        agent = DataCollectionAgent(config)
        # Tushare失败时自动切换
        result = await agent.execute({...})
        assert result.get("source") in ["tushare", "akshare", "yfinance"]
```

### 集成测试

```python
@pytest.mark.integration
async def test_full_data_collection():
    """完整数据采集集成测试"""
    agent = DataCollectionAgent(config)
    
    result = await agent.execute({
        "type": "collect_full",
        "ticker": "600519"
    })
    
    # 验证数据已写入数据库
    db = DuckDBClient()
    price_count = db.execute("SELECT COUNT(*) FROM price_daily WHERE ticker = '600519'")
    assert price_count[0]["count"] > 0
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| collection_success_rate | 采集成功率 | < 95% |
| source_response_time | 数据源响应时间 | > 5s |
| data_freshness | 数据新鲜度 | > 24h |
| error_count | 错误次数 | > 10/min |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
