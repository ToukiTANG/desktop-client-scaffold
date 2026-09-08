from pathlib import Path

from core.app_config import is_configured, load_config
from core.business_config import MATERIAL_PRICE_FILENAME, NAS_ROOT


def get_material_price_file() -> Path:
    config = load_config()

    if not is_configured(config):
        raise RuntimeError("应用尚未完成初始化配置")

    workshop = config["workshop"]

    file_path = NAS_ROOT / workshop / MATERIAL_PRICE_FILENAME

    if not file_path.is_file():
        raise FileNotFoundError(f"原料单价文件不存在: {file_path}")

    return file_path
