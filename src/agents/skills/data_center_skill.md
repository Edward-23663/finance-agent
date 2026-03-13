# 数据中心Agent技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

数据中心Agent负责本地数据湖的统一管理，为其他智能体提供数据访问调度、数据一致性校验、向量检索等能力。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                      DataCenterAgent                      │
├─────────────────────────────────────────────────────────┤
│  数据访问层                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ DuckDB      │  │ LanceDB     │  │ Redis Cache │     │
│  │ 关系型存储   │  │ 向量存储     │  │ 缓存层      │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │            │
│         └────────────────┼────────────────┘            │
│                          ▼                              │
│              ┌─────────────────────┐                  │
│              │   Data Access API   │                  │
│              └──────────┬──────────┘                  │
│                         ▼                              │
│              ┌─────────────────────┐                  │
│              │  Multi-Agent调度    │                  │
│              └─────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `query_price` | 查询行情数据 | ticker, start_date, end_date |
| `query_financial` | 查询财务数据 | ticker, period |
| `query_vector` | 向量相似度检索 | text, top_k |
| `cache_get` | 获取缓存数据 | key |
| `cache_set` | 设置缓存 | key, value, ttl |

---

## 原子级功能

### 1. DuckDB数据库读写

从本地DuckDB数据库读取数据。

**API:**
```python
task_data = {
    "type": "query_price",
    "ticker": "600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

**返回值:**
```json
{
    "status": "success",
    "data": [
        {"ticker": "600519", "trade_date": "2024-01-02", "close": 1800.5, "volume": 1234567},
        {"ticker": "600519", "trade_date": "2024-01-03", "close": 1815.2, "volume": 2345678}
    ],
    "count": 250
}
```

**支持的查询类型:**
| 类型 | 说明 |
|------|------|
| `query_price` | 日线行情数据 |
| `query_financial` | 财务指标数据 |
| `query_stock_info` | 股票基本信息 |
| `query_industry` | 行业分类数据 |

### 2. Redis缓存操作

使用Redis进行数据缓存。

**API:**
```python
task_data = {
    "type": "cache_get",
    "key": "stock:600519:last_price"
}
```

**返回值:**
```json
{
    "status": "success",
    "value": "1800.5",
    "ttl": 300
}
```

**缓存策略:**
- 热点数据: TTL 5分钟
- 静态数据: TTL 24小时
- 计算结果: TTL 1小时

### 3. 向量数据存储与检索

使用LanceDB进行向量存储和相似度检索。

**API:**
```python
task_data = {
    "type": "query_vector",
    "text": "贵州茅台财务报表分析",
    "top_k": 5
}
```

**返回值:**
```json
{
    "status": "success",
    "results": [
        {"text": "...", "score": 0.95, "metadata": {"ticker": "600519"}},
        {"text": "...", "score": 0.87, "metadata": {"ticker": "000858"}}
    ]
}
```

### 4. 数据读写锁控制

防止并发写入冲突。

**方法:** `_acquire_lock()`, `_release_lock()`

```python
async with self._acquire_lock("stock:600519:price"):
    # 执行写入操作
    pass
```

---

## 组合级功能

### 1. 数据一致性校验

校验多数据源数据的一致性。

**实现:**
```python
async def validate_data_consistency(ticker: str) -> Dict[str, Any]:
    """校验数据一致性"""
    duckdb = DuckDBClient()
    lancedb = LanceDBClient()
    
    # 检查DuckDB数据
    price_count = duckdb.execute(
        "SELECT COUNT(*) FROM price_daily WHERE ticker = ?",
        [ticker]
    )
    
    # 检查向量库数据
    vector_count = lancedb.count_documents(f"ticker:{ticker}")
    
    return {
        "ticker": ticker,
        "duckdb_records": price_count[0]["count"],
        "lancedb_documents": vector_count,
        "consistent": price_count[0]["count"] > 0
    }
```

### 2. 数据版本管理

跟踪数据变更历史。

**实现:**
```python
async def get_data_version(ticker: str, data_type: str) -> Dict[str, Any]:
    """获取数据版本信息"""
    db = DuckDBClient()
    
    result = db.execute("""
        SELECT version, updated_at, source 
        FROM data_versions 
        WHERE ticker = ? AND data_type = ?
        ORDER BY version DESC 
        LIMIT 1
    """, [ticker, data_type])
    
    return {
        "ticker": ticker,
        "data_type": data_type,
        "current_version": result[0]["version"] if result else 0,
        "last_update": result[0]["updated_at"] if result else None
    }
```

### 3. 长文本向量化处理

将长文本分批向量化存储。

**实现:**
```python
async def embed_long_text(text: str, metadata: Dict) -> str:
    """长文本向量化处理"""
    # 文本分块
    chunk_size = 512
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    lancedb = LanceDBClient()
    doc_id = None
    
    for i, chunk in enumerate(chunks):
        vector = await self._get_embedding(chunk)
        doc_id = lancedb.add_document(
            chunk, 
            {**metadata, "chunk_index": i, "total_chunks": len(chunks)}
        )
    
    return doc_id
```

### 4. 多周期时间序列对齐

基于DuckDB的ASOF JOIN实现多周期数据对齐。

**实现:**
```python
async def align_time_series(
    ticker: str, 
    periods: List[str]
) -> Dict[str, Any]:
    """多周期时间序列对齐
    
    periods: ["1d", "1w", "1m", "1q"]
    """
    db = DuckDBClient()
    
    # 使用ASOF JOIN对齐不同周期数据
    result = db.execute("""
        SELECT 
            d.trade_date,
            d.close as daily_close,
            w.close as weekly_close,
            m.close as monthly_close
        FROM price_daily d
        ASOF LEFT JOIN price_weekly w 
            ON d.ticker = w.ticker AND d.trade_date >= w.trade_date
        ASOF LEFT JOIN price_monthly m
            ON d.ticker = m.ticker AND d.trade_date >= m.trade_date
        WHERE d.ticker = ?
        ORDER BY d.trade_date
        LIMIT 1000
    """, [ticker])
    
    return {
        "status": "success",
        "data": result,
        "periods": periods
    }
```

---

## 业务级功能

### 1. 本地数据湖管理

统一管理本地数据存储。

**任务模板:**
```python
task = {
    "type": "data_lake_manage",
    "operation": "sync",
    "tickers": ["600519", "000858", "600036"],
    "data_types": ["price", "financial", "info"]
}
```

**执行流程:**
```
1. 锁定数据湖
   ↓
2. 扫描增量数据
   ↓
3. 数据清洗转换
   ↓
4. 写入目标存储
   ↓
5. 更新版本记录
   ↓
6. 释放锁
```

**返回结果:**
```json
{
    "status": "success",
    "operation": "sync",
    "processed": 3,
    "records": {
        "600519": {"price": 250, "financial": 16, "info": 1},
        "000858": {"price": 250, "financial": 16, "info": 1},
        "600036": {"price": 250, "financial": 16, "info": 1}
    },
    "duration_seconds": 5.2
}
```

### 2. 多智能体数据访问调度

为多个智能体分配数据访问权限和资源。

**任务模板:**
```python
task = {
    "type": "调度_data_access",
    "agent_id": "fundamental_agent",
    "tickers": ["600519", "000858"],
    "data_types": ["price", "financial"],
    "priority": "high"
}
```

**调度策略:**
- 高优先级: 立即响应，专用连接
- 中优先级: 排队等待，共享连接
- 低优先级: 批量处理，延迟执行

### 3. 跨源数据聚合查询

聚合来自多个数据源的数据。

**任务模板:**
```python
task = {
    "type": "aggregate_query",
    "ticker": "600519",
    "metrics": ["price", "financial", "news"],
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
    }
}
```

**返回结果:**
```json
{
    "status": "success",
    "ticker": "600519",
    "aggregated_data": {
        "price": {...},
        "financial": {...},
        "news": {...}
    },
    "data_sources": ["duckdb", "lancedb", "redis"]
}
```

---

## 错误处理

### 错误码

| 错误码 | 说明 | 处理策略 |
|--------|------|----------|
| D001 | 数据库连接失败 | 重试3次后返回错误 |
| D002 | 缓存键不存在 | 返回空值 |
| D003 | 向量服务不可用 | 降级到文本搜索 |
| D004 | 数据版本冲突 | 提示用户手动解决 |
| D005 | 锁获取超时 | 等待后重试 |

### 重试机制

```python
async def _execute_with_retry(operation, max_retries=3):
    """带重试的操作执行"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

---

## 配置

### 存储配置

```yaml
# config.yaml
data_center:
  duckdb:
    path: "data/finance.duckdb"
    read_only: false
  
  lancedb:
    path: "data/vectors"
    metric: "cosine"
  
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: null
```

### 锁配置

```yaml
data_center:
  lock:
    timeout: 30
    retry_interval: 1
    max_retries: 5
```

---

## 测试

### 单元测试

```python
# tests/agents/test_data_center.py
import pytest
from src.agents.data_center import DataCenterAgent

class TestDataCenterAgent:
    
    @pytest.mark.asyncio
    async def test_query_price_success(self):
        agent = DataCenterAgent(config)
        result = await agent.execute({
            "type": "query_price",
            "ticker": "600519",
            "start_date": "2024-01-01",
            "end_date": "2024-01-10"
        })
        assert result["status"] == "success"
        assert result["count"] > 0
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        agent = DataCenterAgent(config)
        
        # 设置缓存
        await agent.execute({
            "type": "cache_set",
            "key": "test:key",
            "value": "test_value",
            "ttl": 60
        })
        
        # 获取缓存
        result = await agent.execute({
            "type": "cache_get",
            "key": "test:key"
        })
        
        assert result["value"] == "test_value"
```

### 集成测试

```python
@pytest.mark.integration
async def test_data_lake_sync():
    """数据湖同步集成测试"""
    agent = DataCenterAgent(config)
    
    result = await agent.execute({
        "type": "data_lake_manage",
        "operation": "sync",
        "tickers": ["600519"]
    })
    
    # 验证数据已同步
    query_result = await agent.execute({
        "type": "query_price",
        "ticker": "600519",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    })
    
    assert query_result["count"] > 0
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| query_latency | 查询延迟 | > 1s |
| cache_hit_rate | 缓存命中率 | < 80% |
| lock_contention | 锁竞争率 | > 10% |
| storage_usage | 存储使用率 | > 90% |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
