import { ref, onUnmounted } from 'vue';
import { useAnalysisStore } from '@/stores/analysisStore';
import type { SSEMessage } from '@/models/analysis';
import { ElMessage } from 'element-plus';

export function useSSE(traceId: string) {
  const eventSource = ref<EventSource | null>(null);
  const isConnected = ref(false);
  const analysisStore = useAnalysisStore();
  const sseBaseUrl = import.meta.env.VITE_APP_SSE_URL;

  const connect = () => {
    if (eventSource.value) {
        eventSource.value.close();
    }
    
    const url = `${sseBaseUrl}/${traceId}`;
    console.log(`[SSE] Connecting to: ${url}`);
    
    eventSource.value = new EventSource(url);

    eventSource.value.onopen = () => {
      console.log('[SSE] Connection opened.');
      isConnected.value = true;
    };

    eventSource.value.addEventListener('message', (event: MessageEvent) => {
      try {
        const message: SSEMessage = JSON.parse(event.data);
        handleMessage(message);
      } catch (e) {
        console.error('[SSE] Failed to parse message:', event.data);
      }
    });

    eventSource.value.onerror = (err) => {
      console.error('[SSE] Connection error:', err);
      isConnected.value = false;
      if (eventSource.value?.readyState === EventSource.CLOSED) {
           ElMessage.warning('服务器连接中断，正在尝试重连...');
       }
    };
  };

  const handleMessage = (message: SSEMessage) => {
    analysisStore.processSSEMessage(message);

    if (message.type === 'status_change') {
        if (['completed', 'failed'].includes(message.payload.status)) {
            close();
        }
    }
  };

  const close = () => {
    if (eventSource.value) {
      console.log('[SSE] Closing connection.');
      eventSource.value.close();
      eventSource.value = null;
      isConnected.value = false;
    }
  };

  onUnmounted(() => {
    close();
  });

  return {
    connect,
    close,
    isConnected,
  };
}
