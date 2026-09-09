from __future__ import annotations

import json
import os
from typing import Any

from core.paths import get_config_file


def config_exists() -> bool:
    """
    判断配置文件是否存在。
    """
    return get_config_file().is_file()


def load_config() -> dict[str, Any]:
    """
    读取应用配置。

    配置文件不存在时返回空字典。
    配置文件格式错误或读取失败时抛出异常。
    """
    config_file = get_config_file()

    if not config_file.is_file():
        return {}

    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"配置文件格式错误: {config_file}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"配置文件读取失败: {config_file}"
        ) from exc

    if not isinstance(config, dict):
        raise TypeError(f"配置文件根节点必须是 JSON object: {config_file}")

    return config


def save_config(config: dict[str, Any]) -> None:
    """
    保存应用配置。

    Scaffold 只负责配置文件的持久化，
    不负责具体业务字段及业务校验。
    """
    if not isinstance(config, dict):
        raise TypeError("config must be a dict")

    config_file = get_config_file()
    config_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = config_file.with_name(
        f"{config_file.name}.tmp"
    )

    try:
        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(
                config,
                f,
                ensure_ascii=False,
                indent=2,
            )

        os.replace(
            str(temp_file),
            str(config_file),
        )

    except (OSError, TypeError, ValueError):
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass

        raise