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
