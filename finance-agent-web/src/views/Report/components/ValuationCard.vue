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
import { computed } from 'vue';

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
