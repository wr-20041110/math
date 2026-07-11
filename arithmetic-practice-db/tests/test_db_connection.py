"""数据库连接测试。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import pytest
import tempfile
import uuid
from db.connection import ConnectionManager, get_connection
from db.schema import create_schema, drop_schema


def _temp_db(name: str) -> str:
    """创建唯一临时数据库路径，每次测试用不同文件。"""
    uid = uuid.uuid4().hex[:8]
    return os.path.join(tempfile.gettempdir(), f"{name}_{uid}.db")


class TestConnectionManager:
    def test_singleton_behavior(self):
        """同路径返回同一实例。"""
        db_path = _temp_db("test_singleton")
        ConnectionManager.reset()
        cm1 = ConnectionManager(db_path)
        cm2 = ConnectionManager(db_path)
        assert cm1 is cm2
        cm1.close()

    def test_connection_is_valid(self):
        db_path = _temp_db("test_valid")
        ConnectionManager.reset()
        cm = ConnectionManager(db_path)
        conn = cm.connection
        result = conn.execute("SELECT 1 AS val").fetchone()
        assert result["val"] == 1
        cm.close()

    def test_transaction_rollback(self):
        db_path = _temp_db("test_rollback")
        ConnectionManager.reset()
        cm = ConnectionManager(db_path)
        create_schema(cm.connection)

        try:
            with cm.transaction() as c:
                c.execute("INSERT INTO students (name) VALUES (?)", ("test_rollback",))
                raise RuntimeError("forced error")
        except RuntimeError:
            pass

        row = cm.connection.execute(
            "SELECT * FROM students WHERE name = ?", ("test_rollback",)
        ).fetchone()
        assert row is None
        cm.close()

    def test_transaction_commit(self):
        db_path = _temp_db("test_commit")
        ConnectionManager.reset()
        cm = ConnectionManager(db_path)
        create_schema(cm.connection)

        with cm.transaction() as c:
            c.execute("INSERT INTO students (name) VALUES (?)", ("test_commit",))

        row = cm.connection.execute(
            "SELECT * FROM students WHERE name = ?", ("test_commit",)
        ).fetchone()
        assert row is not None
        assert row["name"] == "test_commit"
        cm.close()


class TestSchema:
    def test_create_and_drop(self):
        db_path = _temp_db("test_schema")
        ConnectionManager.reset()
        cm = ConnectionManager(db_path)

        create_schema(cm.connection)
        tables = cm.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {r["name"] for r in tables}
        assert "students" in table_names
        assert "exercises" in table_names
        assert "problems" in table_names
        assert "answers" in table_names
        assert "scores" in table_names

        drop_schema(cm.connection)
        tables = cm.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        assert len(tables) == 0

        cm.close()
