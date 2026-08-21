import argparse

import webview

from api.app_api import AppApi
from core.database import init_database
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


def main() -> None:
    args = parse_args()
    init_database()
    api = AppApi()

    app_url = get_app_url(dev=args.dev)

    window = webview.create_window(
        title="Desktop Client", url=app_url, js_api=api, width=1600, height=900, min_size=(900, 600)
    )

    api._bind_window(window)

    webview.start(debug=args.dev, http_server=not args.dev)


if __name__ == "__main__":
    main()
