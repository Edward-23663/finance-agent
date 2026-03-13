"""LanceDB客户端测试"""
import pytest
import os
import tempfile
import numpy as np
from src.data.lancedb_client import LanceDBClient


class TestLanceDBClient:
    """LanceDB客户端测试"""

    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "vectors")
            yield LanceDBClient(db_path)

    @pytest.mark.asyncio
    async def test_add_and_search(self, client):
        """测试添加和搜索向量"""
        vectors = [[0.1] * 384, [0.2] * 384]
        metadatas = [{"text": "test1"}, {"text": "test2"}]

        await client.add("test_table", vectors, metadatas)

        results = await client.search("test_table", [0.1] * 384, limit=2)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_delete_table(self, client):
        """测试删除表"""
        await client.add("to_delete", [[0.1] * 384], [{"text": "test"}])
        await client.delete_table("to_delete")

        tables = client.list_tables()
        assert "to_delete" not in tables
