"""Redis客户端封装"""
import json
from typing import Any, Optional, List, Dict
import redis
from src.config import get_settings


class RedisClient:
    """Redis客户端封装"""

    def __init__(self):
        settings = get_settings()
        self._client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )

    def ping(self) -> bool:
        """Ping Redis"""
        return self._client.ping()

    def get(self, key: str) -> Optional[str]:
        """获取值"""
        return self._client.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """设置值"""
        if not isinstance(value, str):
            value = json.dumps(value)
        self._client.set(key, value, ex=ex)

    def delete(self, *keys: str):
        """删除键"""
        self._client.delete(*keys)

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return bool(self._client.exists(key))

    def hset(self, name: str, key: str, value: Any):
        """设置哈希"""
        if not isinstance(value, str):
            value = json.dumps(value)
        self._client.hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希值"""
        value = self._client.hget(name, key)
        return value

    def hgetall(self, name: str) -> Dict[str, str]:
        """获取所有哈希值"""
        return self._client.hgetall(name)

    def expire(self, key: str, seconds: int):
        """设置过期时间"""
        self._client.expire(key, seconds)

    def keys(self, pattern: str) -> List[str]:
        """查找键"""
        return self._client.keys(pattern)

    def xadd(self, stream: str, data: dict, id: str = "*") -> str:
        """添加消息到Stream"""
        return self._client.xadd(stream, data, id=id)

    def xreadgroup(
        self, groupname: str, consumername: str, streams: dict, count: int = 1, block: int = None
    ):
        """从消费者组读取消息"""
        return self._client.xreadgroup(
            groupname=groupname,
            consumername=consumername,
            streams=streams,
            count=count,
            block=block,
        )

    def xack(self, stream: str, groupname: str, *message_ids: str) -> int:
        """确认消息"""
        return self._client.xack(stream, groupname, *message_ids)

    def xgroup_create(self, stream: str, groupname: str, id: str = "0", mkstream: bool = False):
        """创建消费者组"""
        return self._client.xgroup_create(stream, groupname, id=id, mkstream=mkstream)

    def xpending(self, stream: str, groupname: str) -> dict:
        """获取待处理消息信息"""
        return self._client.xpending(stream, groupname)

    def xtrim(self, stream: str, maxlen: int, approximate: bool = True):
        """裁剪Stream"""
        return self._client.xtrim(stream, maxlen=maxlen, approximate=approximate)

    def xlen(self, stream: str) -> int:
        """获取Stream长度"""
        return self._client.xlen(stream)

    def lpush(self, key: str, *values: str) -> int:
        """将值推入列表左侧"""
        return self._client.lpush(key, *values)

    def rpop(self, key: str) -> Optional[str]:
        """从列表右侧弹出值"""
        return self._client.rpop(key)

    def brpop(self, keys: str, timeout: int = 0) -> Optional[tuple]:
        """从列表右侧阻塞弹出"""
        return self._client.brpop(keys, timeout)

    def xrange(self, stream: str, min_: str = "-", max_: str = "+", count: int = None) -> list:
        """获取Stream范围内的消息"""
        return self._client.xrange(stream, min=min_, max=max_, count=count)

    def close(self):
        """关闭连接"""
        self._client.close()
