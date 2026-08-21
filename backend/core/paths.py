import os
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
        local_app_data = os.environ.get("LOCALAPPDATA")

        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA environment variable is unavailable")

        return Path(local_app_data) / "DesktopClient" / "data"

    return get_backend_root() / "data"


def get_log_dir() -> Path:
    if is_frozen():
        local_app_data = os.environ.get("LOCALAPPDATA")

        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA environment variable is unavailable")

        return Path(local_app_data) / "DesktopClient" / "logs"

    return get_backend_root() / "logs"
