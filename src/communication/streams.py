"""Redis Streams通信模块"""
from typing import Dict, Any, Optional, List, Callable
import json
from src.communication.redis_client import RedisClient


class StreamManager:
    """Stream管理器"""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()

    def publish_task(self, stream_key: str, task: Dict[str, Any]) -> str:
        """发布任务到Stream

        Args:
            stream_key: Stream键名
            task: 任务数据

        Returns:
            消息ID
        """
        return self.redis.xadd(stream_key, task)

    def create_consumer_group(self, stream_key: str, group_name: str):
        """创建消费者组"""
        try:
            self.redis.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise

    def consume(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        count: int = 1,
        block: int = 5000,
    ) -> List[Dict[str, Any]]:
        """消费消息

        Args:
            stream_key: Stream键名
            group_name: 消费者组名
            consumer_name: 消费者名
            count: 每次获取数量
            block: 阻塞超时(毫秒)

        Returns:
            消息列表
        """
        messages = self.redis.xreadgroup(
            groupname=group_name,
            consumername=consumer_name,
            streams={stream_key: ">"},
            count=count,
            block=block,
        )

        if not messages:
            return []

        results = []
        for stream_name, stream_messages in messages:
            for msg_id, msg_data in stream_messages:
                results.append({"id": msg_id, "data": msg_data})

        return results

    def ack(self, stream_key: str, group_name: str, message_id: str) -> bool:
        """确认消息"""
        return self.redis.xack(stream_key, group_name, message_id)

    def get_pending(self, stream_key: str, group_name: str) -> List[Dict[str, Any]]:
        """获取待处理消息"""
        return self.redis.xpending(stream_key, group_name)
