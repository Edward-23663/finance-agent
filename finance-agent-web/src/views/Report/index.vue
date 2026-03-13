<template>
  <div class="report-container">
    <el-card class="status-card" shadow="never">
      <div class="status-header">
        <h2 class="ticker-title">{{ ticker }} 分析报告</h2>
        <el-tag :type="statusTagType">{{ analysisStore.taskStatus }}</el-tag>
        <span class="trace-id">Trace ID: {{ traceId }}</span>
      </div>
      <el-progress 
        :percentage="analysisStore.progressPercentage" 
        :status="progressStatus"
        :stroke-width="18"
        text-inside
      />
      <p class="progress-msg">{{ analysisStore.progressMessage }}</p>
    </el-card>

    <div class="report-content">
      <el-tabs type="border-card" v-model="activeTab">
        <el-tab-pane label="综合摘要" name="summary">
          <div class="tab-content">
             <MdViewer :content="analysisStore.reportContentMap['summary_agent'] || '等待生成中...'" />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="基本面分析" name="fundamental" lazy>
           <div class="tab-content">
              <el-row :gutter="20">
                <el-col :span="16">
                    <MdViewer :content="analysisStore.reportContentMap['fundamental_agent'] || '正在进行基本面数据采集与计算...'" />
                </el-col>
                <el-col :span="8">
                    <el-card header="杜邦分析拆解" shadow="hover">
                        <div v-if="analysisStore.chartDataMap['dupont_chart']">
                            {{ analysisStore.chartDataMap['dupont_chart'] }}
                        </div>
                        <el-empty v-else description="图表数据计算中" image-size="60" />
                    </el-card>
                </el-col>
              </el-row>
           </div>
        </el-tab-pane>
        
        <el-tab-pane label="估值概览" name="valuation" lazy>
            <div class="tab-content">
                 <MdViewer :content="analysisStore.reportContentMap['valuation_agent'] || '正在运行多模型估值计算...'" />
            </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';
import { useAnalysisStore } from '@/stores/analysisStore';
import { useSSE } from '@/hooks/useSSE';
import { TaskStatus } from '@/models/analysis';

const MdViewer = defineAsyncComponent(() => import('@/components/Markdown/MdViewer.vue'));

const route = useRoute();
const analysisStore = useAnalysisStore();
const traceId = route.params.traceId as string;
const ticker = ref('Unknown Ticker');

const activeTab = ref('summary');
const { connect } = useSSE(traceId);

const statusTagType = computed(() => {
    switch (analysisStore.taskStatus) {
        case TaskStatus.RUNNING: return 'primary';
        case TaskStatus.COMPLETED: return 'success';
        case TaskStatus.FAILED: return 'danger';
        default: return 'info';
    }
});

const progressStatus = computed(() => {
     if (analysisStore.taskStatus === TaskStatus.FAILED) return 'exception';
     if (analysisStore.taskStatus === TaskStatus.COMPLETED) return 'success';
     return '';
})

onMounted(() => {
    if (analysisStore.currentTraceId !== traceId) {
        analysisStore.setTraceId(traceId);
    }
    connect();
});
</script>

<style scoped lang="scss">
.report-container {
  padding: 20px;

  .status-card {
    margin-bottom: 20px;
    .status-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        .ticker-title { margin: 0 15px 0 0; }
        .trace-id { margin-left: auto; color: #909399; font-size: 12px; font-family: monospace;}
    }
    .progress-msg {
        margin-top: 8px;
        color: #606266;
        font-size: 14px;
    }
  }

  .report-content {
    .tab-content {
        padding: 20px;
        min-height: 400px;
    }
  }
}
</style>
