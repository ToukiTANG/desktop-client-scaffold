from typing import Any

from core.response import failure, success
from services.person_service import PersonService


class PersonApi:
    """人员管理 API。"""

    def __init__(self) -> None:
        self.service = PersonService()

    def list(
        self,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        查询人员列表。
        """

        try:
            result = self.service.list(
                params
            )

            return success(
                data=result
            )

        except ValueError as exc:
            return failure(
                message=str(exc)
            )

        except Exception as exc:
            print(
                f"[PersonApi.list] {exc}"
            )

            return failure(
                message="查询人员失败"
            )

    def create(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        新增人员。
        """

        try:
            result = self.service.create(
                data
            )

            return success(
                data=result,
                message="新增成功",
            )

        except ValueError as exc:
            return failure(
                message=str(exc)
            )

        except Exception as exc:
            print(
                f"[PersonApi.create] {exc}"
            )

            return failure(
                message="新增人员失败"
            )

    def update(
        self,
        person_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        修改人员。
        """

        try:
            self.service.update(
                person_id,
                data,
            )

            return success(
                data=None,
                message="修改成功",
            )

        except ValueError as exc:
            return failure(
                message=str(exc)
            )

        except Exception as exc:
            print(
                f"[PersonApi.update] {exc}"
            )

            return failure(
                message="修改人员失败"
            )

    def delete(
        self,
        person_id: int,
    ) -> dict[str, Any]:
        """
        删除人员。
        """

        try:
            self.service.delete(
                person_id
            )

            return success(
                data=None,
                message="删除成功",
            )

        except ValueError as exc:
            return failure(
                message=str(exc)
            )

        except Exception as exc:
            print(
                f"[PersonApi.delete] {exc}"
            )

            return failure(
                message="删除人员失败"
            )