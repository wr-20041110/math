"""
ConnectionManager —— 数据库连接管理器。

设计要点：
  - 单例模式：全局共享一个连接管理器实例
  - 上下文管理器：自动 commit/rollback
  - WAL 模式：支持并发读写
  - 外键约束：显式启用
"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


class ConnectionManager:
    """SQLite 数据库连接管理器。

    线程安全的单例模式实现。
    """

    _instance: Optional["ConnectionManager"] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "data/mathpractice.db"):
        with cls._lock:
            if cls._instance is None:
                obj = super().__new__(cls)
                obj._db_path = Path(db_path)
                obj._db_path.parent.mkdir(parents=True, exist_ok=True)
                obj._init_connection()
                cls._instance = obj
        return cls._instance

    def _init_connection(self) -> None:
        """初始化数据库连接并配置。"""
        self._conn = sqlite3.connect(
            str(self._db_path),
            check_same_thread=False,  # 允许多线程
        )
        self._conn.row_factory = sqlite3.Row  # 字典式访问
        self._conn.execute("PRAGMA journal_mode=WAL")      # 写前日志
        self._conn.execute("PRAGMA foreign_keys=ON")        # 外键约束
        self._conn.execute("PRAGMA busy_timeout=5000")      # 锁等待 5s

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    @contextmanager
    def transaction(self):
        """事务上下文管理器。

        用法:
            with cm.transaction() as conn:
                conn.execute(...)
        """
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        """关闭连接。"""
        if self._conn:
            self._conn.close()

    @classmethod
    def reset(cls) -> None:
        """重置单例（测试用）。"""
        with cls._lock:
            if cls._instance:
                cls._instance.close()
                cls._instance = None


def get_connection() -> sqlite3.Connection:
    """获取数据库连接（便捷函数）。"""
    return ConnectionManager().connection
