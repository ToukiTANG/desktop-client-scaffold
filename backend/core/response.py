from __future__ import annotations

from typing import Any


def success(
    data: Any = None,
    message: str | None = None,
) -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def failure(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": False,
        "data": data,
        "message": message,
    }