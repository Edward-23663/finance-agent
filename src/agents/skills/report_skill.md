# 报告生成分智能体技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

报告生成分智能体负责整合分析结果，生成结构化的投资分析报告。支持Markdown、PDF等格式输出，包含数据可视化图表。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                ReportGenerationAgent                      │
├─────────────────────────────────────────────────────────┤
│  数据输入层                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  - 基本面分析结果 (FundamentalAnalysisAgent)     │   │
│  │  - 估值分析结果 (ValuationAgent)                │   │
│  │  - 舆情分析结果 (SentimentAgent)                │   │
│  │  - 催化剂分析结果 (CatalystAgent)                │   │
│  └─────────────────────────────────────────────────┘   │
│                    ▼                                    │
│  报告生成引擎                                           │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │  数据整合   │   模板渲染   │   图表生成   │        │
│  └──────────────┴──────────────┴──────────────┘        │
│                    ▼                                    │
│  输出层                                                  │
│  ┌──────────────┬──────────────┐                        │
│  │   Markdown  │     PDF      │                        │
│  └──────────────┴──────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `generate_report` | 生成完整分析报告 | ticker |
| `generate_summary` | 生成简短摘要 | ticker |
| `generate_template` | 使用模板生成报告 | ticker, template |

---

## 原子级功能

### 1. 基本信息提取

从数据库提取股票基本信息。

**方法:** `_extract_basic_info(ticker: str)`

**返回值:**
```json
{
    "ticker": "600519",
    "name": "贵州茅台",
    "industry": "白酒",
    "list_date": "2001-08-27",
    "market": "主板",
    "current_price": 1712.0,
    "currency": "CNY"
}
```

### 2. 财务指标格式化

将财务指标格式化为可读文本。

**方法:** `_format_financial_metrics(metrics: Dict)`

**格式化规则:**

| 指标 | 格式 | 示例 |
|------|------|------|
| ROE | 百分比, 2位小数 | 32.50% |
| 毛利率 | 百分比, 2位小数 | 52.30% |
| PE | 倍数, 2位小数 | 28.50x |
| 市值 | 亿/万亿 | 2.15万亿 |

### 3. 估值结论生成

根据估值结果生成投资建议。

**方法:** `_generate_valuation_conclusion(valuation: Dict)`

**规则:**

| 上涨空间 | 建议 |
|----------|------|
| > 30% | 强烈推荐买入 |
| 15%~30% | 买入 |
| 0%~15% | 持有 |
| -15%~0% | 减持 |
| < -15% | 卖出 |

### 4. 风险提示生成

根据分析结果生成风险提示。

**方法:** `_generate_risk_warnings(analysis: Dict)`

**风险类型:**

| 风险类型 | 判断条件 |
|----------|----------|
| 估值风险 | PE > 行业均值 50% |
| 财务风险 | 负债率 > 70% |
| 成长风险 | 营收连续2年下降 |
| 流动性风险 | 日成交额 < 1000万 |

---

## 组合级功能

### 1. 结构化报告模板

使用模板生成结构化报告。

**模板结构:**
```markdown
# {{company_name}} ({{ticker}}) 分析报告

## 一、基本信息
- 行业: {{industry}}
- 上市日期: {{list_date}}
- 当前价格: {{current_price}}

## 二、基本面分析
### 2.1 财务健康度
- 综合得分: {{score}}/100
- 评级: {{grade}}

### 2.2 盈利能力
- ROE: {{roe}}
- 毛利率: {{gross_margin}}

## 三、估值分析
- 当前PE: {{pe}}
- 合理估值: {{fair_value}}
- 上涨空间: {{upside}}

## 四、投资建议
{{recommendation}}

## 五、风险提示
{{risk_warnings}}
```

### 2. 图表生成

生成可视化图表。

**支持的图表类型:**

| 图表类型 | 用途 | 库 |
|----------|------|-----|
| 股价走势图 | 价格历史 | Matplotlib/Plotly |
| 财务指标柱状图 | 同比对比 | Matplotlib |
| 估值分位图 | 历史估值 | Plotly |
| 财务健康雷达图 | 多维度评分 | Plotly |

**方法:** `_generate_charts(ticker: str, data: Dict)`

```python
# 股价走势图
def generate_price_chart(price_data):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=price_data['date'],
        open=price_data['open'],
        high=price_data['high'],
        low=price_data['low'],
        close=price_data['close']
    ))
    return fig

# 财务健康雷达图
def generate_radar_chart(scores):
    fig = px.line_polar(
        r=scores.values(),
        theta=scores.index,
        line_close=True
    )
    return fig
```

### 3. 事实对齐校验

使用DuckDB精确查询验证LLM生成内容的准确性。

**方法:** `_verify_facts(report_content: str)`

**校验流程:**
1. 从报告提取关键数值
2. 查询DuckDB获取实际值
3. 比对差异
4. 标记不一致之处

```python
def _verify_facts(report_content):
    # 提取关键指标
    extracted = {
        "roe": extract_value(report_content, "ROE"),
        "pe": extract_value(report_content, "PE"),
        "price": extract_value(report_content, "当前价格")
    }
    
    # 查询验证
    verified = {}
    for key, value in extracted.items():
        actual = db.query_actual_value(key)
        verified[key] = {
            "reported": value,
            "actual": actual,
            "match": abs(value - actual) < 0.01
        }
    
    return verified
```

---

## 业务级功能

### 1. 定制化分析报告一键生成

生成完整的投资分析报告。

**任务模板:**
```python
task = {
    "type": "generate_report",
    "ticker": "600519",
    "format": "markdown",  # markdown, pdf
    "sections": [
        "basic_info",
        "fundamental",
        "valuation", 
        "risk",
        "recommendation"
    ],
    "include_charts": True,
    "language": "zh_CN"
}
```

**执行流程:**
```
1. 提取股票基本信息
   ↓
2. 获取基本面分析结果
   ↓
3. 获取估值分析结果
   ↓
4. 生成风险提示
   ↓
5. 生成投资建议
   ↓
6. 事实校验
   ↓
7. 图表生成 (可选)
   ↓
8. 格式化输出
```

**返回结果:**
```json
{
    "status": "success",
    "ticker": "600519",
    "report_type": "full_analysis",
    "content": "# 贵州茅台 (600519) 分析报告\n\n## 一、基本信息\n\n...",
    "metadata": {
        "generated_at": "2024-12-31 10:30:00",
        "data_sources": ["tushare", "duckdb"],
        "version": "1.0"
    },
    "charts": ["price_chart.html", "radar_chart.html"],
    "word_count": 2500
}
```

### 2. 摘要生成

生成简短摘要。

**任务模板:**
```python
task = {
    "type": "generate_summary",
    "ticker": "600519",
    "length": "brief",  # brief, standard, detailed
    "format": "text"
}
```

**输出示例:**
```
贵州茅台 (600519) - 白酒行业

当前价格: 1712.0元 | 合理估值: 1980元
上涨空间: 15.7%

财务健康: 优秀 (85分)
估值水平: 合理 (PE 28.5x)

投资建议: 持有
风险等级: 低
```

### 3. 对比报告生成

生成多股票对比报告。

**任务模板:**
```python
task = {
    "type": "generate_comparison",
    "tickers": ["600519", "000858", "600809"],
    "dimensions": ["fundamental", "valuation", "growth"],
    "format": "markdown"
}
```

**输出结构:**
```markdown
# 白酒行业对比分析报告

## 一、基础信息对比

| 指标 | 贵州茅台 | 五粮液 | 山西汾酒 |
|------|----------|--------|----------|
| 代码 | 600519 | 000858 | 600809 |
| 价格 | 1712.0 | 168.0 | 320.0 |
| 市值 | 2.15万亿 | 6500亿 | 2900亿 |

## 二、估值对比

| 指标 | 贵州茅台 | 五粮液 | 山西汾酒 |
|------|----------|--------|----------|
| PE | 28.5 | 22.0 | 35.0 |
| PB | 8.2 | 5.5 | 7.8 |

## 三、投资建议
...
```

### 4. PDF导出

生成PDF格式报告。

**任务模板:**
```python
task = {
    "type": "generate_report",
    "ticker": "600519",
    "format": "pdf",
    "template": "professional",
    "include_toc": True
}
```

**PDF配置:**
```python
# 使用reportlab生成PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_pdf(content, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    
    for section in content:
        story.append(Paragraph(section['title'], styles['Heading1']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(section['content'], styles['Normal']))
    
    doc.build(story)
```

---

## 输出格式

### Markdown格式

```markdown
# 贵州茅台 (600519) 分析报告

> 报告日期: 2024-12-31

## 一、公司概况

贵州茅台是中国白酒行业的龙头企业，主要从事高端白酒的生产和销售。

### 1.1 基本信息
- 成立时间: 1999年
- 上市时间: 2001年8月
- 注册资本: 50亿元

## 二、财务分析

### 2.1 盈利能力
- **ROE**: 32.50% (行业平均: 22%)
- **毛利率**: 52.30%
- **净利率**: 26.80%

[图表: 盈利能力趋势图]

## 三、估值分析

| 估值方法 | 估值结果 | 当前位置 |
|----------|----------|----------|
| PE | 1800元 | 合理 |
| DCF | 2150元 | 低估 |
| 合理区间 | 1680-2300元 | - |

## 四、投资建议

### 综合评分: 85/100 (优秀)

**操作建议**: 持有

**目标价**: 2300元

**理由**:
1. 财务健康，ROE持续稳定
2. 品牌护城河深厚
3. 估值处于合理区间

## 五、风险提示

1. 消费需求波动风险
2. 政策影响
3. 估值回调风险
```

### JSON格式

```json
{
    "report_type": "full_analysis",
    "ticker": "600519",
    "generated_at": "2024-12-31T10:30:00",
    "sections": {
        "basic_info": {
            "name": "贵州茅台",
            "industry": "白酒",
            "current_price": 1712.0
        },
        "fundamental": {
            "score": 85,
            "grade": "优秀",
            "roe": 0.325,
            "gross_margin": 0.523
        },
        "valuation": {
            "fair_value": 1980,
            "upside": 0.157,
            "recommendation": "持有"
        },
        "risks": []
    }
}
```

---

## 配置

### 报告模板

```yaml
# config.yaml
report:
  templates:
    default: "standard"
    formats:
      - markdown
      - pdf
      - json
  
  sections:
    - basic_info
    - fundamental
    - valuation
    - risk
    - recommendation
  
  charts:
    enabled: true
    types:
      - price_trend
      - financial_radar
      - valuation_percentile
  
  fact_verification:
    enabled: true
    tolerance: 0.01  # 1%误差容忍
```

### 输出配置

```yaml
# config.yaml
output:
  markdown:
    line_length: 100
    include_toc: true
  
  pdf:
    page_size: "A4"
    font: "SimSun"
    include_page_number: true
```

---

## 测试

### 单元测试

```python
# tests/agents/test_report.py
import pytest
from src.agents.report import ReportGenerationAgent

class TestReportGenerationAgent:
    
    @pytest.mark.asyncio
    async def test_generate_full_report(self):
        agent = ReportGenerationAgent(config)
        
        with patch.object(agent.db, 'query_stock_info') as mock_info, \
             patch.object(agent.db, 'query_price_latest') as mock_price, \
             patch.object(agent.db, 'query_financial_metrics') as mock_fin:
            
            mock_info.return_value = [{
                "ticker": "600519",
                "name": "贵州茅台",
                "industry": "白酒"
            }]
            mock_price.return_value = [{"close": 1712.0}]
            mock_fin.return_value = [{"roe": 0.325}]
            
            result = await agent.execute({
                "type": "generate_report",
                "ticker": "600519"
            })
            
            assert result["status"] == "success"
            assert "贵州茅台" in result["report"]
    
    @pytest.mark.asyncio
    async def test_generate_summary(self):
        agent = ReportGenerationAgent(config)
        
        result = await agent.execute({
            "type": "generate_summary",
            "ticker": "600519"
        })
        
        assert result["status"] == "success"
        assert len(result["summary"]) < 200  # 摘要应该简短
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| generation_success_rate | 生成成功率 | < 95% |
| fact_mismatch_rate | 事实不符率 | > 1% |
| generation_time | 生成耗时 | > 30s |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
