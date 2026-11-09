import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from core.window_controls import Win32WindowDriver, WindowControls


class WindowControlsTests(unittest.TestCase):
    def setUp(self):
        self.window = Mock()
        self.driver = Mock()
        self.driver.is_maximized.return_value = False
        self.controls = WindowControls(self.window, self.driver)

    def test_toggle_uses_actual_native_state(self):
        self.controls.toggle_maximize()
        self.driver.show.assert_called_once_with(3)
        self.driver.is_maximized.return_value = True
        self.controls.toggle_maximize()
        self.driver.show.assert_called_with(9)

    def test_minimize_and_close(self):
        self.controls.minimize()
        self.driver.show.assert_called_once_with(6)
        self.controls.close()
        self.window.destroy.assert_called_once_with()

    def test_state_reads_native_state(self):
        self.driver.is_maximized.return_value = True
        self.assertEqual(self.controls.state(), {"maximized": True})

    def test_resize_edges_and_invalid_edge(self):
        self.controls.resize("bottom-right")
        self.driver.resize.assert_called_once_with(8)
        with self.assertRaises(ValueError):
            self.controls.resize("bad")

    def test_maximized_resize_is_ignored(self):
        self.driver.is_maximized.return_value = True
        self.controls.resize("left")
        self.driver.resize.assert_not_called()

    def test_drag_delegates_to_native_move(self):
        self.controls.move()
        self.driver.move.assert_called_once_with()

    def test_window_is_required(self):
        with self.assertRaises(RuntimeError):
            WindowControls(None)


class NativeMoveTests(unittest.TestCase):
    def make_driver(self, maximized):
        driver = Win32WindowDriver.__new__(Win32WindowDriver)
        driver.native = Mock(InvokeRequired=False)
        driver.user32 = Mock()
        driver.handle = 123
        driver.is_maximized = Mock(return_value=maximized)
        return driver

    def test_restored_move_uses_system_command(self):
        driver = self.make_driver(False)
        driver.move()
        driver.user32.ShowWindow.assert_not_called()
        driver.user32.SendMessageW.assert_called_once_with(123, 0x0112, 0xF012, 0)

    def test_maximized_move_restores_beneath_pointer(self):
        driver = self.make_driver(True)

        def cursor(pointer):
            pointer._obj.x, pointer._obj.y = 500, 20
            return True

        sizes = iter([(2000, 1000), (1000, 700)])

        def bounds(handle, pointer):
            rect = pointer._obj
            width, height = next(sizes)
            rect.left, rect.top, rect.right, rect.bottom = 0, 0, width, height
            return True

        driver.user32.GetCursorPos.side_effect = cursor
        driver.user32.GetWindowRect.side_effect = bounds
        driver.move()
        driver.user32.ShowWindow.assert_called_once_with(123, 9)
        driver.user32.SetWindowPos.assert_called_once_with(123, None, 250, 0, 0, 0, 5)
        driver.user32.SendMessageW.assert_called_once_with(123, 0x0112, 0xF012, 0)

    def test_bridge_move_runs_inside_ui_invoke(self):
        self.assert_mouse_ui_dispatch("move", (), 0xF012)

    def test_bridge_resize_runs_inside_ui_invoke(self):
        self.assert_mouse_ui_dispatch("resize", (8,), 0xF008)

    def assert_mouse_ui_dispatch(self, action, args, command):
        driver = self.make_driver(False)
        driver.native.InvokeRequired = True
        inside_ui = False

        def invoke(callback):
            nonlocal inside_ui
            inside_ui = True
            try:
                callback()
            finally:
                inside_ui = False

        def release_capture():
            self.assertTrue(inside_ui, "Mouse capture must be released on the UI thread")

        driver.native.Invoke.side_effect = invoke
        driver.user32.ReleaseCapture.side_effect = release_capture
        driver.user32.SendMessageW.side_effect = lambda *args: self.assertTrue(inside_ui)
        with patch.dict("sys.modules", {"System": SimpleNamespace(Action=lambda callback: callback)}):
            getattr(driver, action)(*args)
        driver.native.Invoke.assert_called_once()
        driver.user32.SendMessageW.assert_called_once_with(123, 0x0112, command, 0)


class NativeFrameTests(unittest.TestCase):
    make_driver = NativeMoveTests.make_driver

    def frame_modules(self):
        return {
            "System": SimpleNamespace(Action=lambda callback: callback),
            "System.Drawing": SimpleNamespace(ColorTranslator=SimpleNamespace(FromHtml=lambda color: color)),
            "System.Windows.Forms": SimpleNamespace(Padding=lambda size: (size, size, size, size)),
        }

    def test_native_border_reserves_all_four_sides_without_changing_window_style(self):
        driver = self.make_driver(False)
        original_style = driver.native.FormBorderStyle
        with patch.dict("sys.modules", self.frame_modules()):
            driver.configure_frame()
        self.assertEqual(driver.native.BackColor, "#9fb1c2")
        self.assertEqual(driver.native.Padding, (1, 1, 1, 1))
        self.assertIs(driver.native.FormBorderStyle, original_style)
        driver.native.PerformLayout.assert_called_once_with()
        driver.user32.SetWindowPos.assert_not_called()

    def test_native_frame_setup_is_dispatched_to_ui_thread(self):
        driver = self.make_driver(False)
        driver.native.InvokeRequired = True
        with patch.dict("sys.modules", self.frame_modules()):
            driver.configure_frame()
            driver.native.Invoke.assert_called_once()
            driver.native.PerformLayout.assert_not_called()
            driver.native.Invoke.call_args.args[0]()
        driver.native.PerformLayout.assert_called_once_with()

    def test_controls_initialize_native_frame(self):
        driver = Mock()
        WindowControls(Mock(), driver).initialize_frame()
        driver.configure_frame.assert_called_once_with()


class RestoredWindowSizeTests(unittest.TestCase):
    def test_initial_restore_uses_eighty_percent_of_work_area(self):
        from core.window_controls import get_restored_window_size

        user32 = Mock()

        def work_area(action, unused, pointer, flags):
            pointer._obj.left, pointer._obj.top = -100, 40
            pointer._obj.right, pointer._obj.bottom = 1820, 1080
            return True

        user32.SystemParametersInfoW.side_effect = work_area
        self.assertEqual(get_restored_window_size(user32), (1536, 832))
        user32.GetSystemMetrics.assert_not_called()

    def test_small_display_respects_existing_minimum_size(self):
        from core.window_controls import get_restored_window_size

        user32 = Mock()

        def work_area(action, unused, pointer, flags):
            pointer._obj.right, pointer._obj.bottom = 1366, 728
            return True

        user32.SystemParametersInfoW.side_effect = work_area
        self.assertEqual(get_restored_window_size(user32), (1092, 600))

    def test_work_area_failure_falls_back_to_display_size(self):
        from core.window_controls import get_restored_window_size

        user32 = Mock()
        user32.SystemParametersInfoW.return_value = False
        user32.GetSystemMetrics.side_effect = [1920, 1080]
        self.assertEqual(get_restored_window_size(user32), (1536, 864))
