"""任务管理API路由"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from src.api.deps import verify_api_key, get_orchestrator

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskRequest(BaseModel):
    """创建任务请求"""

    ticker: str
    user_input: str
    dimensions: List[str] = ["fundamental", "valuation"]
    options: Optional[dict] = {}


class TaskResponse(BaseModel):
    """任务响应"""

    trace_id: str
    status: str
    created_at: datetime


@router.post("", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    api_key: str = Depends(verify_api_key),
) -> TaskResponse:
    """创建分析任务"""
    trace_id = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"

    orchestrator = get_orchestrator()
    await orchestrator.submit_task(
        trace_id=trace_id,
        user_input=request.user_input,
        ticker=request.ticker,
        dimensions=request.dimensions,
    )

    return TaskResponse(trace_id=trace_id, status="pending", created_at=datetime.now())


@router.get("/{trace_id}")
async def get_task(
    trace_id: str,
    api_key: str = Depends(verify_api_key),
):
    """获取任务状态和结果"""
    orchestrator = get_orchestrator()
    result = await orchestrator.get_task_result(trace_id)

    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    return result


@router.get("/health")
async def health_check():
    """健康检查"""
    import redis.asyncio as redis
    from src.data.duckdb_client import DuckDBClient

    checks = {"redis": False, "duckdb": False}

    try:
        r = redis.Redis(host="localhost", port=6379, db=0)
        await r.ping()
        checks["redis"] = True
        await r.close()
    except Exception:
        pass

    try:
        db = DuckDBClient()
        db.query("SELECT 1")
        checks["duckdb"] = True
    except Exception:
        pass

    status = "healthy" if all(checks.values()) else "degraded"

    return {"status": status, "checks": checks}
