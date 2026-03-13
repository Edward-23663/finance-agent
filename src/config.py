"""配置管理模块"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""

    project_dir: str = os.path.expanduser("~/.finance_agent")

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    max_retries: int = 3
    retry_delay: int = 5

    log_level: str = "INFO"

    tushare_token: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
