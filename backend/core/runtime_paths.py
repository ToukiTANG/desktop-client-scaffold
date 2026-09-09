from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """
    判断当前是否运行在 PyInstaller 打包环境中。
    """
    return bool(getattr(sys, "frozen", False))


def get_project_root() -> Path:
    """
    获取应用资源根目录。

    开发环境：
        desktop-client-scaffold/

    PyInstaller 环境：
        sys._MEIPASS
    """
    if is_frozen():
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]