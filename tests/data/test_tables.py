"""表结构测试"""
import pytest
import os
import tempfile
from src.data.duckdb_client import DuckDBClient
from src.data.tables import create_all_tables, STOCK_INFO_COLUMNS


class TestTableCreation:
    """表创建测试"""

    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield DuckDBClient(db_path)

    def test_stock_info_columns(self, client):
        """测试stock_info表字段"""
        expected = [
            "ticker VARCHAR PRIMARY KEY",
            "name VARCHAR",
            "industry VARCHAR",
            "list_date DATE",
            "market_type VARCHAR",
        ]
        assert STOCK_INFO_COLUMNS == expected

    def test_create_all_tables(self, client):
        """测试创建所有表"""
        create_all_tables(client)

        result = client.execute(
            """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'main'
        """
        )
        tables = [row[0] for row in result.fetchall()]

        assert "stock_info" in tables
        assert "price_daily" in tables
        assert "financial_statements" in tables
        assert "financial_metrics" in tables
        assert "valuations" in tables
        assert "news_sentiment" in tables
        assert "catalyst_events" in tables
        assert "task_history" in tables
