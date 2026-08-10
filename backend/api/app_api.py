import platform
import sys


class AppApi:
    """暴露给 Vue 前端调用的 Python API。"""

    def ping(self) -> dict:
        return {
            "code": 0,
            "message": "pong",
        }

    def hello(self, name: str) -> dict:
        return {
            "code": 0,
            "message": f"Hello, {name}",
        }

    def get_system_info(self) -> dict:
        return {
            "code": 0,
            "data": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": sys.version,
            },
        }