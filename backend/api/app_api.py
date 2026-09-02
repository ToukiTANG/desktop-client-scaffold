import os

from core.paths import get_data_dir, get_log_dir
from core.response import success
from core.version import get_app_version


class AppApi:
    def __init__(self):
        pass
    def _bind_window(self, window):
        pass
    def ping(self):
        return success(data="pong")

    def get_app_info(self):
        return success(
            data={"version": get_app_version(), "dataDir": str(get_data_dir()), "logDir": str(get_log_dir())}
        )

    def open_directory(self, path: str):
        if not os.path.isdir(path):
            return success(data=False, message=f"目录不存在: {path}")

        os.startfile(path)

        return success(data=True)
