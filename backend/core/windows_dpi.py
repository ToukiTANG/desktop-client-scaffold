"""配置进程 DPI 感知，并在 Windows 7 上回退到兼容接口。"""

import ctypes
import logging

logger = logging.getLogger(__name__)

# HRESULT E_ACCESSDENIED 表示 DPI 感知已配置，例如已由应用清单设置。
DPI_ALREADY_CONFIGURED = -2147024891


def configure_dpi_awareness() -> None:
    try:
        result = ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if result in (0, DPI_ALREADY_CONFIGURED):
            return
        logger.warning("现代 DPI 接口设置失败（HRESULT=%s），尝试旧版兼容接口", result)
    except (OSError, AttributeError):
        # 包括继承自 OSError 的 PyInstallerImportError，兼容打包后的 DLL 加载异常。
        logger.info("现代 DPI 接口不可用，尝试 Windows 7 兼容接口")

    try:
        if not ctypes.windll.user32.SetProcessDPIAware():
            logger.warning("旧版 DPI 感知未启用，继续使用系统默认设置")
    except (OSError, AttributeError):
        # DPI 缩放配置失败不应阻止应用启动，继续使用系统默认设置。
        logger.warning("DPI 接口不可用，继续使用系统默认设置", exc_info=True)
