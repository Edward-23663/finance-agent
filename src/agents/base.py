"""Agent基类模块"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.communication.redis_client import RedisClient
from src.communication.streams import StreamManager
from src.orchestrator.state_machine import TaskStateMachine, TaskState


@dataclass
class AgentConfig:
    """Agent配置"""

    name: str
    stream_key: str
    consumer_group: str
    max_retries: int = 3


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.redis = RedisClient()
        self.streams = StreamManager(self.redis)
        self.state_machine = TaskStateMachine(self.redis)
        self._running = False

    async def start(self):
        """启动Agent"""
        self._running = True

        self.streams.create_consumer_group(self.config.stream_key, self.config.consumer_group)

        asyncio.create_task(self._consume_loop())

    async def stop(self):
        """停止Agent"""
        self._running = False

    async def _consume_loop(self):
        """消费循环"""
        while self._running:
            try:
                messages = self.streams.consume(
                    self.config.stream_key, self.config.consumer_group, self.config.name
                )

                for message in messages:
                    await self._process_message(message)

            except Exception as e:
                print(f"Error in consume loop: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message: Dict[str, Any]):
        """处理消息"""
        msg_id = message.get("id")
        data = message.get("data", {})

        trace_id = data.get("trace_id")
        task_type = data.get("type")

        try:
            self.state_machine.transition(trace_id, TaskState.RUNNING)

            result = await self.execute(data)

            self.state_machine.transition(trace_id, TaskState.COMPLETED)
            self.streams.ack(self.config.stream_key, self.config.consumer_group, msg_id)

        except Exception as e:
            self.state_machine.transition(trace_id, TaskState.FAILED, str(e))
            self.streams.ack(self.config.stream_key, self.config.consumer_group, msg_id)

    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行任务"""
        pass
