import argparse
from pathlib import Path

import webview

from api.app_api import AppApi
from core.database import init_database

DEV_SERVER_URL = "http://127.0.0.1:5173"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Desktop Client",
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run application in development mode",
    )

    return parser.parse_args()


def get_project_root() -> Path:
    """
    backend 和 frontend 的共同父目录。
    """

    backend_dir = Path(__file__).resolve().parent

    return backend_dir.parent


def get_frontend_dist() -> Path:
    project_root = get_project_root()

    return project_root / "frontend" / "dist"


def get_app_url(dev: bool) -> str:
    if dev:
        return DEV_SERVER_URL

    index_file = get_frontend_dist() / "index.html"

    if not index_file.exists():
        raise FileNotFoundError(
            "Frontend build not found: "
            f"{index_file}\n"
            "Please run `npm run build` "
            "inside frontend first."
        )

    return str(index_file)


def main() -> None:
    args = parse_args()
    init_database()
    api = AppApi()

    app_url = get_app_url(
        dev=args.dev,
    )

    webview.create_window(
        title="Desktop Client",
        url=app_url,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
    )

    webview.start(
        debug=args.dev,
        http_server=not args.dev,
    )


if __name__ == "__main__":
    main()
