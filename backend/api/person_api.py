from __future__ import annotations

from typing import Any

import webview

from core.person_dictionary import (
    GENDER_OPTIONS,
    IDENTITY_OPTIONS,
    SPECIALIZE_CLASSIFY_OPTIONS,
    PRODUCTION_GROUP_CLASSIFY_OPTIONS,
)
from core.response import failure, success
from services.person_service import PersonService


class PersonApi:
    """人员管理 API。"""

    def __init__(self) -> None:
        self.service = PersonService()

        self._window = None

        self._import_file_path: str | None = None

    def list(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        查询人员列表。
        """

        try:
            result = self.service.list(params)

            return success(data=result)

        except ValueError as exc:
            return failure(message=str(exc))

        except Exception as exc:
            print(f"[PersonApi.list] {exc}")

            return failure(message="查询人员失败")

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增人员。
        """

        try:
            result = self.service.create(data)

            return success(data=result, message="新增成功")

        except ValueError as exc:
            return failure(message=str(exc))

        except Exception as exc:
            print(f"[PersonApi.create] {exc}")

            return failure(message="新增人员失败")

    def update(self, person_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        修改人员。
        """

        try:
            self.service.update(person_id, data)

            return success(data=None, message="修改成功")

        except ValueError as exc:
            return failure(message=str(exc))

        except Exception as exc:
            print(f"[PersonApi.update] {exc}")

            return failure(message="修改人员失败")

    def delete(self, person_id: int) -> dict[str, Any]:
        """
        删除人员。
        """

        try:
            self.service.delete(person_id)

            return success(data=None, message="删除成功")

        except ValueError as exc:
            return failure(message=str(exc))

        except Exception as exc:
            print(f"[PersonApi.delete] {exc}")

            return failure(message="删除人员失败")

    def _bind_window(self, window) -> None:
        self._window = window

    def select_import_file(self) -> dict[str, Any]:
        """
        选择人员导入 Excel，
        并立即解析生成预览数据。
        """

        try:
            if self._window is None:
                return failure(message="应用窗口尚未初始化")

            files = self._window.create_file_dialog(
                webview.FileDialog.OPEN, allow_multiple=False, file_types=("Excel 文件 (*.xlsx)",)
            )

            # 用户取消选择
            if not files:
                self._import_file_path = None

                return success(data=None, message="已取消选择")

            file_path = str(files[0])

            # =========================
            # 解析 Excel
            # =========================

            result = self.service.preview_import_file(file_path)

            # 只有解析成功之后，
            # 才保存当前导入文件。
            self._import_file_path = file_path

            return success(data=result, message="文件解析完成")

        except ValueError as exc:
            self._import_file_path = None

            return failure(message=str(exc))

        except Exception as exc:
            self._import_file_path = None

            print(f"[PersonApi.select_import_file] {exc}")

            return failure(message="Excel 文件解析失败")

    def confirm_import(self) -> dict[str, Any]:
        """
        确认导入当前已经选择并预览过的 Excel 文件。
        """

        if not self._import_file_path:
            return failure(message="请先选择需要导入的 Excel 文件")

        file_path = self._import_file_path

        try:
            result = self.service.import_file(file_path)

            # 导入已经执行完成。
            # 清除当前文件，防止用户重复点击导致重复导入。
            self._import_file_path = None

            return success(data=result, message="人员导入完成")

        except ValueError as exc:
            return failure(message=str(exc))

        except Exception as exc:
            print(f"[PersonApi.confirm_import] {exc}")

            return failure(message="人员导入失败")

    def get_dictionary(self) -> dict[str, Any]:
        """
        获取人员相关固定业务字典。
        """

        try:
            return success(
                data={
                    "gender": [{"value": value, "label": label} for value, label in GENDER_OPTIONS.items()],
                    "identity": [{"value": value, "label": label} for value, label in IDENTITY_OPTIONS.items()],
                    "specializeClassify": [
                        {"value": value, "label": label} for value, label in SPECIALIZE_CLASSIFY_OPTIONS.items()
                    ],
                    "productionGroupClassify": [
                        {"value": value, "label": label} for value, label in PRODUCTION_GROUP_CLASSIFY_OPTIONS.items()
                    ],
                }
            )

        except Exception as exc:
            print(f"[PersonApi.get_dictionary] {exc}")

            return failure(message="获取人员字典失败")
