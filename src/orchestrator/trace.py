"""链路追踪模块"""
import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.communication.redis_client import RedisClient


def generate_trace_id() -> str:
    """生成Trace_ID"""
    return f"{int(time.time() * 1000):013d}-{uuid.uuid4().hex[:8]}"


class TraceManager:
    """链路追踪管理器"""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()

    def create_trace(self, trace_id: str, metadata: Optional[Dict[str, Any]] = None):
        """创建追踪"""
        key = f"trace:{trace_id}"
        data = {
            "trace_id": trace_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "started",
        }
        if metadata:
            data.update(metadata)
        self.redis.hset(key, "data", data)
        self.redis.expire(key, 86400)

    def add_span(
        self,
        trace_id: str,
        span_name: str,
        span_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """添加Span"""
        span_id = f"{trace_id}:{span_name}:{int(time.time() * 1000)}"
        span_key = f"span:{span_id}"

        span_data = {
            "span_id": span_id,
            "trace_id": trace_id,
            "name": span_name,
            "type": span_type,
            "start_time": datetime.utcnow().isoformat(),
        }
        if metadata:
            span_data.update(metadata)

        self.redis.hset(span_key, "data", span_data)
        self.redis.expire(span_key, 86400)

        return span_id

    def end_span(self, span_id: str, result: Optional[Dict[str, Any]] = None):
        """结束Span"""
        span_key = f"span:{span_id}"
        self.redis.hset(span_key, "end_time", datetime.utcnow().isoformat())
        if result:
            self.redis.hset(span_key, "result", result)

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """获取追踪信息"""
        key = f"trace:{trace_id}"
        data = self.redis.hgetall(key)
        return data

    def list_spans(self, trace_id: str) -> List[Dict[str, Any]]:
        """列出所有Span"""
        pattern = f"span:{trace_id}:*"
        span_keys = self.redis.keys(pattern)

        spans = []
        for span_key in span_keys:
            span = self.redis.hgetall(span_key)
            if span:
                spans.append(span)

        return spans
