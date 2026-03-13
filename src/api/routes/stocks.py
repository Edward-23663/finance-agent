"""股票数据查询API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from src.api.deps import verify_api_key

router = APIRouter(prefix="/stocks", tags=["stocks"])


class StockInfo(BaseModel):
    """股票基本信息"""

    ticker: str
    name: str
    industry: str
    list_date: Optional[date] = None
    market_type: Optional[str] = None


class PriceData(BaseModel):
    """行情数据"""

    ticker: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/{ticker}")
async def get_stock_info(
    ticker: str,
    api_key: str = Depends(verify_api_key),
):
    """获取股票基本信息"""
    from src.data.duckdb_client import DuckDBClient

    db = DuckDBClient()
    result = db.query(f"SELECT * FROM stock_info WHERE ticker = '{ticker}'")

    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")

    return result[0]


@router.get("/{ticker}/price")
async def get_price(
    ticker: str,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=500, description="返回条数"),
    api_key: str = Depends(verify_api_key),
):
    """获取行情数据"""
    from src.data.duckdb_client import DuckDBClient

    db = DuckDBClient()

    query = f"SELECT * FROM price_daily WHERE ticker = '{ticker}'"
    if start_date:
        query += f" AND trade_date >= '{start_date}'"
    if end_date:
        query += f" AND trade_date <= '{end_date}'"
    query += f" ORDER BY trade_date DESC LIMIT {limit}"

    result = db.query(query)
    return result


@router.get("/{ticker}/financial")
async def get_financial(
    ticker: str,
    report_type: Optional[str] = Query(None, description="报告类型: annual/quarterly"),
    api_key: str = Depends(verify_api_key),
):
    """获取财务数据"""
    from src.data.duckdb_client import DuckDBClient

    db = DuckDBClient()

    query = f"SELECT * FROM financial_metrics WHERE ticker = '{ticker}'"
    if report_type:
        query += f" AND report_type = '{report_type}'"
    query += " ORDER BY report_date DESC LIMIT 10"

    result = db.query(query)
    return result


@router.get("/{ticker}/valuation")
async def get_valuation(
    ticker: str,
    api_key: str = Depends(verify_api_key),
):
    """获取估值数据"""
    from src.data.duckdb_client import DuckDBClient

    db = DuckDBClient()
    result = db.query(
        f"SELECT * FROM valuations WHERE ticker = '{ticker}' ORDER BY valuation_date DESC LIMIT 1"
    )

    if not result:
        raise HTTPException(status_code=404, detail="Valuation data not found")

    return result[0]
