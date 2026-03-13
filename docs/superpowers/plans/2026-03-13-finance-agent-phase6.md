# Phase 6 Web UI 组件完善实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完善金融分析Web UI的图表组件、布局组件和报告子组件

**Architecture:** 使用ECharts作为图表库，Element Plus作为UI组件库，采用经典后台管理布局

**Tech Stack:** Vue 3 + TypeScript + ECharts 5.x + Element Plus

---

## 准备阶段

- [ ] 安装ECharts依赖

```bash
cd /home/jianwei/project1/finance-agent-web && npm install echarts vue-echarts @types/echarts
```

---

## Chunk 1: 布局组件

### Task 1: AppSidebar 左侧导航

**Files:**
- Create: `src/components/Layout/AppSidebar.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-aside width="200px" class="app-sidebar">
    <div class="logo">
      <h3>金融分析AI</h3>
    </div>
    <el-menu
      :default-active="activeMenu"
      router
      class="sidebar-menu"
    >
      <el-menu-item index="/">
        <el-icon><House /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/report">
        <el-icon><Document /></el-icon>
        <span>分析报告</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { House, Document } from '@element-plus/icons-vue';

const route = useRoute();
const activeMenu = computed(() => route.path);
</script>

<style scoped lang="scss">
.app-sidebar {
  background: #304156;
  height: 100vh;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #2b3a4a;
    
    h3 {
      color: #fff;
      font-size: 18px;
      margin: 0;
    }
  }
  
  .sidebar-menu {
    border-right: none;
    background: #304156;
    
    :deep(.el-menu-item) {
      color: #bfcbd9;
      
      &:hover {
        background: #263445;
        color: #409eff;
      }
      
      &.is-active {
        background: #409eff;
        color: #fff;
      }
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Layout/AppSidebar.vue
git commit -m "feat(web): 添加AppSidebar左侧导航组件"
```

---

### Task 2: AppHeader 顶部导航

**Files:**
- Create: `src/components/Layout/AppHeader.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRoute">{{ currentRoute }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-icon><User /></el-icon>
          <span>用户</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>设置</el-dropdown-item>
            <el-dropdown-item divided>退出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { User } from '@element-plus/icons-vue';

const route = useRoute();
const currentRoute = computed(() => route.meta?.title as string);
</script>

<style scoped lang="scss">
.app-header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    font-size: 14px;
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 5px;
      cursor: pointer;
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Layout/AppHeader.vue
git commit -m "feat(web): 添加AppHeader顶部导航组件"
```

---

### Task 3: MainLayout 主布局容器

**Files:**
- Create: `src/components/Layout/MainLayout.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-container class="main-layout">
    <AppSidebar />
    <el-container>
      <AppHeader />
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
import AppHeader from './AppHeader.vue';
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  
  .main-content {
    background: #f0f2f5;
    padding: 20px;
    min-height: calc(100vh - 60px);
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Layout/MainLayout.vue
git commit -m "feat(web): 添加MainLayout主布局容器"
```

---

## Chunk 2: 图表组件

### Task 4: KLineChart K线图

**Files:**
- Create: `src/components/Chart/KLineChart.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <div class="kline-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 400px" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { CandlestickChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, CandlestickChart, GridComponent, TooltipComponent, DataZoomComponent]);

interface KLineData {
  date: string;
  open: number;
  close: number;
  low: number;
  high: number;
  volume: number;
}

const props = defineProps<{
  data: KLineData[];
}>();

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  grid: [{ left: '10%', right: '10%', height: '50%' }, { left: '10%', right: '10%', top: '65%', height: '20%' }],
  xAxis: [
    { type: 'category', data: props.data.map(d => d.date), gridIndex: 0 },
    { type: 'category', data: props.data.map(d => d.date), gridIndex: 1 }
  ],
  yAxis: [
    { scale: true, gridIndex: 0 },
    { scale: true, gridIndex: 1, name: '成交量' }
  ],
  series: [
    {
      type: 'candlestick',
      data: props.data.map(d => [d.open, d.close, d.low, d.high]),
      itemStyle: { color: '#ef232a', color0: '#14b143', borderColor: '#ef232a', borderColor0: '#14b143' }
    },
    {
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: props.data.map(d => d.volume)
    }
  ]
}));
</script>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Chart/KLineChart.vue
git commit -m "feat(web): 添加KLineChart K线图组件"
```

---

### Task 5: ValuationChart 估值对比图

**Files:**
- Create: `src/components/Chart/ValuationChart.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <div class="valuation-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 350px" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent]);

interface ValuationModel {
  name: string;
  value: number;
}

const props = defineProps<{
  data: ValuationModel[];
  currentPrice?: number;
}>();

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['估值', '当前价格'] },
  xAxis: { type: 'category', data: props.data.map(d => d.name) },
  yAxis: { type: 'value', name: '价格(元)' },
  series: [
    {
      name: '估值',
      type: 'bar',
      data: props.data.map(d => d.value),
      itemStyle: { color: '#409eff' }
    },
    ...(props.currentPrice ? [{
      name: '当前价格',
      type: 'line',
      data: props.data.map(() => props.currentPrice),
      itemStyle: { color: '#e6a23c' },
      lineStyle: { type: 'dashed' }
    }] : [])
  ]
}));
</script>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Chart/ValuationChart.vue
git commit -m "feat(web): 添加ValuationChart估值对比图组件"
```

---

### Task 6: FinancialTrendChart 财务趋势图

**Files:**
- Create: `src/components/Chart/FinancialTrendChart.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <div class="financial-trend-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 300px" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent]);

interface TrendPoint {
  period: string;
  revenue?: number;
  profit?: number;
  roe?: number;
}

const props = defineProps<{
  data: TrendPoint[];
}>();

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['营收', '净利润', 'ROE'] },
  xAxis: { type: 'category', data: props.data.map(d => d.period) },
  yAxis: [
    { type: 'value', name: '金额(亿)', position: 'left' },
    { type: 'value', name: 'ROE(%)', position: 'right', min: 0, max: 50 }
  ],
  series: [
    { name: '营收', type: 'line', data: props.data.map(d => d.revenue), smooth: true },
    { name: '净利润', type: 'line', data: props.data.map(d => d.profit), smooth: true },
    { name: 'ROE', type: 'line', yAxisIndex: 1, data: props.data.map(d => d.roe), smooth: true }
  ]
}));
</script>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Chart/FinancialTrendChart.vue
git commit -m "feat(web): 添加FinancialTrendChart财务趋势图组件"
```

---

### Task 7: DupontChart 杜邦分析图

**Files:**
- Create: `src/components/Chart/DupontChart.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <div class="dupont-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 300px" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

interface DupontItem {
  name: string;
  value: number;
}

const props = defineProps<{
  data: DupontItem[];
}>();

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}: {d}%' },
    data: props.data
  }]
}));
</script>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/Chart/DupontChart.vue
git commit -m "feat(web): 添加DupontChart杜邦分析图组件"
```

---

## Chunk 3: 报告子组件

### Task 8: FinancialCard 财务指标卡片

**Files:**
- Create: `src/views/Report/components/FinancialCard.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-card class="financial-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <el-tag size="small" :type="changeType">{{ changeText }}</el-tag>
      </div>
    </template>
    <div class="card-content">
      <div class="main-value">{{ formattedValue }}</div>
      <div class="sub-info">
        <span>同期: {{ previousValue }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';

const props = defineProps<{
  title: string;
  value: number;
  previousValue: string;
  unit?: string;
  change?: number;
}>();

const formattedValue = computed(() => {
  const val = props.value;
  return props.unit === '亿' ? `${(val / 100).toFixed(2)}亿` : val.toFixed(2);
});

const changeType = computed(() => {
  if (!props.change) return 'info';
  return props.change > 0 ? 'success' : 'danger';
});

const changeText = computed(() => {
  if (!props.change) return '';
  return `${props.change > 0 ? '+' : ''}${props.change.toFixed(1)}%`;
});
</script>

<style scoped lang="scss">
.financial-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card-content {
    text-align: center;
    .main-value {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
      margin: 10px 0;
    }
    .sub-info {
      color: #909399;
      font-size: 12px;
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/views/Report/components/FinancialCard.vue
git commit -m "feat(web): 添加FinancialCard财务指标卡片组件"
```

---

### Task 9: ValuationCard 估值结果卡片

**Files:**
- Create: `src/views/Report/components/ValuationCard.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-card class="valuation-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>{{ modelName }}</span>
        <el-tag size="small" :type="tagType">{{ tagText }}</el-tag>
      </div>
    </template>
    <div class="card-content">
      <div class="price-value">{{ price }}</div>
      <div class="price-unit">元/股</div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';

const props = defineProps<{
  modelName: string;
  price: number;
  currentPrice: number;
}>();

const tagType = computed(() => {
  const ratio = props.price / props.currentPrice;
  if (ratio > 1.2) return 'success';
  if (ratio < 0.8) return 'danger';
  return 'warning';
});

const tagText = computed(() => {
  const ratio = props.price / props.currentPrice;
  if (ratio > 1.2) return '高估';
  if (ratio < 0.8) return '低估';
  return '合理';
});
</script>

<style scoped lang="scss">
.valuation-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card-content {
    text-align: center;
    .price-value {
      font-size: 32px;
      font-weight: bold;
      color: #409eff;
    }
    .price-unit {
      color: #909399;
      font-size: 12px;
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/views/Report/components/ValuationCard.vue
git commit -m "feat(web): 添加ValuationCard估值结果卡片组件"
```

---

### Task 10: SentimentCard 舆情分析卡片

**Files:**
- Create: `src/views/Report/components/SentimentCard.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-card class="sentiment-card" shadow="hover">
    <template #header>
      <span>舆情分析</span>
    </template>
    <div class="sentiment-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="sentiment-item positive">
            <div class="count">{{ positive }}</div>
            <div class="label">正面</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sentiment-item neutral">
            <div class="count">{{ neutral }}</div>
            <div class="label">中性</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sentiment-item negative">
            <div class="count">{{ negative }}</div>
            <div class="label">负面</div>
          </div>
        </el-col>
      </el-row>
      <div class="summary">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ summary }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { WarningFilled } from '@element-plus/icons-vue';

defineProps<{
  positive: number;
  neutral: number;
  negative: number;
  summary: string;
}>();
</script>

<style scoped lang="scss">
.sentiment-card {
  .sentiment-content {
    .sentiment-item {
      text-align: center;
      padding: 15px 0;
      border-radius: 8px;
      
      &.positive { background: #f0f9eb; }
      &.neutral { background: #f4f4f5; }
      &.negative { background: #fef0f0; }
      
      .count {
        font-size: 24px;
        font-weight: bold;
      }
      .label {
        font-size: 12px;
        color: #909399;
      }
    }
    .summary {
      margin-top: 15px;
      padding: 10px;
      background: #fdf6ec;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #e6a23c;
      font-size: 13px;
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/views/Report/components/SentimentCard.vue
git commit -m "feat(web): 添加SentimentCard舆情分析卡片组件"
```

---

### Task 11: CatalystCard 催化剂信息卡片

**Files:**
- Create: `src/views/Report/components/CatalystCard.vue`

- [ ] **Step 1: 创建组件文件**

```vue
<template>
  <el-card class="catalyst-card" shadow="hover">
    <template #header>
      <span>催化剂分析</span>
    </template>
    <div class="catalyst-content">
      <el-timeline>
        <el-timeline-item
          v-for="item in catalysts"
          :key="item.id"
          :timestamp="item.date"
          :type="item.type"
          :hollow="item.hollow"
        >
          <h4>{{ item.title }}</h4>
          <p>{{ item.description }}</p>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

interface Catalyst {
  id: number;
  date: string;
  title: string;
  description: string;
  type?: 'primary' | 'success' | 'warning' | 'danger';
  hollow?: boolean;
}

defineProps<{
  catalysts: Catalyst[];
}>();
</script>

<style scoped lang="scss">
.catalyst-card {
  .catalyst-content {
    h4 {
      margin: 0 0 5px 0;
      font-size: 14px;
    }
    p {
      margin: 0;
      color: #606266;
      font-size: 12px;
    }
  }
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/views/Report/components/CatalystCard.vue
git commit -m "feat(web): 添加CatalystCard催化剂信息卡片组件"
```

---

## Chunk 4: 集成

### Task 12: 更新Report页面使用新组件

**Files:**
- Modify: `src/views/Report/index.vue`

- [ ] **Step 1: 导入并使用新组件**

在script中添加:
```typescript
import KLineChart from '@/components/Chart/KLineChart.vue';
import ValuationChart from '@/components/Chart/ValuationChart.vue';
import FinancialCard from './components/FinancialCard.vue';
import ValuationCard from './components/ValuationCard.vue';
```

在模板中添加组件使用示例

- [ ] **Step 2: 提交**

```bash
git add src/views/Report/index.vue
git commit -m "feat(web): 集成图表和卡片组件到Report页面"
```

---

### Task 13: 最终测试与提交

- [ ] **Step 1: 运行构建测试**

```bash
cd /home/jianwei/project1/finance-agent-web && npm run build
```

- [ ] **Step 2: 推送到远程**

```bash
git push origin main
```

---

**计划完成，共13个任务**
