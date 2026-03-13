"""DuckDB客户端封装"""
import os
import duckdb
from typing import Any, List, Tuple, Optional
from pathlib import Path
from src.config import get_settings


class DuckDBClient:
    """DuckDB客户端封装"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "finance.duckdb")

        self.db_path = db_path
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    def connect(self) -> duckdb.DuckDBPyConnection:
        """连接数据库"""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def execute(self, query: str, params: Tuple = ()) -> Any:
        """执行SQL"""
        conn = self.connect()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)

    def execute_many(self, query: str, params_list: List[Tuple]):
        """批量执行"""
        conn = self.connect()
        conn.executemany(query, params_list)

    def fetchall(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """查询所有结果"""
        result = self.execute(query, params)
        return result.fetchall()

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """查询单条结果"""
        result = self.execute(query, params)
        return result.fetchone()

    def query_to_dicts(self, query: str, params: Tuple = ()) -> List[dict]:
        """查询并返回字典列表"""
        result = self.execute(query, params)
        columns = [desc[0] for desc in result.description] if result.description else []
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def query_financial_metrics(self, ticker: str, limit: int = 10) -> List[dict]:
        """查询财务指标"""
        query = f"""
            SELECT * FROM financial_metrics 
            WHERE ticker = '{ticker}'
            ORDER BY report_date DESC
            LIMIT {limit}
        """
        return self.query_to_dicts(query)

    def query_price_latest(self, ticker: str) -> List[dict]:
        """查询最新价格"""
        query = f"""
            SELECT * FROM price_daily 
            WHERE ticker = '{ticker}'
            ORDER BY trade_date DESC
            LIMIT 1
        """
        return self.query_to_dicts(query)

    def query_price_range(self, ticker: str, start_date: str, end_date: str) -> List[dict]:
        """查询日期范围价格"""
        query = f"""
            SELECT * FROM price_daily 
            WHERE ticker = '{ticker}'
            AND trade_date >= '{start_date}'
            AND trade_date <= '{end_date}'
            ORDER BY trade_date ASC
        """
        return self.query_to_dicts(query)

    def query_stock_info(self, ticker: str) -> List[dict]:
        """查询股票信息"""
        query = f"SELECT * FROM stock_info WHERE ticker = '{ticker}'"
        return self.query_to_dicts(query)

    def query_valuations(self, ticker: str) -> List[dict]:
        """查询估值数据"""
        query = f"""
            SELECT * FROM valuations 
            WHERE ticker = '{ticker}'
            ORDER BY valuation_date DESC
            LIMIT 1
        """
        return self.query_to_dicts(query)

    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
