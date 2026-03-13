"""数据表结构定义"""
from typing import List

STOCK_INFO_COLUMNS = [
    "ticker VARCHAR PRIMARY KEY",
    "name VARCHAR",
    "industry VARCHAR",
    "list_date DATE",
    "market_type VARCHAR",
]

PRICE_DAILY_COLUMNS = [
    "ticker VARCHAR",
    "trade_date DATE",
    "open DECIMAL(10,2)",
    "high DECIMAL(10,2)",
    "low DECIMAL(10,2)",
    "close DECIMAL(10,2)",
    "volume BIGINT",
    "amount DECIMAL(20,2)",
    "PRIMARY KEY (ticker, trade_date)",
]

FINANCIAL_STATEMENTS_COLUMNS = [
    "ticker VARCHAR",
    "report_date DATE",
    "report_type VARCHAR",
    "version INTEGER DEFAULT 1",
    "revenue DECIMAL(20,2)",
    "net_profit DECIMAL(20,2)",
    "total_assets DECIMAL(20,2)",
    "total_liabilities DECIMAL(20,2)",
    "equity DECIMAL(20,2)",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "PRIMARY KEY (ticker, report_date, report_type, version)",
]

FINANCIAL_METRICS_COLUMNS = [
    "ticker VARCHAR",
    "report_date DATE",
    "report_type VARCHAR",
    "roe DECIMAL(10,4)",
    "roa DECIMAL(10,4)",
    "gross_margin DECIMAL(10,4)",
    "net_margin DECIMAL(10,4)",
    "current_ratio DECIMAL(10,4)",
    "debt_ratio DECIMAL(10,4)",
    "eps DECIMAL(10,4)",
    "bps DECIMAL(10,4)",
    "PRIMARY KEY (ticker, report_date, report_type)",
]

VALUATIONS_COLUMNS = [
    "ticker VARCHAR",
    "valuation_date DATE",
    "pe DECIMAL(10,2)",
    "pb DECIMAL(10,2)",
    "ps DECIMAL(10,2)",
    "peg DECIMAL(10,2)",
    "dcf_value DECIMAL(20,2)",
    "ddm_value DECIMAL(20,2)",
    "fair_value_low DECIMAL(20,2)",
    "fair_value_mid DECIMAL(20,2)",
    "fair_value_high DECIMAL(20,2)",
    "PRIMARY KEY (ticker, valuation_date)",
]

NEWS_SENTIMENT_COLUMNS = [
    "id VARCHAR PRIMARY KEY",
    "ticker VARCHAR",
    "title TEXT",
    "content TEXT",
    "publish_date TIMESTAMP",
    "sentiment_score DECIMAL(5,4)",
    "sentiment_label VARCHAR",
    "source VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
]

CATALYST_EVENTS_COLUMNS = [
    "id VARCHAR PRIMARY KEY",
    "ticker VARCHAR",
    "event_type VARCHAR",
    "event_date DATE",
    "title TEXT",
    "description TEXT",
    "impact_score DECIMAL(5,2)",
    "impact_direction VARCHAR",
    "source VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
]

TASK_HISTORY_COLUMNS = [
    "trace_id VARCHAR PRIMARY KEY",
    "user_input TEXT",
    "status VARCHAR",
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "updated_at TIMESTAMP",
    "completed_at TIMESTAMP",
    "result JSON",
    "error_message TEXT",
]


def create_all_tables(client) -> None:
    """创建所有表"""
    tables = {
        "stock_info": STOCK_INFO_COLUMNS,
        "price_daily": PRICE_DAILY_COLUMNS,
        "financial_statements": FINANCIAL_STATEMENTS_COLUMNS,
        "financial_metrics": FINANCIAL_METRICS_COLUMNS,
        "valuations": VALUATIONS_COLUMNS,
        "news_sentiment": NEWS_SENTIMENT_COLUMNS,
        "catalyst_events": CATALYST_EVENTS_COLUMNS,
        "task_history": TASK_HISTORY_COLUMNS,
    }

    for table_name, columns in tables.items():
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        client.execute(query)
