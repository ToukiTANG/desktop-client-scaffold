import argparse
import ctypes
import logging
from ctypes import wintypes

import webview

from api.app_api import AppApi
from core.database import init_database
from core.logging_config import setup_logging
from core.paths import get_frontend_dist, get_log_dir
from core.project_config import get_app_name
from core.webview2 import validate_webview2_runtime
from core.windows_dpi import configure_dpi_awareness

DEV_SERVER_URL = "http://127.0.0.1:5173"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=get_app_name())

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
    ctypes.windll.user32.MessageBoxW(0, message, f"{get_app_name()} 启动失败", 0x10)


def maximize_window(window: webview.Window) -> None:
    # PyWebView 4.2.2 没有最大化 API，在窗口显示后使用 WinForms 句柄最大化。
    from webview.platforms.winforms import BrowserView

    native_window = BrowserView.instances[window.uid]
    show_window = ctypes.windll.user32.ShowWindowAsync
    show_window.argtypes = [wintypes.HWND, ctypes.c_int]
    show_window.restype = wintypes.BOOL
    show_window(native_window.Handle.ToInt64(), 3)  # SW_MAXIMIZE：标准最大化，保留系统标题栏。


def main() -> None:
    args = parse_args()

    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("%s starting", get_app_name())
    logger.info("Development mode: %s", args.dev)

    try:
        validate_webview2_runtime()
    except RuntimeError as exc:
        logger.exception("WebView2 runtime validation failed")

        if not args.dev:
            show_startup_error(str(exc))

        raise

    try:
        init_database()

        api = AppApi()
        app_url = get_app_url(dev=args.dev)

        logger.info("Application URL: %s", app_url)

        configure_dpi_awareness()

        window = webview.create_window(
            title=get_app_name(),
            url=app_url,
            js_api=api,
            width=1600,
            height=900,
            min_size=(900, 600),
            resizable=True,
            fullscreen=False,
            frameless=False,
            text_select=True,
        )

        window.events.shown += lambda: maximize_window(window)
        api._bind_window(window)

        logger.info("Starting PyWebView")

        webview.start(gui="edgechromium", debug=args.dev, http_server=not args.dev)

        logger.info("%s stopped", get_app_name())

    except Exception:
        logger.exception("%s startup failed", get_app_name())

        if not args.dev:
            show_startup_error(f"程序启动失败。\n\n详细错误信息已记录到日志文件：\n{get_log_dir() / 'app.log'}")

        raise


if __name__ == "__main__":
    main()
