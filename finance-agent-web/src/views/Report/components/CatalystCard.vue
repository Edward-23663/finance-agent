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
