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
import { computed } from 'vue';

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
