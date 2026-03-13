# 基本面分析Agent技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

基本面分析Agent负责分析公司财务健康状况，计算各项财务指标，评估公司盈利、偿债、运营、成长和现金流五大维度的表现。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│               FundamentalAnalysisAgent                   │
├─────────────────────────────────────────────────────────┤
│  输入层                                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │            DuckDB 财务数据                        │   │
│  │  - financial_metrics (财务指标)                   │   │
│  │  - price_daily (价格数据)                         │   │
│  └─────────────────────────────────────────────────┘   │
│                    ▼                                    │
│  分析引擎                                                │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │  偿债能力    │   盈利能力    │   运营能力    │        │
│  │  - 流动比率  │   - ROE      │   - 资产周转率 │        │
│  │  - 速动比率  │   - ROA      │   - 存货周转率 │        │
│  │  - 资产负债率│   - 毛利率   │              │        │
│  └──────────────┴──────────────┴──────────────┘        │
│  ┌──────────────┬──────────────┐                       │
│  │   成长能力    │   现金流     │                       │
│  │  - 营收增长率 │  - 经营现金流 │                       │
│  │  - 利润增长率 │  - 自由现金流│                       │
│  └──────────────┴──────────────┘                       │
│                    ▼                                    │
│  输出层                                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  - 财务健康得分 (0-100)                         │   │
│  │  - 五大维度评分                                 │   │
│  │  - 风险评估                                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `analyze_financial_health` | 计算财务健康得分 | ticker |
| `analyze_growth` | 分析成长能力 | ticker |
| `analyze_profitability` | 分析盈利能力 | ticker |

---

## 原子级功能

### 1. 偿债能力分析

分析公司偿还债务的能力。

**方法:** `_analyze_solvency(ticker: str)`

**计算指标:**

| 指标 | 计算公式 | 阈值 |
|------|----------|------|
| 流动比率 | 流动资产 / 流动负债 | > 2.0 优秀, > 1.5 良好 |
| 速动比率 | (流动资产 - 存货) / 流动负债 | > 1.5 优秀, > 1.0 良好 |
| 资产负债率 | 总负债 / 总资产 | < 0.3 优秀, < 0.5 良好 |

**返回值:**
```json
{
    "ticker": "600519",
    "current_ratio": 2.5,
    "quick_ratio": 2.1,
    "debt_ratio": 0.28,
    "solvency_score": 90
}
```

### 2. 盈利能力分析

分析公司获取利润的能力。

**方法:** `_analyze_profitability(ticker: str)`

**计算指标:**

| 指标 | 计算公式 | 阈值 |
|------|----------|------|
| ROE | 净利润 / 股东权益 | > 15% 优秀, > 10% 良好 |
| ROA | 净利润 / 总资产 | > 8% 优秀, > 5% 良好 |
| 毛利率 | (营收 - 成本) / 营收 | > 40% 优秀, > 25% 良好 |
| 净利率 | 净利润 / 营收 | > 15% 优秀, > 10% 良好 |

**返回值:**
```json
{
    "ticker": "600519",
    "roe": 0.32,
    "roa": 0.18,
    "gross_margin": 0.52,
    "net_margin": 0.26,
    "profitability_score": 95
}
```

### 3. 运营能力分析

分析公司资产运营效率。

**方法:** `_analyze_operation(ticker: str)`

**计算指标:**

| 指标 | 说明 | 阈值 |
|------|------|------|
| 资产周转率 | 营收 / 总资产 | > 1.0 优秀 |
| 存货周转率 | 营业成本 / 存货 | > 8 优秀 |
| 应收账款周转率 | 营收 / 应收账款 | > 10 优秀 |

### 4. 成长能力分析

分析公司业务增长趋势。

**方法:** `_analyze_growth(ticker: str)`

**计算指标:**

| 指标 | 计算公式 |
|------|----------|
| 营收增长率 | (本期营收 - 上期营收) / 上期营收 |
| 利润增长率 | (本期利润 - 上期利润) / 上期利润 |
| 资产增长率 | (本期资产 - 上期资产) / 上期资产 |

**返回值:**
```json
{
    "ticker": "600519",
    "revenue_growth": 0.15,
    "profit_growth": 0.22,
    "asset_growth": 0.12,
    "growth_score": 85
}
```

### 5. 现金流分析

分析公司现金流入流出情况。

**方法:** `_analyze_cashflow(ticker: str)`

**计算指标:**

| 指标 | 说明 |
|------|------|
| 经营现金流/营收 | 经营现金流与营收比率 |
| 自由现金流 | 经营现金流 - 资本支出 |
| 现金流/债务 | 现金流与总债务比率 |

---

## 组合级功能

### 1. 财务健康度评分

综合五大维度计算财务健康得分。

**方法:** `_calculate_financial_health(ticker: str)`

**评分权重:**

| 维度 | 权重 |
|------|------|
| 盈利能力 | 30% |
| 偿债能力 | 30% |
| 运营能力 | 15% |
| 成长能力 | 15% |
| 现金流 | 10% |

**评分规则:**
- 得分 > 80: 优秀
- 得分 > 60: 良好
- 得分 > 40: 一般
- 得分 <= 40: 较差

**返回值:**
```json
{
    "status": "success",
    "ticker": "600519",
    "score": 85,
    "grade": "优秀",
    "roe": 0.32,
    "current_ratio": 2.5,
    "debt_ratio": 0.28,
    "dimensions": {
        "profitability": 95,
        "solvency": 90,
        "operation": 75,
        "growth": 85,
        "cashflow": 70
    }
}
```

### 2. 杜邦分析

使用杜邦恒等式拆解ROE。

**方法:** `_dupont_analysis(ticker: str)`

**公式:**
```
ROE = 净利率 × 资产周转率 × 权益乘数
    = (净利润/营收) × (营收/总资产) × (总资产/股东权益)
```

**返回值:**
```json
{
    "ticker": "600519",
    "roe": 0.32,
    "net_margin": 0.26,
    "asset_turnover": 0.85,
    "equity_multiplier": 1.45,
    "breakdown": {
        "net_margin_contribution": 0.221,
        "asset_turnover_contribution": 0.0725,
        "equity_multiplier_contribution": 0.0265
    }
}
```

### 3. 同业对标分析

与同行业公司进行对比。

**方法:** `_benchmark_analysis(ticker: str, industry: str)`

**返回值:**
```json
{
    "ticker": "600519",
    "industry": "白酒",
    "benchmarks": {
        "roe": {
            "self": 0.32,
            "industry_avg": 0.22,
            "percentile": 85
        },
        "gross_margin": {
            "self": 0.52,
            "industry_avg": 0.45,
            "percentile": 78
        }
    }
}
```

### 4. 造假风险检测

检测财务异常指标。

**方法:** `_detect_fraud_risk(ticker: str)`

**检测规则:**

| 规则 | 条件 |
|------|------|
| 营收与现金流背离 | 营收增长 > 30% 但经营现金流下降 |
| 存货异常增长 | 存货增长率 > 营收增长率的2倍 |
| 应收账款异常 | 应收账款增长率 > 营收增长率的1.5倍 |
| 毛利率异常 | 毛利率大幅提升但无合理理由 |
| 大额关联交易 | 关联交易占比 > 30% |

**返回值:**
```json
{
    "ticker": "600519",
    "risk_level": "low",
    "warnings": [],
    "details": [
        {"rule": "营收与现金流背离", "status": "pass"},
        {"rule": "存货异常增长", "status": "pass"}
    ]
}
```

---

## 业务级功能

### 1. 标的基本面风险价值评估

完整的基本面分析报告。

**任务模板:**
```python
task = {
    "type": "full_fundamental_analysis",
    "ticker": "600519",
    "include": [
        "financial_health",
        "profitability", 
        "growth",
        "solvency",
        "cashflow",
        "fraud_detection",
        "benchmark"
    ]
}
```

**执行流程:**
```
1. 获取财务数据
   ↓
2. 计算五大维度指标
   ↓
3. 杜邦分析拆解ROE
   ↓
4. 造假风险检测
   ↓
5. 同业对标分析
   ↓
6. 综合评分
   ↓
7. 生成评估报告
```

**返回结果:**
```json
{
    "status": "success",
    "ticker": "600519",
    "name": "贵州茅台",
    "industry": "白酒",
    "report_date": "2024-12-31",
    "overall_score": 85,
    "grade": "优秀",
    "risk_level": "低",
    "financial_health": {
        "score": 85,
        "roe": 0.32,
        "current_ratio": 2.5,
        "debt_ratio": 0.28
    },
    "profitability": {
        "score": 95,
        "gross_margin": 0.52,
        "net_margin": 0.26
    },
    "growth": {
        "score": 85,
        "revenue_growth": 0.15,
        "profit_growth": 0.22
    },
    "fraud_detection": {
        "risk_level": "low",
        "warnings": []
    },
    "recommendation": "推荐持有",
    "target_price": 1800.0,
    "upside_potential": 0.15
}
```

### 2. 批量基本面筛选

对多只股票进行批量基本面筛选。

**任务模板:**
```python
task = {
    "type": "screen_stocks",
    "tickers": ["600519", "000858", "600036"],
    "criteria": {
        "min_roe": 0.15,
        "max_debt_ratio": 0.5,
        "min_score": 70
    }
}
```

**返回结果:**
```json
{
    "status": "success",
    "total": 3,
    "passed": 2,
    "results": [
        {
            "ticker": "600519",
            "score": 85,
            "passed": true
        },
        {
            "ticker": "000858",
            "score": 72,
            "passed": true
        },
        {
            "ticker": "600036",
            "score": 65,
            "passed": false,
            "reason": "ROE不满足要求"
        }
    ]
}
```

### 3. 财务指标趋势分析

分析财务指标的历史趋势。

**任务模板:**
```python
task = {
    "type": "trend_analysis",
    "ticker": "600519",
    "metrics": ["roe", "gross_margin", "revenue_growth"],
    "periods": 8  # 8个季度
}
```

---

## 错误处理

### 错误码

| 错误码 | 说明 | 处理策略 |
|--------|------|----------|
| F001 | 无财务数据 | 返回"数据不足"状态 |
| F002 | 数据不完整 | 部分计算，跳过缺失指标 |
| F003 | 计算异常 | 记录日志，返回错误 |

### 数据不足处理

```python
if not metrics or len(metrics) == 0:
    return {
        "status": "failed", 
        "error": "No financial data"
    }

if len(metrics) < 2:
    return {
        "status": "partial",
        "warning": "Insufficient historical data for growth analysis",
        "available_metrics": available_metrics
    }
```

---

## 配置

### 评分阈值

可在配置文件中调整评分阈值:

```yaml
# config.yaml
fundamental_analysis:
  scoring:
    roe:
      excellent: 0.15
      good: 0.10
    current_ratio:
      excellent: 2.0
      good: 1.5
    debt_ratio:
      excellent: 0.30
      good: 0.50
```

### 行业基准

```yaml
# config.yaml
fundamental_analysis:
  industry_benchmarks:
    白酒:
      avg_roe: 0.22
      avg_gross_margin: 0.45
    银行:
      avg_roe: 0.12
      avg_gross_margin: 0.30
```

---

## 测试

### 单元测试

```python
# tests/agents/test_fundamental.py
import pytest
from src.agents.fundamental import FundamentalAnalysisAgent

class TestFundamentalAnalysisAgent:
    
    @pytest.mark.asyncio
    async def test_financial_health_calculation(self):
        agent = FundamentalAnalysisAgent(config)
        
        # Mock数据库返回
        with patch.object(agent.db, 'query_financial_metrics') as mock:
            mock.return_value = [{
                "roe": 0.32,
                "current_ratio": 2.5,
                "debt_ratio": 0.28
            }]
            
            result = await agent.execute({
                "type": "analyze_financial_health",
                "ticker": "600519"
            })
            
            assert result["score"] == 85  # 40+30+15
    
    @pytest.mark.asyncio
    async def test_growth_analysis(self):
        agent = FundamentalAnalysisAgent(config)
        
        with patch.object(agent.db, 'query_financial_metrics') as mock:
            mock.return_value = [
                {"revenue": 1000, "net_profit": 200},
                {"revenue": 870, "net_profit": 160}
            ]
            
            result = await agent.execute({
                "type": "analyze_growth",
                "ticker": "600519"
            })
            
            assert result["revenue_growth"] == pytest.approx(0.149, rel=0.01)
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| analysis_success_rate | 分析成功率 | < 90% |
| data_coverage | 数据覆盖率 | < 80% |
| score_distribution | 得分分布异常 | 过度集中 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
