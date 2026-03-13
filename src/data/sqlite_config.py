"""SQLite配置管理模块"""
import os
import sqlite3
import json
from typing import Any, Optional, Dict
from pathlib import Path
from src.config import get_settings


class SQLiteConfigManager:
    """SQLite配置管理器"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            db_path = os.path.join(settings.project_dir, "config.db")

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self.get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                key VARCHAR PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()

    def get_conn(self) -> sqlite3.Connection:
        """获取连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def set(self, key: str, value: Any) -> None:
        """设置配置"""
        conn = self.get_conn()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        conn = self.get_conn()
        cursor = conn.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row is None:
            return default

        value = row[0]
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def delete(self, key: str) -> None:
        """删除配置"""
        conn = self.get_conn()
        conn.execute("DELETE FROM config WHERE key = ?", (key,))
        conn.commit()

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        conn = self.get_conn()
        cursor = conn.execute("SELECT key, value FROM config")
        result = {}
        for row in cursor.fetchall():
            try:
                result[row[0]] = json.loads(row[1])
            except (json.JSONDecodeError, TypeError):
                result[row[0]] = row[1]
        return result

    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
