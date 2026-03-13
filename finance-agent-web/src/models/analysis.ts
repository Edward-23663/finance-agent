export enum AnalysisDimension {
  FUNDAMENTAL = 'fundamental',
  VALUATION = 'valuation',
  SENTIMENT = 'sentiment',
  INDUSTRY = 'industry',
}

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PARTIAL_SUCCESS = 'partial_success',
}

export interface SubmitTaskRequest {
  ticker: string;
  dimensions: AnalysisDimension[];
  params: {
    start_date?: string;
    end_date?: string;
    benchmark?: string;
  };
}

export interface SubmitTaskResponse {
  trace_id: string;
  status: TaskStatus;
}

export interface SSEMessage<T = any> {
  type: 'progress' | 'chunk' | 'result' | 'error' | 'status_change';
  trace_id: string;
  agent_name?: string;
  timestamp: number;
  payload: T;
}

export interface TextChunkPayload {
  text: string;
  is_finished: boolean;
}

export interface ProgressPayload {
  percentage: number;
  message: string;
}
