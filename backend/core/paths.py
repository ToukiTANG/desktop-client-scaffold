import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_project_root() -> Path:
    if is_frozen():
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def get_backend_root() -> Path:
    return get_project_root() / "backend"


def get_frontend_dist() -> Path:
    return get_project_root() / "frontend" / "dist"


def get_data_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent / "data"

    return get_backend_root() / "data"