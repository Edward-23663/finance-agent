# 行业持仓分析Agent技能文档

> 版本: 1.0.0
> 最后更新: 2026-03-13
> 维护者: Finance Agent Team

## 概述

行业持仓分析Agent负责行业分类映射、成分股列表获取、趋势计算、行业轮动周期分析、持仓性价比分析等功能。

## 快速参考

| 任务类型 | 说明 | 必需参数 |
|----------|------|----------|
| `get_industry` | 获取股票行业分类 | ticker |
| `get_constituents` | 获取行业成分股 | industry |
| `calculate_trend` | 计算行业趋势 | industry |
| `industry_rotation` | 行业轮动周期分析 | - |
| `portfolio_analysis` | 持仓性价比分析 | tickers |

---

## 原子级功能

### 1. 行业分类映射

获取股票的申万/中信行业分类。

**API:**
```python
task_data = {
    "type": "get_industry",
    "ticker": "600519"
}
```

**返回值:**
```json
{
    "status": "success",
    "data": [{"industry": "白酒", "level": 1}]
}
```

### 2. 成分股列表获取

获取指定行业的成分股列表。

**API:**
```python
task_data = {
    "type": "get_constituents",
    "industry": "白酒"
}
```

### 3. 趋势计算

计算行业的价格趋势。

**API:**
```python
task_data = {
    "type": "calculate_trend",
    "industry": "白酒"
}
```

### 4. 强弱指标计算

计算行业相对于大盘的强弱指标。

### 5. 指数对比

将行业指数与基准指数进行对比分析。

---

## 组合级功能

### 行业轮动周期分析

分析各行业在不同周期内的表现，识别轮动规律。

**API:**
```python
task_data = {
    "type": "industry_rotation"
}
```

**返回值:**
```json
{
    "status": "success",
    "data": [
        {"industry": "白酒", "return_1m": 5.2},
        {"industry": "新能源", "return_1m": -2.1}
    ]
}
```

---

## 业务级功能

### 持仓性价比分析

分析投资组合中各股票的估值性价比。

**API:**
```python
task_data = {
    "type": "portfolio_analysis",
    "tickers": ["600519", "000858", "600036"]
}
```

**返回值:**
```json
{
    "status": "success",
    "data": [
        {"ticker": "600519", "pe": 35, "roe": 0.25, "value_score": 0.007},
        {"ticker": "000858", "pe": 20, "roe": 0.15, "value_score": 0.0075}
    ]
}
```

---

## 错误处理

| 错误码 | 说明 |
|--------|------|
| I001 | 行业不存在 |
| I002 | 无成分股数据 |
| I003 | 数据不足无法计算趋势 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-13 | 初始版本 |
