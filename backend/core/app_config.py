import json
from typing import Any

from core.paths import get_config_file


def config_exists() -> bool:
    """
    判断配置文件是否存在。
    """
    return get_config_file().is_file()


def load_config() -> dict[str, Any] | None:
    """
    读取配置文件。

    Returns:
        dict: 配置文件存在且 JSON 格式正确
        None: 文件不存在或 JSON 格式错误
    """
    config_file = get_config_file()

    if not config_file.is_file():
        return None

    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = json.load(f)

        if not isinstance(config, dict):
            return None

        return config

    except (OSError, json.JSONDecodeError):
        return None


def is_configured(config: dict[str, Any] | None) -> bool:
    """
    判断当前配置是否已经完成初始化。
    """
    if not config:
        return False

    workshop = config.get("workshop")
    apartment = config.get("apartment")

    if not isinstance(workshop, str) or not workshop.strip():
        return False

    if not isinstance(apartment, str) or not apartment.strip():
        return False

    return True


def save_config(workshop: str, apartment: str) -> None:
    """
    保存初始化配置。
    """
    workshop = workshop.strip()
    apartment = apartment.strip()

    if not workshop:
        raise ValueError("workshop cannot be empty")

    if not apartment:
        raise ValueError("apartment cannot be empty")

    config_file = get_config_file()
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config = {"workshop": workshop, "apartment": apartment}

    with config_file.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
