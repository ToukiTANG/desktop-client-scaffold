from __future__ import annotations

from pathlib import Path
from typing import Any

import webview

from core.problem_dictionary import PROBLEM_DICTIONARY
from core.response import failure, success
from services.problem_service import ProblemService


class ProblemApi:
    def __init__(self):
        self.service = ProblemService()
        self._window = None
        self._import_file_path: str | None = None

    def _bind_window(self, window):
        self._window = window

    def list(self, params: dict[str, Any]):
        try:
            return success(data=self.service.list(params))
        except Exception as exc:
            return failure(str(exc))

    def get_dictionary(self):
        data = {
            key: [{"value": value, "label": label} for value, label in options.items()]
            for key, options in PROBLEM_DICTIONARY.items()
        }

        return success(data=data)

    def select_import_file(self):
        try:
            if self._window is None:
                return failure("窗口尚未初始化")

            result = self._window.create_file_dialog(
                webview.FileDialog.OPEN,
                allow_multiple=False,
                file_types=("Excel 文件 (*.xls;*.xlsx)",),
            )

            if not result:
                return success(data=None, message="已取消选择")

            file_path = str(result[0])

            preview = self.service.preview_import_file(file_path)

            self._import_file_path = file_path

            return success(data=preview)

        except Exception as exc:
            self._import_file_path = None
            return failure(str(exc))

    def confirm_import(self):
        try:
            if not self._import_file_path:
                return failure("请先选择需要导入的 Excel 文件")

            file_path = self._import_file_path

            if not Path(file_path).exists():
                self._import_file_path = None
                return failure("Excel 文件不存在，请重新选择")

            result = self.service.import_file(file_path)

            self._import_file_path = None

            return success(data=result, message="导入完成")

        except Exception as exc:
            return failure(str(exc))