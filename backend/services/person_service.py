from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from core.database import get_connection


class PersonService:
    """人员数据业务服务。"""

    # =========================
    # 基础工具
    # =========================

    @staticmethod
    def _now() -> str:
        """返回当前本地时间。"""
        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def _row_to_person(
        row: sqlite3.Row,
    ) -> dict[str, Any]:
        """
        SQLite snake_case
        转换为前端 camelCase。
        """

        return {
            "id": row["id"],
            "name": row["name"],
            "department": row["department"],
            "jobTitle": row["job_title"],
            "identity": row["identity"],
            "specializeClassify": row["specialize_classify"],
            "education": row["education"],
            "gender": row["gender"],
            "productionGroupClassify": row[
                "production_group_classify"
            ],
            "createTime": row["created_at"],
        }

    @staticmethod
    def _parse_required_int(
        value: Any,
        field_name: str,
    ) -> int:
        """
        将必填枚举字段转换为整数。

        支持：
        1
        "1"

        不允许：
        None
        ""
        True / False
        非数字字符串
        """

        if value is None or value == "":
            raise ValueError(
                f"{field_name}不能为空"
            )

        # bool 是 int 的子类，需要单独排除
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name}格式错误"
            )

        try:
            result = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name}格式错误"
            ) from exc

        return result

    @staticmethod
    def _parse_optional_int(
        value: Any,
        field_name: str,
    ) -> int | None:
        """
        解析可为空的整数枚举字段。
        """

        if value is None or value == "":
            return None

        if isinstance(value, bool):
            raise ValueError(
                f"{field_name}格式错误"
            )

        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name}格式错误"
            ) from exc

    @staticmethod
    def _escape_like(
        value: str,
    ) -> str:
        """
        转义 LIKE 中的特殊字符。

        防止用户搜索 % 或 _ 时被当成通配符。
        """

        return (
            value
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

    # =========================
    # 人员数据校验
    # =========================

    def _validate_person(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        校验新增/编辑人员数据。

        注意：
        前端表单校验负责用户体验；
        这里的后端校验负责数据完整性。
        """

        name = str(
            data.get("name") or ""
        ).strip()

        department = str(
            data.get("department") or ""
        ).strip()

        job_title = str(
            data.get("jobTitle") or ""
        ).strip()

        education = str(
            data.get("education") or ""
        ).strip()

        if not name:
            raise ValueError(
                "姓名不能为空"
            )

        if len(name) > 50:
            raise ValueError(
                "姓名不能超过50个字符"
            )

        if not department:
            raise ValueError(
                "部门不能为空"
            )

        if not job_title:
            raise ValueError(
                "职名不能为空"
            )

        if not education:
            raise ValueError(
                "学历不能为空"
            )

        identity = self._parse_required_int(
            data.get("identity"),
            "身份类型",
        )

        specialize_classify = (
            self._parse_required_int(
                data.get(
                    "specializeClassify"
                ),
                "专业分类",
            )
        )

        gender = self._parse_required_int(
            data.get("gender"),
            "性别",
        )

        production_group_classify = (
            self._parse_optional_int(
                data.get(
                    "productionGroupClassify"
                ),
                "生产组类别",
            )
        )

        return {
            "name": name,
            "department": department,
            "job_title": job_title,
            "identity": identity,
            "specialize_classify":
                specialize_classify,
            "education": education,
            "gender": gender,
            "production_group_classify":
                production_group_classify,
        }

    # =========================
    # 分页查询
    # =========================

    def list(
        self,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        查询人员列表。

        支持参数：

        {
            "keyword": "",
            "department": "",
            "identity": 1,
            "specializeClassify": 1,
            "education": "",
            "gender": 1,
            "productionGroupClassify": 1,
            "page": 1,
            "pageSize": 20
        }
        """

        params = params or {}

        keyword = str(
            params.get("keyword") or ""
        ).strip()

        department = str(
            params.get("department") or ""
        ).strip()

        education = str(
            params.get("education") or ""
        ).strip()

        # =========================
        # 枚举筛选参数
        # =========================

        identity = self._parse_optional_int(
            params.get("identity"),
            "身份类型",
        )

        specialize_classify = (
            self._parse_optional_int(
                params.get(
                    "specializeClassify"
                ),
                "专业分类",
            )
        )

        gender = self._parse_optional_int(
            params.get("gender"),
            "性别",
        )

        production_group_classify = (
            self._parse_optional_int(
                params.get(
                    "productionGroupClassify"
                ),
                "生产组类别",
            )
        )

        # =========================
        # 分页
        # =========================

        try:
            page = int(
                params.get("page", 1)
            )
        except (TypeError, ValueError):
            page = 1

        try:
            page_size = int(
                params.get(
                    "pageSize",
                    20,
                )
            )
        except (TypeError, ValueError):
            page_size = 20

        page = max(
            page,
            1,
        )

        # 最多一次查询100条
        page_size = max(
            1,
            min(
                page_size,
                100,
            ),
        )

        offset = (
            page - 1
        ) * page_size

        # =========================
        # 构造 WHERE
        # =========================

        conditions: list[str] = []
        args: list[Any] = []

        if keyword:
            escaped = self._escape_like(
                keyword
            )

            like_keyword = (
                f"%{escaped}%"
            )

            conditions.append(
                """
                (
                    name LIKE ? ESCAPE '\\'
                    OR job_title LIKE ? ESCAPE '\\'
                )
                """
            )

            args.extend([
                like_keyword,
                like_keyword,
            ])

        if department:
            conditions.append(
                "department = ?"
            )

            args.append(
                department
            )

        if identity is not None:
            conditions.append(
                "identity = ?"
            )

            args.append(
                identity
            )

        if specialize_classify is not None:
            conditions.append(
                "specialize_classify = ?"
            )

            args.append(
                specialize_classify
            )

        if education:
            conditions.append(
                "education = ?"
            )

            args.append(
                education
            )

        if gender is not None:
            conditions.append(
                "gender = ?"
            )

            args.append(
                gender
            )

        if (
            production_group_classify
            is not None
        ):
            conditions.append(
                "production_group_classify = ?"
            )

            args.append(
                production_group_classify
            )

        where_sql = ""

        if conditions:
            where_sql = (
                "WHERE "
                + " AND ".join(
                    conditions
                )
            )

        # =========================
        # 查询 SQLite
        # =========================

        with get_connection() as conn:
            # 总数
            count_sql = f"""
                SELECT
                    COUNT(*) AS total
                FROM person
                {where_sql}
            """

            total_row = conn.execute(
                count_sql,
                args,
            ).fetchone()

            total = (
                total_row["total"]
                if total_row
                else 0
            )

            # 当前页
            query_sql = f"""
                SELECT
                    id,
                    name,
                    department,
                    job_title,
                    identity,
                    specialize_classify,
                    education,
                    gender,
                    production_group_classify,
                    created_at
                FROM person
                {where_sql}
                ORDER BY id DESC
                LIMIT ?
                OFFSET ?
            """

            rows = conn.execute(
                query_sql,
                [
                    *args,
                    page_size,
                    offset,
                ],
            ).fetchall()

        return {
            "items": [
                self._row_to_person(row)
                for row in rows
            ],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    # =========================
    # 新增人员
    # =========================

    def create(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        新增人员。
        """

        person = self._validate_person(
            data
        )

        now = self._now()

        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO person (
                    name,
                    department,
                    job_title,
                    identity,
                    specialize_classify,
                    education,
                    gender,
                    production_group_classify,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?
                )
                """,
                (
                    person["name"],
                    person["department"],
                    person["job_title"],
                    person["identity"],
                    person[
                        "specialize_classify"
                    ],
                    person["education"],
                    person["gender"],
                    person[
                        "production_group_classify"
                    ],
                    now,
                    now,
                ),
            )

            person_id = cursor.lastrowid

        return {
            "id": person_id,
        }

    # =========================
    # 修改人员
    # =========================

    def update(
        self,
        person_id: int,
        data: dict[str, Any],
    ) -> None:
        """
        修改人员。
        """

        person = self._validate_person(
            data
        )

        now = self._now()

        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE person
                SET
                    name = ?,
                    department = ?,
                    job_title = ?,
                    identity = ?,
                    specialize_classify = ?,
                    education = ?,
                    gender = ?,
                    production_group_classify = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    person["name"],
                    person["department"],
                    person["job_title"],
                    person["identity"],
                    person[
                        "specialize_classify"
                    ],
                    person["education"],
                    person["gender"],
                    person[
                        "production_group_classify"
                    ],
                    now,
                    person_id,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "人员不存在"
                )

    # =========================
    # 删除人员
    # =========================

    def delete(
        self,
        person_id: int,
    ) -> None:
        """
        删除人员。
        """

        with get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM person
                WHERE id = ?
                """,
                (
                    person_id,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "人员不存在"
                )