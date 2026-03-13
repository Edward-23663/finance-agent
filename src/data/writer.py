"""DataWriter单线程写机制"""
import json
import asyncio
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from src.communication.redis_client import RedisClient
from src.data.duckdb_client import DuckDBClient
from src.data.tables import create_all_tables


class WriteTaskType(str, Enum):
    """写任务类型"""

    PRICE_DAILY = "price_daily"
    FINANCIAL_STATEMENT = "financial_statement"
    FINANCIAL_METRIC = "financial_metric"
    VALUATION = "valuation"
    NEWS_SENTIMENT = "news_sentiment"
    CATALYST_EVENT = "catalyst_event"
    STOCK_INFO = "stock_info"


@dataclass
class WriteTask:
    """写任务"""

    task_type: WriteTaskType
    data: Dict[str, Any]
    trace_id: Optional[str] = None

    def serialize(self) -> str:
        """序列化任务"""
        return json.dumps(asdict(self))

    @classmethod
    def deserialize(cls, data: str) -> "WriteTask":
        """反序列化任务"""
        obj = json.loads(data)
        return cls(
            task_type=WriteTaskType(obj["task_type"]),
            data=obj["data"],
            trace_id=obj.get("trace_id"),
        )


class DataWriter:
    """DataWriter单线程消费者"""

    QUEUE_KEY = "data:write:queue"

    def __init__(self, db_path: Optional[str] = None):
        self.redis = RedisClient()
        self.db = DuckDBClient(db_path)
        self._running = False

    def enqueue(self, task: WriteTask) -> None:
        """将写任务加入队列"""
        self.redis.lpush(self.QUEUE_KEY, task.serialize())

    async def run(self) -> None:
        """运行消费者循环"""
        self._running = True
        create_all_tables(self.db)

        while self._running:
            try:
                result = self.redis.brpop(self.QUEUE_KEY)
                if result:
                    _, task_data = result
                    task = WriteTask.deserialize(task_data)
                    await self.execute_write(task)
            except Exception as e:
                print(f"DataWriter error: {e}")
                await asyncio.sleep(1)

    async def execute_write(self, task: WriteTask) -> None:
        """执行写任务"""
        if task.task_type == WriteTaskType.PRICE_DAILY:
            await self._write_price_daily(task)
        elif task.task_type == WriteTaskType.FINANCIAL_STATEMENT:
            await self._write_financial_statement(task)
        elif task.task_type == WriteTaskType.FINANCIAL_METRIC:
            await self._write_financial_metric(task)
        elif task.task_type == WriteTaskType.VALUATION:
            await self._write_valuation(task)
        elif task.task_type == WriteTaskType.NEWS_SENTIMENT:
            await self._write_news_sentiment(task)
        elif task.task_type == WriteTaskType.CATALYST_EVENT:
            await self._write_catalyst_event(task)
        elif task.task_type == WriteTaskType.STOCK_INFO:
            await self._write_stock_info(task)

    async def _write_price_daily(self, task: WriteTask) -> None:
        """写入行情数据"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO price_daily 
            (ticker, trade_date, open, high, low, close, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["ticker"],
                data["trade_date"],
                data.get("open"),
                data.get("high"),
                data.get("low"),
                data.get("close"),
                data.get("volume"),
                data.get("amount"),
            ),
        )

    async def _write_financial_statement(self, task: WriteTask) -> None:
        """写入财务报表"""
        data = task.data
        self.db.execute(
            """
            INSERT INTO financial_statements 
            (ticker, report_date, report_type, version, revenue, net_profit, 
             total_assets, total_liabilities, equity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["ticker"],
                data["report_date"],
                data["report_type"],
                data.get("version", 1),
                data.get("revenue"),
                data.get("net_profit"),
                data.get("total_assets"),
                data.get("total_liabilities"),
                data.get("equity"),
            ),
        )

    async def _write_financial_metric(self, task: WriteTask) -> None:
        """写入财务指标"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO financial_metrics 
            (ticker, report_date, report_type, roe, roa, gross_margin, 
             net_margin, current_ratio, debt_ratio, eps, bps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["ticker"],
                data["report_date"],
                data["report_type"],
                data.get("roe"),
                data.get("roa"),
                data.get("gross_margin"),
                data.get("net_margin"),
                data.get("current_ratio"),
                data.get("debt_ratio"),
                data.get("eps"),
                data.get("bps"),
            ),
        )

    async def _write_valuation(self, task: WriteTask) -> None:
        """写入估值数据"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO valuations 
            (ticker, valuation_date, pe, pb, ps, peg, dcf_value, ddm_value,
             fair_value_low, fair_value_mid, fair_value_high)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["ticker"],
                data["valuation_date"],
                data.get("pe"),
                data.get("pb"),
                data.get("ps"),
                data.get("peg"),
                data.get("dcf_value"),
                data.get("ddm_value"),
                data.get("fair_value_low"),
                data.get("fair_value_mid"),
                data.get("fair_value_high"),
            ),
        )

    async def _write_news_sentiment(self, task: WriteTask) -> None:
        """写入舆情数据"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO news_sentiment 
            (id, ticker, title, content, publish_date, sentiment_score, 
             sentiment_label, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["id"],
                data["ticker"],
                data.get("title"),
                data.get("content"),
                data.get("publish_date"),
                data.get("sentiment_score"),
                data.get("sentiment_label"),
                data.get("source"),
            ),
        )

    async def _write_catalyst_event(self, task: WriteTask) -> None:
        """写入催化剂事件"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO catalyst_events 
            (id, ticker, event_type, event_date, title, description,
             impact_score, impact_direction, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["id"],
                data["ticker"],
                data.get("event_type"),
                data.get("event_date"),
                data.get("title"),
                data.get("description"),
                data.get("impact_score"),
                data.get("impact_direction"),
                data.get("source"),
            ),
        )

    async def _write_stock_info(self, task: WriteTask) -> None:
        """写入股票信息"""
        data = task.data
        self.db.execute(
            """
            INSERT OR REPLACE INTO stock_info 
            (ticker, name, industry, list_date, market_type)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                data["ticker"],
                data.get("name"),
                data.get("industry"),
                data.get("list_date"),
                data.get("market_type"),
            ),
        )

    def stop(self) -> None:
        """停止消费者"""
        self._running = False
