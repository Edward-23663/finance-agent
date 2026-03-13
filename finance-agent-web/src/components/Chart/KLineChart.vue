<template>
  <div class="kline-chart">
    <v-chart :option="chartOption" :autoresize="true" style="height: 400px" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
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
  grid: [
    { left: '10%', right: '10%', height: '50%' },
    { left: '10%', right: '10%', top: '65%', height: '20%' }
  ],
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
      itemStyle: {
        color: '#ef232a',
        color0: '#14b143',
        borderColor: '#ef232a',
        borderColor0: '#14b143'
      }
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
