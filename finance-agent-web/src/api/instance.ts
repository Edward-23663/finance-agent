import axios from 'axios';
import type { SubmitTaskRequest, SubmitTaskResponse } from '@/models/analysis';

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL || '/api/v1';

const instance = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

instance.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const submitAnalysisTask = (data: SubmitTaskRequest) => {
  return instance.post<SubmitTaskResponse>('/tasks', data);
};

export const getTaskStatus = (traceId: string) => {
  return instance.get(`/tasks/${traceId}`);
};

export const getStockInfo = (ticker: string) => {
  return instance.get(`/stocks/${ticker}`);
};

export const getStockPrice = (ticker: string, startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  return instance.get(`/stocks/${ticker}/price?${params.toString()}`);
};

export default instance;
