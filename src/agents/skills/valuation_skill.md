# 多模型估值Agent技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

多模型估值Agent负责使用多种估值方法计算股票的合理价值，包括PE、PB、DCF、DDM等模型，并进行交叉验证和敏感性分析。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    ValuationAgent                        │
├─────────────────────────────────────────────────────────┤
│  输入层                                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │            DuckDB 数据                            │   │
│  │  - price_daily (价格数据)                        │   │
│  │  - financial_metrics (财务指标)                 │   │
│  │  - stock_info (股票信息)                        │   │
│  └─────────────────────────────────────────────────┘   │
│                    ▼                                    │
│  估值模型层                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │   PE   │ │   PB   │ │  DCF   │ │  DDM   │     │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘     │
│       │            │            │            │          │
│       └────────────┼────────────┘            │          │
│                    ▼                         │          │
│           ┌────────────────┐                 │          │
│           │ 结果交叉验证   │◄────────────────┘          │
│           └────────┬───────┘                            │
│                    ▼                                    │
│  输出层                                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  - 合理估值区间                                  │   │
│  │  - 敏感性分析                                    │   │
│  │  - 投资建议                                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `calculate_pe` | 市盈率估值 | ticker |
| `calculate_pb` | 市净率估值 | ticker |
| `calculate_dcf` | DCF估值 | ticker |
| `full_valuation` | 完整估值 | ticker |

---

## 原子级功能

### 1. 市盈率估值 (PE)

基于盈利的估值方法。

**方法:** `_calculate_pe(ticker: str)`

**公式:**
```
PE = 当前股价 / 每股收益(EPS)
```

**估值逻辑:**
- 静态PE: 使用历史EPS
- 动态PE: 使用预期EPS

**行业PE基准:**

| 行业 | 低估 | 合理 | 高估 |
|------|------|------|------|
| 白酒 | < 20 | 20-35 | > 35 |
| 银行 | < 6 | 6-10 | > 10 |
| 科技 | < 25 | 25-50 | > 50 |
| 医药 | < 20 | 20-40 | > 40 |

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "pe": 28.5,
    "price": 1712.0,
    "eps": 60.07,
    "pe_percentile": 45,
    "valuation": "合理",
    "industry_avg_pe": 30
}
```

### 2. 市净率估值 (PB)

基于资产的估值方法。

**方法:** `_calculate_pb(ticker: str)`

**公式:**
```
PB = 当前股价 / 每股净资产(BPS)
```

**估值逻辑:**
- PB < 1: 股价低于净资产
- PB = 1: 股价等于净资产
- PB > 1: 股价高于净资产

**行业PB基准:**

| 行业 | 低估 | 合理 | 高估 |
|------|------|------|------|
| 银行 | < 0.6 | 0.6-1.2 | > 1.2 |
| 地产 | < 0.5 | 0.5-1.5 | > 1.5 |
| 制造 | < 1.5 | 1.5-3.0 | > 3.0 |

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "pb": 8.2,
    "price": 1712.0,
    "bps": 208.78,
    "valuation": "高估"
}
```

### 3. PEG估值

将PE与增长率结合。

**方法:** `_calculate_peg(ticker: str)`

**公式:**
```
PEG = PE / 净利润增长率(G)
```

**判断标准:**
- PEG < 1: 低估
- PEG = 1: 合理
- PEG > 1: 高估

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "peg": 0.85,
    "pe": 28.5,
    "growth_rate": 33.5,
    "valuation": "低估"
}
```

### 4. DCF估值 (现金流折现)

基于现金流的估值方法。

**方法:** `_calculate_dcf(ticker: str)`

**模型参数:**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| growth_rate | 初始增长率 | 5% |
| discount_rate | 折现率 | 10% |
| terminal_growth | 永续增长率 | 3% |
| projection_years | 预测年数 | 5年 |

**公式:**
```
企业价值 = Σ(FCF_t / (1+r)^t) + 终值/(1+r)^n

终值 = FCF_n × (1+g) / (r-g)
```

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "dcf_value": 2150.0,
    "parameters": {
        "growth_rate": 0.05,
        "discount_rate": 0.10,
        "terminal_growth": 0.03,
        "projection_years": 5
    },
    "cash_flows": [1050, 1102, 1157, 1215, 1276],
    "terminal_value": 19142,
    "discounted_terminal": 11953
}
```

### 5. DDM股息折现模型

基于股息的估值方法。

**方法:** `_calculate_ddm(ticker: str)`

**公式:**
```
股票价值 = Σ(D_t / (1+r)^t) + P_n/(1+r)^n

其中 P_n = D_{n+1} / (r-g)
```

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "ddm_value": 1680.0,
    "dividend_yield": 0.015,
    "dividend_growth": 0.12,
    "discount_rate": 0.10
}
```

---

## 组合级功能

### 1. 多模型估值结果交叉验证

将多种估值方法的结果进行交叉验证。

**方法:** `_cross_validate(ticker: str)`

**验证逻辑:**

```python
def _cross_validate(pe_value, pb_value, dcf_value, ddm_value):
    values = [pe_value, pb_value, dcf_value, ddm_value]
    
    # 计算各模型偏差
    avg = sum(values) / len(values)
    deviations = [abs(v - avg) / avg for v in values]
    
    # 判断一致性
    max_deviation = max(deviations)
    if max_deviation < 0.2:
        confidence = "高"
        fair_value = avg
    elif max_deviation < 0.4:
        confidence = "中"
        # 去掉最高和最低，取平均
        values.sort()
        fair_value = sum(values[1:-1]) / (len(values) - 2)
    else:
        confidence = "低"
        fair_value = dcf_value  # 优先信任DCF
    
    return {
        "confidence": confidence,
        "fair_value": fair_value,
        "deviations": deviations
    }
```

**返回值:**
```json
{
    "ticker": "600519",
    "models": {
        "pe": {"value": 1712, "weight": 0.3},
        "pb": {"value": 2450, "weight": 0.2},
        "dcf": {"value": 2150, "weight": 0.5},
        "ddm": {"value": 1680, "weight": 0.0}
    },
    "fair_value": 1980,
    "confidence": "中",
    "deviation": 0.15
}
```

### 2. 敏感性分析

分析关键参数变化对估值的影响。

**方法:** `_sensitivity_analysis(ticker: str)`

**参数组合:**

| 参数 | 低 | 中 | 高 |
|------|-----|-----|-----|
| 增长率 | 3% | 5% | 8% |
| 折现率 | 8% | 10% | 12% |
| 永续增长率 | 2% | 3% | 4% |

**返回值:**
```json
{
    "ticker": "600519",
    "sensitivity_matrix": {
        "discount_rate": {
            "0.08": {"growth_0.03": 2500, "growth_0.05": 2800, "growth_0.08": 3200},
            "0.10": {"growth_0.03": 2100, "growth_0.05": 2400, "growth_0.08": 2700},
            "0.12": {"growth_0.03": 1800, "growth_0.05": 2000, "growth_0.08": 2300}
        }
    },
    "base_case": 2150,
    "upside": 2700,
    "downside": 1800,
    "volatility": 0.22
}
```

### 3. 历史估值分位计算

计算当前估值在历史估值中的分位。

**方法:** `_calculate_percentile(ticker: str)`

**返回值:**
```json
{
    "ticker": "600519",
    "pe_percentile": 45,
    "pb_percentile": 72,
    "dcf_percentile": 38,
    "current_price": 1712,
    "historial_range": {
        "pe_low": 15,
        "pe_high": 50,
        "pb_low": 3,
        "pb_high": 12
    }
}
```

---

## 业务级功能

### 1. 标的合理估值区间测算

完整的估值分析，包括敏感性分析。

**任务模板:**
```python
task = {
    "type": "full_valuation",
    "ticker": "600519",
    "include": ["pe", "pb", "dcf", "ddm"],
    "sensitivity": true,
    "benchmark": true
}
```

**执行流程:**
```
1. 获取价格和财务数据
   ↓
2. 计算PE估值
   ↓
3. 计算PB估值
   ↓
4. 计算DCF估值
   ↓
5. 计算DDM估值 (如有股息数据)
   ↓
6. 交叉验证确定合理价值
   ↓
7. 敏感性分析
   ↓
8. 历史分位分析
   ↓
9. 生成投资建议
```

**返回结果:**
```json
{
    "status": "success",
    "ticker": "600519",
    "name": "贵州茅台",
    "current_price": 1712.0,
    "valuation_date": "2024-12-31",
    "models": {
        "pe": {"value": 1712, "method": "static"},
        "pb": {"value": 2450, "method": "adjusted"},
        "dcf": {"value": 2150, "method": "5yr_projection"},
        "ddm": {"value": 1680, "method": "2_stage"}
    },
    "fair_value": {
        "low": 1680,
        "mid": 1980,
        "high": 2300,
        "confidence": "中"
    },
    "upside_potential": 0.16,
    "recommendation": "持有",
    "sensitivity": {
        "discount_rate_sensitive": true,
        "growth_rate_sensitive": false,
        "price_range": [1800, 2700]
    },
    "percentile": {
        "pe": 45,
        "pb": 72
    }
}
```

### 2. 批量估值筛选

对多只股票进行批量估值分析。

**任务模板:**
```python
task = {
    "type": "batch_valuation",
    "tickers": ["600519", "000858", "600036"],
    "models": ["pe", "dcf"]
}
```

**返回结果:**
```json
{
    "status": "success",
    "total": 3,
    "results": [
        {
            "ticker": "600519",
            "current_price": 1712,
            "fair_value": 1980,
            "upside": 0.16,
            "recommendation": "持有"
        },
        {
            "ticker": "000858", 
            "current_price": 168,
            "fair_value": 195,
            "upside": 0.16,
            "recommendation": "持有"
        },
        {
            "ticker": "600036",
            "current_price": 42,
            "fair_value": 38,
            "upside": -0.10,
            "recommendation": "卖出"
        }
    ]
}
```

### 3. 估值报告生成

生成详细的估值分析报告。

**任务模板:**
```python
task = {
    "type": "valuation_report",
    "ticker": "600519",
    "format": "markdown",
    "include_charts": true
}
```

---

## 错误处理

### 错误码

| 错误码 | 说明 | 处理策略 |
|--------|------|----------|
| V001 | 无价格数据 | 返回失败 |
| V002 | 无财务数据 | 跳过PE/DC计算 |
| V003 | EPS为负 | PE不适用，使用PB |
| V004 | BPS为负 | PB不适用 |

### 处理策略

```python
# EPS为负时的处理
if eps <= 0:
    pe_result = {"status": "skipped", "reason": "EPS <= 0"}
else:
    pe_result = calculate_pe()

# 数据不足时的权重调整
if not ddm_available:
    weights = {"pe": 0.4, "pb": 0.3, "dcf": 0.3}
else:
    weights = {"pe": 0.3, "pb": 0.2, "dcf": 0.4, "ddm": 0.1}
```

---

## 配置

### 模型参数

```yaml
# config.yaml
valuation:
  dcf:
    default_growth_rate: 0.05
    default_discount_rate: 0.10
    terminal_growth: 0.03
    projection_years: 5
  
  weights:
    pe: 0.30
    pb: 0.20
    dcf: 0.50
    ddm: 0.00
  
  thresholds:
    undervalued: 0.20  # 上涨空间 > 20%
    overvalued: -0.20   # 下跌空间 > 20%
```

### 行业参数

```yaml
# config.yaml
valuation:
  industry_params:
    白酒:
      default_pe: 30
      default_pb: 8
      growth_rate: 0.15
    银行:
      default_pe: 8
      default_pb: 0.8
      growth_rate: 0.05
```

---

## 测试

### 单元测试

```python
# tests/agents/test_valuation.py
import pytest
from src.agents.valuation import ValuationAgent

class TestValuationAgent:
    
    @pytest.mark.asyncio
    async def test_pe_calculation(self):
        agent = ValuationAgent(config)
        
        with patch.object(agent.db, 'query_price_latest') as mock_price, \
             patch.object(agent.db, 'query_financial_metrics') as mock_fin:
            
            mock_price.return_value = [{"close": 1712.0}]
            mock_fin.return_value = [{"eps": 60.07}]
            
            result = await agent.execute({
                "type": "calculate_pe",
                "ticker": "600519"
            })
            
            assert result["pe"] == pytest.approx(28.5, rel=0.1)
    
    @pytest.mark.asyncio
    async def test_dcf_calculation(self):
        agent = ValuationAgent(config)
        
        with patch.object(agent.db, 'query_financial_metrics') as mock:
            mock.return_value = [{"net_profit": 50000000000}]
            
            result = await agent.execute({
                "type": "calculate_dcf", 
                "ticker": "600519"
            })
            
            assert result["status"] == "success"
            assert result["dcf_value"] > 0
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| valuation_success_rate | 估值成功率 | < 90% |
| model_confidence | 模型置信度 | < 中 |
| data_freshness | 数据新鲜度 | > 24h |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
