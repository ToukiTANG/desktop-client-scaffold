"""Shared frameless-window controls for the Windows PyWebView host."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import ClassVar


def get_restored_window_size(user32=None):
    """Choose a useful restore size before the initial startup maximize."""
    if user32 is None:
        user32 = ctypes.windll.user32
    work = wintypes.RECT()
    if user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(work), 0):  # SPI_GETWORKAREA
        width, height = work.right - work.left, work.bottom - work.top
    else:
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return max(900, int(width * 0.8)), max(600, int(height * 0.8))


class Win32WindowDriver:
    def __init__(self, window):
        from webview.platforms.winforms import BrowserView

        self.native = BrowserView.instances[window.uid]
        self.handle = self.native.Handle.ToInt64()
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetWindowRect.restype = wintypes.BOOL
        self.user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.user32.GetCursorPos.restype = wintypes.BOOL
        self.user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.ShowWindow.restype = wintypes.BOOL
        self.user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.user32.IsZoomed.argtypes = [wintypes.HWND]
        self.user32.IsZoomed.restype = wintypes.BOOL
        self.user32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.ShowWindowAsync.restype = wintypes.BOOL
        self.user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
        self.user32.SendMessageW.restype = ctypes.c_ssize_t

    def configure_frame(self):
        self._on_ui_thread(self._configure_frame)

    def _configure_frame(self):
        from System.Drawing import ColorTranslator
        from System.Windows.Forms import Padding

        # WinForms paints the reserved border outside the docked WebView.
        # Keep FormBorderStyle unchanged so maximize/restore sizing stays correct.
        self.native.BackColor = ColorTranslator.FromHtml("#9fb1c2")
        self.native.Padding = Padding(1)
        self.native.PerformLayout()

    def is_maximized(self):
        return bool(self.user32.IsZoomed(self.handle))

    def show(self, command):
        if command == 3:
            # Borderless WinForms otherwise covers the taskbar when maximized.
            from System import Action
            from System.Drawing import Rectangle
            from System.Windows.Forms import Screen

            def set_bounds():
                screen = Screen.FromHandle(self.native.Handle)
                work, bounds = screen.WorkingArea, screen.Bounds
                self.native.MaximizedBounds = Rectangle(work.X - bounds.X, work.Y - bounds.Y, work.Width, work.Height)

            self.native.Invoke(Action(set_bounds))
        self.user32.ShowWindowAsync(self.handle, command)

    def _on_ui_thread(self, callback):
        # JS bridge methods run on worker threads; capture belongs to the UI thread.
        if self.native.InvokeRequired:
            from System import Action

            self.native.Invoke(Action(callback))
        else:
            callback()

    def move(self):
        self._on_ui_thread(self._move)

    def _move(self):
        if self.is_maximized():
            # Restore beneath the pointer before entering Windows' native move loop.
            point, before, after = wintypes.POINT(), wintypes.RECT(), wintypes.RECT()
            self.user32.GetCursorPos(ctypes.byref(point))
            self.user32.GetWindowRect(self.handle, ctypes.byref(before))
            fraction = (point.x - before.left) / max(1, before.right - before.left)
            offset_y = max(0, point.y - before.top)
            self.user32.ShowWindow(self.handle, 9)
            self.user32.GetWindowRect(self.handle, ctypes.byref(after))
            self.user32.SetWindowPos(
                self.handle,
                None,
                point.x - int((after.right - after.left) * fraction),
                point.y - offset_y,
                0,
                0,
                0x0005,
            )
        self.user32.ReleaseCapture()
        self.user32.SendMessageW(self.handle, 0x0112, 0xF012, 0)  # WM_SYSCOMMAND, SC_MOVE | HTCAPTION

    def resize(self, edge):
        self._on_ui_thread(lambda: self._resize(edge))

    def _resize(self, edge):
        self.user32.ReleaseCapture()
        self.user32.SendMessageW(self.handle, 0x0112, 0xF000 | edge, 0)  # SC_SIZE


class WindowControls:
    EDGES: ClassVar[dict[str, int]] = {
        "left": 1,
        "right": 2,
        "top": 3,
        "top-left": 4,
        "top-right": 5,
        "bottom": 6,
        "bottom-left": 7,
        "bottom-right": 8,
    }

    def __init__(self, window, driver=None):
        if window is None:
            raise RuntimeError("窗口尚未就绪")
        self.window = window
        self.driver = driver if driver is not None else Win32WindowDriver(window)

    def initialize_frame(self):
        self.driver.configure_frame()

    def state(self):
        return {"maximized": self.driver.is_maximized()}

    def minimize(self):
        self.driver.show(6)

    def toggle_maximize(self):
        self.driver.show(9 if self.driver.is_maximized() else 3)

    def close(self):
        # Keep PyWebView's closing handlers and confirmation behavior.
        self.window.destroy()

    def move(self):
        self.driver.move()

    def resize(self, edge):
        if edge not in self.EDGES:
            raise ValueError("无效的窗口缩放方向")
        if not self.driver.is_maximized():
            self.driver.resize(self.EDGES[edge])
