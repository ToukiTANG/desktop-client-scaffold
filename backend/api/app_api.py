from api.person_api import PersonApi


class AppApi:
    """暴露给 Vue 前端调用的 Python API。"""

    def __init__(self):
        # 人员模块
        self.person = PersonApi()

    def ping(self):
        return {
            "success": True,
            "data": "pong",
            "message": None,
        }
