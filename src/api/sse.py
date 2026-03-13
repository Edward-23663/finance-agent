"""SSE流式推送模块"""
from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import redis.asyncio as redis
import json
import asyncio

router = APIRouter()


async def event_generator(trace_id: str, request: Request) -> AsyncGenerator[str, None]:
    """SSE事件流生成器"""
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    channel = f"stream:{trace_id}"

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    try:
        while True:
            if await request.is_disconnected():
                break

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

            if message and message.get("type") == "message":
                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode()

                yield f"data: {data}\n\n"

    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis_client.close()


@router.get("/stream/{trace_id}")
async def stream(trace_id: str, request: Request):
    """SSE流式端点"""

    async def event_publisher():
        async for event in event_generator(trace_id, request):
            yield event

    return StreamingResponse(
        event_publisher(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
