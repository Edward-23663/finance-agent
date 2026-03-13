# Phase 6: Web UI 组件完善

## 概述

完善金融分析AI代理系统的Web前端UI组件，包括图表组件、布局组件和报告子组件。

## 当前状态

- 已完成: Dashboard首页、Report报告页面基础结构
- 待完善: Chart组件库、Layout布局、报告详情子组件

## 组件设计

### 1. 图表组件 (src/components/Chart/)

| 组件名 | 用途 | 图表类型 |
|--------|------|----------|
| KLineChart.vue | K线图+成交量 | ECharts K线 |
| DupontChart.vue | 杜邦分析拆解 | ECharts 饼图/瀑布图 |
| ValuationChart.vue | 多模型估值对比 | ECharts 柱状图 |
| FinancialTrendChart.vue | 财务指标趋势 | ECharts 折线图 |

### 2. 布局组件 (src/components/Layout/)

| 组件名 | 用途 |
|--------|------|
| AppSidebar.vue | 左侧导航菜单 |
| AppHeader.vue | 顶部导航+状态 |
| MainLayout.vue | 页面主布局容器 |

### 3. 报告子组件 (src/views/Report/components/)

| 组件名 | 用途 |
|--------|------|
| FinancialCard.vue | 财务指标数据卡片 |
| ValuationCard.vue | 估值结果展示卡片 |
| SentimentCard.vue | 舆情分析摘要卡片 |
| CatalystCard.vue | 催化剂信息卡片 |

## 技术选型

- **图表库**: ECharts 5.x (与Element Plus风格统一)
- **布局方案**: 经典后台管理布局(侧边栏+顶部+内容区)
- **响应式**: 支持桌面端(1920x1080为主)

## 文件结构

```
finance-agent-web/src/
├── components/
│   ├── Chart/
│   │   ├── KLineChart.vue
│   │   ├── DupontChart.vue
│   │   ├── ValuationChart.vue
│   │   └── FinancialTrendChart.vue
│   └── Layout/
│       ├── AppSidebar.vue
│       ├── AppHeader.vue
│       └── MainLayout.vue
└── views/Report/components/
    ├── FinancialCard.vue
    ├── ValuationCard.vue
    ├── SentimentCard.vue
    └── CatalystCard.vue
```

## 实施顺序

1. 布局组件 (AppSidebar, AppHeader, MainLayout)
2. 图表组件 (KLineChart, ValuationChart等)
3. 报告子组件 (FinancialCard, ValuationCard等)
4. 集成到Report页面
