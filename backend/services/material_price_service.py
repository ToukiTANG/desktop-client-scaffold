from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import openpyxl

from core.app_config import load_config


DEFAULT_NAS_ROOT = Path(r"\\192.168.1.100\share")
MATERIAL_FILE_NAME = "材料价格表.xlsx"


def get_material_root() -> Path:
    dev_root = os.environ.get("DESKTOP_CLIENT_MATERIAL_ROOT")

    if dev_root:
        return Path(dev_root)

    return DEFAULT_NAS_ROOT


class MaterialPriceService:
    def get_material_file_path(self) -> Path:
        config = load_config()

        workshop = str(config.get("workshop", "")).strip()
        apartment = str(config.get("apartment", "")).strip()

        if not workshop:
            raise ValueError("未配置车间")

        if not apartment:
            raise ValueError("未配置公寓")

        return get_material_root() / workshop / apartment / MATERIAL_FILE_NAME

    def get_material_prices(self) -> list[dict[str, Any]]:
        file_path = self.get_material_file_path()

        if not file_path.exists():
            raise FileNotFoundError(
                f"材料价格表不存在或无法访问: {file_path}"
            )

        return self._read_xlsx(file_path)

    def _read_xlsx(self, file_path: Path) -> list[dict[str, Any]]:
        try:
            workbook = openpyxl.load_workbook(
                filename=str(file_path),
                read_only=True,
                data_only=True,
            )
        except PermissionError as exc:
            raise RuntimeError(
                f"没有权限访问材料价格表: {file_path}"
            ) from exc
        except OSError as exc:
            raise RuntimeError(
                f"无法读取材料价格表: {file_path}"
            ) from exc

        try:
            worksheet = workbook.active

            rows = [
                list(row)
                for row in worksheet.iter_rows(values_only=True)
            ]

            return self._parse_rows(rows)
        finally:
            workbook.close()

    def _parse_rows(
            self,
            rows: list[list[Any]],
    ) -> list[dict[str, Any]]:
        header_index = self._find_header_row(rows)

        if header_index is None:
            raise ValueError(
                "材料价格表中未找到“品名、单价、单位”表头"
            )

        headers = [
            self._normalize_header(value)
            for value in rows[header_index]
        ]

        name_index = headers.index("品名")
        price_index = headers.index("单价")
        unit_index = headers.index("单位")

        materials = []

        for row in rows[header_index + 1:]:
            name = self._get_cell(row, name_index)

            if name is None or str(name).strip() == "":
                continue

            price = self._get_cell(row, price_index)
            unit = self._get_cell(row, unit_index)

            materials.append(
                {
                    "name": str(name).strip(),
                    "price": price,
                    "unit": (
                        str(unit).strip()
                        if unit is not None
                        else ""
                    ),
                }
            )

        return materials

    def _find_header_row(
            self,
            rows: list[list[Any]],
    ) -> int | None:
        for index, row in enumerate(rows[:20]):
            headers = {
                self._normalize_header(value)
                for value in row
                if value is not None
            }

            if {
                "品名",
                "单价",
                "单位",
            }.issubset(headers):
                return index

        return None

    @staticmethod
    def _normalize_header(value: Any) -> str:
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .replace(" ", "")
            .replace("\n", "")
        )

    @staticmethod
    def _get_cell(
            row: list[Any],
            index: int,
    ) -> Any:
        if index >= len(row):
            return None

        return row[index]
