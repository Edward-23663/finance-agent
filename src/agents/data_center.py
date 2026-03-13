"""数据中心Agent"""
import asyncio
from typing import Dict, Any, List, Optional
import json
import time

from src.agents.base import BaseAgent, AgentConfig
from src.data.duckdb_client import DuckDBClient
from src.data.lancedb_client import LanceDBClient
from src.communication.redis_client import RedisClient


class DataCenterAgent(BaseAgent):
    """数据中心Agent - 负责本地数据湖的统一管理"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.duckdb = DuckDBClient()
        self.lancedb = LanceDBClient()
        self.redis = RedisClient()
        self._locks: Dict[str, asyncio.Lock] = {}

    async def execute(self, task_data: Dict[str, Any]) -> Any:
        """执行数据中心任务"""
        task_type = task_data.get("type")

        if task_type == "query_price":
            return await self._query_price(
                task_data.get("ticker"),
                task_data.get("start_date"),
                task_data.get("end_date"),
            )
        elif task_type == "query_financial":
            return await self._query_financial(
                task_data.get("ticker"),
                task_data.get("period"),
            )
        elif task_type == "query_stock_info":
            return await self._query_stock_info(task_data.get("ticker"))
        elif task_type == "query_industry":
            return await self._query_industry(task_data.get("industry"))
        elif task_type == "cache_get":
            return await self._cache_get(task_data.get("key"))
        elif task_type == "cache_set":
            return await self._cache_set(
                task_data.get("key"),
                task_data.get("value"),
                task_data.get("ttl", 300),
            )
        elif task_type == "query_vector":
            return await self._query_vector(
                task_data.get("text"),
                task_data.get("top_k", 5),
            )
        elif task_type == "data_lake_manage":
            return await self._data_lake_manage(task_data)
        elif task_type == "dispatch_data_access":
            return await self._dispatch_data_access(task_data)
        elif task_type == "aggregate_query":
            return await self._aggregate_query(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _query_price(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """查询行情数据"""
        cache_key = f"price:{ticker}:{start_date}:{end_date}"
        cached = await self.redis.get(cache_key)
        if cached:
            return {"status": "success", "data": json.loads(cached), "source": "cache"}

        query = """
            SELECT ticker, trade_date, open, high, low, close, volume, amount
            FROM price_daily
            WHERE ticker = ? AND trade_date >= ? AND trade_date <= ?
            ORDER BY trade_date
        """
        result = self.duckdb.execute(query, [ticker, start_date, end_date])

        data = [dict(row) for row in result]
        if data:
            await self.redis.set(cache_key, json.dumps(data), ttl=300)

        return {"status": "success", "data": data, "count": len(data)}

    async def _query_financial(self, ticker: str, period: Optional[str] = None) -> Dict[str, Any]:
        """查询财务数据"""
        if period:
            query = """
                SELECT * FROM financial_metrics
                WHERE ticker = ? AND report_date = ?
                ORDER BY report_date DESC
            """
            result = self.duckdb.execute(query, [ticker, period])
        else:
            query = """
                SELECT * FROM financial_metrics
                WHERE ticker = ?
                ORDER BY report_date DESC
            """
            result = self.duckdb.execute(query, [ticker])

        data = [dict(row) for row in result]
        return {"status": "success", "data": data, "count": len(data)}

    async def _query_stock_info(self, ticker: str) -> Dict[str, Any]:
        """查询股票基本信息"""
        query = "SELECT * FROM stock_info WHERE ticker = ?"
        result = self.duckdb.execute(query, [ticker])

        data = [dict(row) for row in result]
        if data:
            return {"status": "success", "data": data[0]}
        return {"status": "success", "data": None}

    async def _query_industry(self, industry: str) -> Dict[str, Any]:
        """查询行业分类数据"""
        query = "SELECT * FROM stock_info WHERE industry = ?"
        result = self.duckdb.execute(query, [industry])

        data = [dict(row) for row in result]
        return {"status": "success", "data": data, "count": len(data)}

    async def _cache_get(self, key: str) -> Dict[str, Any]:
        """获取缓存数据"""
        value = await self.redis.get(key)
        if value:
            return {"status": "success", "value": value}
        return {"status": "success", "value": None}

    async def _cache_set(self, key: str, value: str, ttl: int = 300) -> Dict[str, Any]:
        """设置缓存"""
        await self.redis.set(key, value, ttl=ttl)
        return {"status": "success", "key": key, "ttl": ttl}

    async def _query_vector(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        """向量相似度检索"""
        results = self.lancedb.search(text, top_k)
        return {"status": "success", "results": results}

    async def _data_lake_manage(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """数据湖管理"""
        operation = task_data.get("operation")
        tickers = task_data.get("tickers", [])
        data_types = task_data.get("data_types", [])

        if "data_lake" not in self._locks:
            self._locks["data_lake"] = asyncio.Lock()

        lock = self._locks["data_lake"]
        await lock.acquire()
        try:
            results = {}
            start_time = time.time()

            for ticker in tickers:
                results[ticker] = {}

                if "price" in data_types:
                    count = self.duckdb.execute(
                        "SELECT COUNT(*) FROM price_daily WHERE ticker = ?", [ticker]
                    )
                    results[ticker]["price"] = count[0]["count"] if count else 0

                if "financial" in data_types:
                    count = self.duckdb.execute(
                        "SELECT COUNT(*) FROM financial_metrics WHERE ticker = ?",
                        [ticker],
                    )
                    results[ticker]["financial"] = count[0]["count"] if count else 0

                if "info" in data_types:
                    count = self.duckdb.execute(
                        "SELECT COUNT(*) FROM stock_info WHERE ticker = ?", [ticker]
                    )
                    results[ticker]["info"] = count[0]["count"] if count else 0

            duration = time.time() - start_time

            return {
                "status": "success",
                "operation": operation,
                "processed": len(tickers),
                "records": results,
                "duration_seconds": round(duration, 2),
            }
        finally:
            lock.release()

    async def _dispatch_data_access(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """多智能体数据访问调度"""
        agent_id = task_data.get("agent_id")
        tickers = task_data.get("tickers", [])
        data_types = task_data.get("data_types", [])
        priority = task_data.get("priority", "normal")

        dispatch_key = f"dispatch:{agent_id}:{int(time.time())}"
        dispatch_data = {
            "agent_id": agent_id,
            "tickers": tickers,
            "data_types": data_types,
            "priority": priority,
            "timestamp": time.time(),
        }

        await self.redis.set(dispatch_key, json.dumps(dispatch_data), ttl=3600)

        results = {}
        for ticker in tickers:
            results[ticker] = {}
            if "price" in data_types:
                result = self.duckdb.execute(
                    "SELECT COUNT(*) FROM price_daily WHERE ticker = ?", [ticker]
                )
                results[ticker]["price"] = result[0]["count"] if result else 0

            if "financial" in data_types:
                result = self.duckdb.execute(
                    "SELECT COUNT(*) FROM financial_metrics WHERE ticker = ?", [ticker]
                )
                results[ticker]["financial"] = result[0]["count"] if result else 0

        return {
            "status": "success",
            "agent_id": agent_id,
            "priority": priority,
            "results": results,
        }

    async def _aggregate_query(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """跨源数据聚合查询"""
        ticker = task_data.get("ticker")
        metrics = task_data.get("metrics", [])
        date_range = task_data.get("date_range", {})

        aggregated = {}

        if "price" in metrics:
            start = date_range.get("start", "2020-01-01")
            end = date_range.get("end", "2024-12-31")
            result = self.duckdb.execute(
                """SELECT * FROM price_daily 
                   WHERE ticker = ? AND trade_date >= ? AND trade_date <= ?
                   ORDER BY trade_date""",
                [ticker, start, end],
            )
            aggregated["price"] = [dict(row) for row in result]

        if "financial" in metrics:
            result = self.duckdb.execute(
                "SELECT * FROM financial_metrics WHERE ticker = ? ORDER BY report_date", [ticker]
            )
            aggregated["financial"] = [dict(row) for row in result]

        if "news" in metrics:
            results = self.lancedb.search(f"{ticker} news", top_k=10)
            aggregated["news"] = results

        return {
            "status": "success",
            "ticker": ticker,
            "aggregated_data": aggregated,
            "data_sources": ["duckdb", "lancedb"],
        }

    async def _acquire_lock(self, resource: str):
        """获取锁"""
        if resource not in self._locks:
            self._locks[resource] = asyncio.Lock()

        await self._locks[resource].acquire()

        class LockContext:
            def __init__(self, lock):
                self._lock = lock

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                self._lock.release()

        return LockContext(self._locks[resource])

    async def _release_lock(self, resource: str):
        """释放锁"""
        if resource in self._locks and self._locks[resource].locked():
            self._locks[resource].release()
