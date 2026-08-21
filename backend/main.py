import argparse
import ctypes
import logging

import webview

from api.app_api import AppApi
from core.database import init_database
from core.logging_config import setup_logging
from core.paths import get_frontend_dist

DEV_SERVER_URL = "http://127.0.0.1:5173"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Desktop Client")

    parser.add_argument("--dev", action="store_true", help="Run application in development mode")

    return parser.parse_args()


def get_app_url(dev: bool) -> str:
    if dev:
        return DEV_SERVER_URL

    index_file = get_frontend_dist() / "index.html"

    if not index_file.exists():
        raise FileNotFoundError(
            f"Frontend build not found: {index_file}\nPlease run `npm run build` inside frontend first."
        )

    return str(index_file)


def show_startup_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, message, "Desktop Client 启动失败", 0x10)


def main() -> None:
    args = parse_args()

    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Desktop Client starting")
    logger.info("Development mode: %s", args.dev)

    try:
        init_database()

        api = AppApi()
        app_url = get_app_url(dev=args.dev)

        logger.info("Application URL: %s", app_url)

        window = webview.create_window(
            title="Desktop Client", url=app_url, js_api=api, width=1600, height=900, min_size=(900, 600)
        )

        api._bind_window(window)

        logger.info("Starting PyWebView")

        webview.start(debug=args.dev, http_server=not args.dev)

        logger.info("Desktop Client stopped")
    except Exception:
        logger.exception("Desktop Client startup failed")

        if not args.dev:
            show_startup_error(
                "程序启动失败。\n\n详细错误信息已记录到日志文件：\n%LOCALAPPDATA%\\DesktopClient\\logs\\app.log"
            )

        raise


if __name__ == "__main__":
    main()
