"""重试机制测试"""
import pytest
import asyncio
from unittest.mock import AsyncMock
from src.orchestrator.retry import RetryPolicy, with_retry


class TestRetryPolicy:
    """RetryPolicy 测试"""

    def test_default_values(self):
        """测试默认值"""
        policy = RetryPolicy()

        assert policy.max_retries == 3
        assert policy.min_wait == 1
        assert policy.max_wait == 60

    def test_should_retry_with_attempts_left(self):
        """测试还有重试次数时应该重试"""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry(0, Exception("test")) is True
        assert policy.should_retry(1, Exception("test")) is True
        assert policy.should_retry(2, Exception("test")) is True

    def test_should_retry_no_attempts_left(self):
        """测试没有重试次数时不应重试"""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry(3, Exception("test")) is False

    def test_should_not_retry_non_retryable_errors(self):
        """测试不可重试的错误类型"""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry(0, ValueError("test")) is False
        assert policy.should_retry(0, TypeError("test")) is False
        assert policy.should_retry(0, KeyError("test")) is False

    def test_get_wait_time_exponential_backoff(self):
        """测试指数退避计算"""
        policy = RetryPolicy(min_wait=1, max_wait=60)

        wait_0 = policy.get_wait_time(0)
        wait_1 = policy.get_wait_time(1)
        wait_2 = policy.get_wait_time(2)

        assert wait_0 < wait_1
        assert wait_1 < wait_2

    def test_get_wait_time_max_cap(self):
        """测试最大等待时间限制"""
        policy = RetryPolicy(min_wait=1, max_wait=10)

        wait = policy.get_wait_time(100)

        assert wait <= 12


class TestWithRetry:
    """with_retry 装饰器测试"""

    @pytest.mark.asyncio
    async def test_succeeds_first_attempt(self):
        """测试第一次尝试就成功"""
        mock_func = AsyncMock(return_value="success")
        decorated = with_retry(max_attempts=3)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_until_success(self):
        """测试重试直到成功"""
        mock_func = AsyncMock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        decorated = with_retry(max_attempts=3)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_exhaust_all_attempts(self):
        """测试耗尽所有重试次数"""
        mock_func = AsyncMock(side_effect=Exception("always fail"))
        decorated = with_retry(max_attempts=3)(mock_func)

        with pytest.raises(Exception, match="always fail"):
            await decorated()

        assert mock_func.call_count == 3
