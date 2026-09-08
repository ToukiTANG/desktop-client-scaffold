from __future__ import annotations

import logging
import os
from typing import Any

from core.app_config import load_config, save_config
from core.paths import get_data_dir, get_log_dir
from core.response import failure, success
from core.version import get_app_version


logger = logging.getLogger(__name__)


class AppApi:
    def __init__(self):
        self._window = None

        self._apis = {
        }

    def _bind_window(self, window):
        self._window = window

        for api in self._apis.values():
            api._bind_window(window)

    def invoke(
        self,
        module: str,
        method: str,
        args: list[Any] | None = None,
    ):
        """
        统一调用业务 API。
        """

        api = self._apis.get(module)

        if api is None:
            return failure(
                message=f"未知 API 模块: {module}"
            )

        if method.startswith("_"):
            return failure(
                message=f"不允许调用私有 API 方法: {method}"
            )

        func = getattr(api, method, None)

        if func is None or not callable(func):
            return failure(
                message=f"未知 API 方法: {module}.{method}"
            )

        try:
            data = func(*(args or []))

            return success(data=data)

        except Exception as exc:
            logger.exception(
                "API call failed: %s.%s",
                module,
                method,
            )

            return failure(
                message=str(exc)
            )

    # ========================================================
    # 系统级 API
    # ========================================================

    def ping(self):
        return success(data="pong")

    def get_app_info(self):
        return success(
            data={
                "version": get_app_version(),
                "dataDir": str(get_data_dir()),
                "logDir": str(get_log_dir()),
            }
        )

    def open_directory(self, path: str):
        if not os.path.isdir(path):
            return success(
                data=False,
                message=f"目录不存在: {path}",
            )

        os.startfile(path)

        return success(data=True)

    def get_app_config(self):
        try:
            return success(
                data=load_config()
            )
        except (ValueError, RuntimeError) as exc:
            return failure(
                message=str(exc)
            )

    def save_app_config(
            self,
            config: dict[str, Any],
    ):
        try:
            save_config(config)

            return success(
                data=config
            )

        except (
                TypeError,
                ValueError,
                RuntimeError,
                OSError,
        ) as exc:
            return failure(
                message=str(exc)
            )