"""LanceDB向量存储客户端"""
import os
from typing import List, Dict, Any, Optional
import lancedb
from pathlib import Path
from src.config import get_settings


class LanceDBClient:
    """LanceDB向量存储客户端"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "vectors")

        self.db_path = db_path
        self._db = None

    def get_db(self):
        """获取数据库连接"""
        if self._db is None:
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(self.db_path)
        return self._db

    async def add(
        self, table_name: str, vectors: List[List[float]], metadatas: List[Dict[str, Any]]
    ) -> None:
        """添加向量数据"""
        import asyncio

        db = self.get_db()

        data = [{"vector": vec, **meta} for vec, meta in zip(vectors, metadatas)]

        def _add_sync():
            try:
                tbl = db.open_table(table_name)
                tbl.add(data)
            except Exception:
                db.create_table(table_name, data)

        await asyncio.get_event_loop().run_in_executor(None, _add_sync)

    async def search(
        self, table_name: str, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索向量"""
        import asyncio

        db = self.get_db()

        def _search_sync():
            try:
                tbl = db.open_table(table_name)
                results = tbl.search(query_vector).limit(limit).to_list()
                return results
            except Exception:
                return []

        return await asyncio.get_event_loop().run_in_executor(None, _search_sync)

    def list_tables(self) -> List[str]:
        """列出所有表"""
        db = self.get_db()
        return db.table_names()

    async def delete_table(self, table_name: str) -> None:
        """删除表"""
        import asyncio

        db = self.get_db()

        def _delete_sync():
            try:
                db.drop_table(table_name)
            except Exception:
                pass

        await asyncio.get_event_loop().run_in_executor(None, _delete_sync)

    async def get_table_count(self, table_name: str) -> int:
        """获取表的向量数量"""
        import asyncio

        db = self.get_db()

        def _count_sync():
            try:
                tbl = db.open_table(table_name)
                return tbl.count_rows()
            except Exception:
                return 0

        return await asyncio.get_event_loop().run_in_executor(None, _count_sync)

    def close(self):
        """关闭连接"""
        self._db = None
