"""配置模块测试"""
import pytest
from src.config import Settings, get_settings


class TestSettings:
    """Settings 测试"""

    def test_default_values(self):
        """测试默认值"""
        settings = Settings()

        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.redis_db == 0
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.max_retries == 3
        assert settings.retry_delay == 5
        assert settings.log_level == "INFO"

    def test_custom_values_from_env(self, monkeypatch):
        """测试从环境变量覆盖"""
        monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
        monkeypatch.setenv("API_PORT", "9000")

        settings = Settings()

        assert settings.redis_host == "127.0.0.1"
        assert settings.api_port == 9000

    def test_get_settings_is_cached(self):
        """测试 get_settings 是单例缓存"""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
