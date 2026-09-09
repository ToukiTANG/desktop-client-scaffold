import logging
import sys
import threading
from logging.handlers import RotatingFileHandler

from core.paths import get_log_dir

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(threadName)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    root_logger.addHandler(file_handler)

    sys.excepthook = _handle_exception
    threading.excepthook = _handle_thread_exception


def _handle_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger("exception").critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def _handle_thread_exception(args: threading.ExceptHookArgs) -> None:
    logging.getLogger("exception").critical(
        "Unhandled thread exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )
