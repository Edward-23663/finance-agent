import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { TaskStatus, type SSEMessage, type TextChunkPayload } from '@/models/analysis';

export const useAnalysisStore = defineStore('analysis', () => {
  const currentTraceId = ref<string | null>(null);
  const taskStatus = ref<TaskStatus>(TaskStatus.PENDING);
  const progressPercentage = ref(0);
  const progressMessage = ref('');
  const reportContentMap = ref<Record<string, string>>({});
  const chartDataMap = ref<Record<string, any>>({});

  const isLoading = computed(() => 
    [TaskStatus.PENDING, TaskStatus.RUNNING].includes(taskStatus.value)
  );

  function resetState() {
    currentTraceId.value = null;
    taskStatus.value = TaskStatus.PENDING;
    progressPercentage.value = 0;
    progressMessage.value = '';
    reportContentMap.value = {};
    chartDataMap.value = {};
  }

  function setTraceId(id: string) {
      resetState();
      currentTraceId.value = id;
  }

  function processSSEMessage(message: SSEMessage) {
    if (message.trace_id !== currentTraceId.value) return;

    switch (message.type) {
      case 'status_change':
        taskStatus.value = message.payload.status;
        break;
        
      case 'progress':
        progressPercentage.value = message.payload.percentage;
        progressMessage.value = message.payload.message;
        break;

      case 'chunk':
        const agentName = message.agent_name || 'default';
        const chunkPayload = message.payload as TextChunkPayload;
        
        if (!reportContentMap.value[agentName]) {
            reportContentMap.value[agentName] = '';
        }
        reportContentMap.value[agentName] += chunkPayload.text;
        break;

      case 'result':
        if (message.payload.chart_data) {
            chartDataMap.value = { ...chartDataMap.value, ...message.payload.chart_data };
        }
        break;
        
      case 'error':
        taskStatus.value = TaskStatus.FAILED;
        progressMessage.value = `Error: ${message.payload.error_msg}`;
        break;
    }
  }

  return {
    currentTraceId,
    taskStatus,
    progressPercentage,
    progressMessage,
    reportContentMap,
    chartDataMap,
    isLoading,
    setTraceId,
    processSSEMessage,
    resetState
  };
});
