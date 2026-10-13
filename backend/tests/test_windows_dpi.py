import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from core.windows_dpi import DPI_ALREADY_CONFIGURED, configure_dpi_awareness


class WindowsDpiTests(unittest.TestCase):
    def run_with_apis(self, modern, legacy):
        apis = SimpleNamespace(
            shcore=SimpleNamespace(SetProcessDpiAwareness=modern), user32=SimpleNamespace(SetProcessDPIAware=legacy)
        )
        with patch("core.windows_dpi.ctypes.windll", apis, create=True):
            configure_dpi_awareness()

    def test_modern_windows_uses_per_monitor_dpi(self):
        modern, legacy = Mock(return_value=0), Mock()
        self.run_with_apis(modern, legacy)
        modern.assert_called_once_with(2)
        legacy.assert_not_called()

    def test_already_configured_manifest_does_not_change_dpi(self):
        modern, legacy = Mock(return_value=DPI_ALREADY_CONFIGURED), Mock()
        self.run_with_apis(modern, legacy)
        legacy.assert_not_called()

    def test_missing_dll_in_frozen_win7_uses_legacy_api(self):
        class PyInstallerImportError(OSError):
            pass

        class MissingShcore:
            @property
            def shcore(self):
                raise PyInstallerImportError("Failed to load dynlib/dll 'shcore'")

        apis = MissingShcore()
        legacy = Mock(return_value=1)
        apis.user32 = SimpleNamespace(SetProcessDPIAware=legacy)
        with patch("core.windows_dpi.ctypes.windll", apis, create=True):
            configure_dpi_awareness()
        legacy.assert_called_once_with()

    def test_missing_function_uses_legacy_api(self):
        legacy = Mock(return_value=1)
        self.run_with_apis(Mock(side_effect=AttributeError("missing function")), legacy)
        legacy.assert_called_once_with()

    def test_failed_modern_hresult_uses_legacy_api(self):
        legacy = Mock(return_value=1)
        with self.assertLogs("core.windows_dpi", level="WARNING"):
            self.run_with_apis(Mock(return_value=-2147024809), legacy)
        legacy.assert_called_once_with()

    def test_failed_legacy_api_does_not_abort_startup(self):
        for legacy in (
            Mock(return_value=0),
            Mock(side_effect=OSError("unavailable")),
            Mock(side_effect=AttributeError("unavailable")),
        ):
            with self.subTest(legacy=legacy), self.assertLogs("core.windows_dpi", level="WARNING"):
                self.run_with_apis(Mock(side_effect=OSError("missing shcore")), legacy)


if __name__ == "__main__":
    unittest.main()
