<template>
  <div class="valuation-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 350px" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
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
