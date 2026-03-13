"""DuckDB客户端测试"""
import pytest
import os
import tempfile
from src.data.duckdb_client import DuckDBClient


class TestDuckDBClient:
    """DuckDB客户端测试"""

    @pytest.fixture
    def client(self):
        """创建测试用DuckDB客户端"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield DuckDBClient(db_path)

    def test_connect(self, client):
        """测试连接"""
        result = client.execute("SELECT 1 as test")
        assert result.fetchone()[0] == 1

    def test_table_creation(self, client):
        """测试表创建"""
        from src.data.tables import create_all_tables

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
