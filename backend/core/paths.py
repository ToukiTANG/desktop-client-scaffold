from __future__ import annotations

import os
from pathlib import Path

from core.project_config import get_data_dir_name
from core.runtime_paths import get_project_root, is_frozen


def get_backend_root() -> Path:
    return get_project_root() / "backend"


def get_frontend_dist() -> Path:
    return get_project_root() / "frontend" / "dist"


def get_data_dir() -> Path:
    if is_frozen():
        local_app_data = os.environ.get("LOCALAPPDATA")

        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA environment variable is unavailable")

        return Path(local_app_data) / get_data_dir_name() / "data"

    return get_backend_root() / "data"


def get_log_dir() -> Path:
    if is_frozen():
        local_app_data = os.environ.get("LOCALAPPDATA")

        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA environment variable is unavailable")

        return Path(local_app_data) / get_data_dir_name() / "logs"

    return get_backend_root() / "logs"


def get_config_file() -> Path:
    return get_data_dir() / "config.json"
