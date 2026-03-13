"""重试机制模块"""
import asyncio
import random
from typing import Callable, TypeVar, Any
from functools import wraps


T = TypeVar("T")


class RetryPolicy:
    """重试策略"""

    def __init__(self, max_retries: int = 3, min_wait: int = 1, max_wait: int = 60):
        self.max_retries = max_retries
        self.min_wait = min_wait
        self.max_wait = max_wait

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False

        non_retryable = (ValueError, TypeError, KeyError)
        if isinstance(exception, non_retryable):
            return False

        return True

    def get_wait_time(self, attempt: int) -> int:
        """计算等待时间（指数退避）"""
        wait = min(self.max_wait, self.min_wait * (2**attempt))
        return wait + random.randint(0, wait // 4)


def with_retry(max_attempts: int = 3):
    """重试装饰器"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = min(60, 2**attempt)
                        await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper

    return decorator
