<template>
  <div class="financial-trend-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 300px" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
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
