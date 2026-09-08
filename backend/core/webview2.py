from __future__ import annotations

import sys
import winreg
from typing import Optional


WEBVIEW2_CLIENT_ID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"


def is_windows_7() -> bool:
    """
    判断当前系统是否为 Windows 7。
    """
    if sys.platform != "win32":
        return False

    version = sys.getwindowsversion()

    return version.major == 6 and version.minor == 1


def get_webview2_version() -> Optional[str]:
    """
    获取系统已安装的 WebView2 Runtime 版本。

    Returns:
        如 "109.0.1518.140"
        未安装则返回 None
    """
    if sys.platform != "win32":
        return None

    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}"),
        (winreg.HKEY_CURRENT_USER, rf"Software\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}"),
    ]

    for root, path in registry_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                version, _ = winreg.QueryValueEx(key, "pv")

                if isinstance(version, str) and version and version != "0.0.0.0":
                    return version

        except FileNotFoundError:
            continue

    return None


def is_webview2_compatible() -> bool:
    version = get_webview2_version()

    if not version:
        return False

    if not is_windows_7():
        return True

    try:
        major = int(version.split(".", 1)[0])
    except (ValueError, IndexError):
        return False

    return major == 109


def validate_webview2_runtime() -> None:
    """
    校验当前系统的 WebView2 Runtime 是否满足程序运行要求。

    Windows 7:
        必须安装 WebView2 Runtime 109.x

    Windows 10 / 11:
        必须存在可用的 WebView2 Runtime
    """
    version = get_webview2_version()

    if is_windows_7():
        if not version:
            raise RuntimeError("当前系统为 Windows 7，但未检测到 Microsoft Edge WebView2 Runtime 109。")

        try:
            major = int(version.split(".", 1)[0])
        except (ValueError, IndexError):
            raise RuntimeError(f"无法识别 WebView2 Runtime 版本: {version}")

        if major != 109:
            raise RuntimeError(f"Windows 7 必须使用 WebView2 Runtime 109，当前检测到版本: {version}")

        return

    if not version:
        raise RuntimeError("未检测到 Microsoft Edge WebView2 Runtime，程序无法启动。")
