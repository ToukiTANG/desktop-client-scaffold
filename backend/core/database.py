from contextlib import contextmanager
import sqlite3

from alembic import command
from alembic.config import Config

from core.paths import get_backend_root, get_data_dir

DATA_DIR = get_data_dir()
DB_PATH = DATA_DIR / "desktop.db"
ALEMBIC_INI_PATH = get_backend_root() / "alembic.ini"


def create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection():
    conn = create_connection()

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """初始化并升级数据库到最新版本。"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    config = Config(str(ALEMBIC_INI_PATH))

    command.upgrade(config, "head")
