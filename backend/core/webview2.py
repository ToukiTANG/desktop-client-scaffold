from __future__ import annotations

import ctypes
import logging
import os
import struct
import sys
import winreg
from importlib.util import find_spec
from pathlib import Path

logger = logging.getLogger(__name__)
WEBVIEW2_CLIENT_ID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
NET_FRAMEWORK_MIN_RELEASE = 394802


def is_windows_7() -> bool:
    if sys.platform != "win32":
        return False
    version = sys.getwindowsversion()
    return version.major == 6 and version.minor == 1


def get_net_framework_release() -> int:
    # 使用显式注册表视图，不把 32 位和 64 位进程的视图混淆。
    key_path = r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full"
    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | view) as key:
                release, _ = winreg.QueryValueEx(key, "Release")
                if isinstance(release, int) and release >= NET_FRAMEWORK_MIN_RELEASE:
                    return release
        except FileNotFoundError:
            continue
    return 0


def get_webview2_version() -> str | None:
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(
                hive,
                rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
            ) as key:
                version, _ = winreg.QueryValueEx(key, "pv")
                if isinstance(version, str) and version and version != "0.0.0.0":
                    return version
        except FileNotFoundError:
            continue
    return None


def get_pe_machine(path: Path) -> int:
    # 读取 PE 文件头，避免只根据文件名或 Program Files (x86) 目录判断位数。
    with path.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("运行时文件不是有效的 Windows 程序")
        stream.seek(60)
        offset = struct.unpack("<I", stream.read(4))[0]
        stream.seek(offset)
        if stream.read(4) != b"PE\0\0":
            raise ValueError("运行时文件 PE 头无效")
        return struct.unpack("<H", stream.read(2))[0]


def query_webview2_version() -> str:
    # 使用安装包内、与进程架构一致的官方加载器验证实际可用性。
    spec = find_spec("webview")
    if spec is None or spec.origin is None:
        raise RuntimeError("缺少 PyWebView 组件，请重新安装软件")
    arch = "win-x64" if struct.calcsize("P") == 8 else "win-x86"
    loader = Path(spec.origin).parent / "lib" / "runtimes" / arch / "native" / "WebView2Loader.dll"
    if not loader.is_file():
        raise RuntimeError(f"缺少 {arch} WebView2Loader.dll，请重新安装软件")
    try:
        library = ctypes.WinDLL(str(loader))
        query = library.GetAvailableCoreWebView2BrowserVersionString
        query.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p)]
        query.restype = ctypes.c_long
        version_ptr = ctypes.c_void_p()
        result = query(None, ctypes.byref(version_ptr))
        try:
            if result != 0 or not version_ptr.value:
                raise RuntimeError(
                    f"WebView2 加载器未找到可用运行时（HRESULT=0x{result & 0xFFFFFFFF:08X}），请运行安装程序修复环境"
                )
            return ctypes.wstring_at(version_ptr.value)
        finally:
            if version_ptr.value:
                free = ctypes.windll.ole32.CoTaskMemFree
                free.argtypes = [ctypes.c_void_p]
                free.restype = None
                free(version_ptr)
    except OSError as exc:
        raise RuntimeError(
            f"WebView2 加载器无法加载（系统错误码 {getattr(exc, 'winerror', '未知')}），请运行安装程序修复环境"
        ) from exc


def validate_webview2_runtime() -> None:
    if sys.platform != "win32":
        return
    try:
        release = get_net_framework_release()
    except OSError as exc:
        raise RuntimeError("无法读取 .NET Framework 环境信息，请检查系统权限") from exc
    if release < NET_FRAMEWORK_MIN_RELEASE:
        raise RuntimeError(
            "未检测到 .NET Framework 4.6.2 或以上完整版本，请运行安装程序安装 .NET Framework 4.8 后重启电脑"
        )
    logger.info(".NET Framework Release=%s；进程位数=%s", release, struct.calcsize("P") * 8)
    override = os.environ.get("WEBVIEW2_BROWSER_EXECUTABLE_FOLDER")
    if override:
        executable = Path(override) / "msedgewebview2.exe"
        try:
            expected = 0x8664 if struct.calcsize("P") == 8 else 0x14C
            if get_pe_machine(executable) != expected:
                raise RuntimeError("指定的 WebView2 运行时位数与软件不一致，请清除错误目录配置并运行安装程序修复")
        except (OSError, ValueError, struct.error) as exc:
            raise RuntimeError("指定的 WebView2 运行时目录无效，请检查 WEBVIEW2_BROWSER_EXECUTABLE_FOLDER") from exc
    version = query_webview2_version()
    logger.info("WebView2 加载器检测版本=%s", version)
    if is_windows_7() and not version.startswith("109."):
        raise RuntimeError(f"Windows 7 必须使用 WebView2 Runtime 109 x64，当前可用版本：{version}，请运行安装程序修复")


def is_webview2_compatible() -> bool:
    try:
        validate_webview2_runtime()
        return True
    except RuntimeError:
        return False
