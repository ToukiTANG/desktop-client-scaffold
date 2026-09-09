from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from core.runtime_paths import get_project_root


@lru_cache(maxsize=1)
def get_project_config() -> dict[str, Any]:
    config_file = get_project_root() / "project.json"

    if not config_file.is_file():
        raise RuntimeError(f"项目配置文件不存在: {config_file}")

    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"项目配置文件格式错误: {config_file}") from exc
    except OSError as exc:
        raise RuntimeError(f"项目配置文件读取失败: {config_file}") from exc

    if not isinstance(config, dict):
        raise TypeError("project.json 根节点必须是 JSON object")

    required_fields = ("app_name", "app_id", "internal_name", "executable_name", "data_dir_name", "installer_name")

    for field in required_fields:
        value = config.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"project.json 缺少有效字段: {field}")

    return config


def get_app_name() -> str:
    return str(get_project_config()["app_name"])


def get_app_id() -> str:
    return str(get_project_config()["app_id"])


def get_internal_name() -> str:
    return str(get_project_config()["internal_name"])


def get_executable_name() -> str:
    return str(get_project_config()["executable_name"])


def get_data_dir_name() -> str:
    return str(get_project_config()["data_dir_name"])


def get_installer_name() -> str:
    return str(get_project_config()["installer_name"])
