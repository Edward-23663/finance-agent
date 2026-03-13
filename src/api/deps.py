"""API依赖注入模块"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from src.config import get_settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """验证API Key"""
    settings = get_settings()

    if not settings.api_key:
        return "dev_key"

    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


def get_orchestrator():
    """获取主编排器实例"""
    from src.orchestrator.main import Orchestrator

    return Orchestrator()
