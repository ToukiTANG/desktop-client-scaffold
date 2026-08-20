from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

# backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent

# backend/data/
DATA_DIR = BACKEND_DIR / "data"

# backend/data/desktop.db
DB_PATH = DATA_DIR / "desktop.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    department TEXT NOT NULL,

    job_title TEXT NOT NULL,

    identity INTEGER NOT NULL,

    specialize_classify INTEGER NOT NULL,

    education TEXT,

    gender INTEGER NOT NULL,

    production_group_classify INTEGER,

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_person_name
ON person (name);


CREATE INDEX IF NOT EXISTS idx_person_department
ON person (department);


CREATE INDEX IF NOT EXISTS idx_person_identity
ON person (identity);


CREATE INDEX IF NOT EXISTS idx_person_specialize_classify
ON person (specialize_classify);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    创建一次数据库连接。

    每次业务操作独立创建连接，
    操作结束后自动 commit / rollback / close。
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=5.0)

    # 查询结果支持：
    # row["name"]
    # 而不是只能 row[0]
    conn.row_factory = sqlite3.Row

    # 每个连接都显式启用外键支持。
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def init_database() -> None:
    """
    初始化数据库。

    应用启动时执行一次。
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=5.0)

    try:
        # 桌面应用允许查询与写入具有更好的并发体验
        conn.execute("PRAGMA journal_mode = WAL")

        conn.executescript(SCHEMA_SQL)

        conn.commit()

    finally:
        conn.close()
