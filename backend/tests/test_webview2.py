import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core import webview2


class WebView2Tests(unittest.TestCase):
    def test_missing_framework_blocks_before_native_loading(self):
        with patch.object(webview2, "get_net_framework_release", return_value=0), patch.object(
            webview2, "query_webview2_version"
        ) as query:
            with self.assertRaisesRegex(RuntimeError, ".NET Framework"):
                webview2.validate_webview2_runtime()
            query.assert_not_called()

    def test_native_failure_is_not_hidden_by_registry_version(self):
        with patch.object(webview2, "get_net_framework_release", return_value=528040), patch.dict(
            os.environ, {}, clear=True
        ), patch.object(
            webview2, "query_webview2_version", side_effect=RuntimeError("HRESULT=0x80070002")
        ), self.assertRaisesRegex(RuntimeError, "80070002"):
            webview2.validate_webview2_runtime()

    def test_win7_rejects_newer_runtime(self):
        with patch.object(webview2, "get_net_framework_release", return_value=528040), patch.dict(
            os.environ, {}, clear=True
        ), patch.object(webview2, "query_webview2_version", return_value="110.0.0.0"), patch.object(
            webview2, "is_windows_7", return_value=True
        ), self.assertRaisesRegex(RuntimeError, "109"):
            webview2.validate_webview2_runtime()

    def test_win7_accepts_runtime109(self):
        with patch.object(webview2, "get_net_framework_release", return_value=528040), patch.dict(
            os.environ, {}, clear=True
        ), patch.object(webview2, "query_webview2_version", return_value="109.0.1518.140"), patch.object(
            webview2, "is_windows_7", return_value=True
        ):
            webview2.validate_webview2_runtime()

    def test_incorrect_override_architecture_is_rejected(self):
        with patch.object(webview2, "get_net_framework_release", return_value=528040), patch.dict(
            os.environ, {"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "bad-runtime"}
        ), patch.object(webview2, "get_pe_machine", return_value=0x14C), patch.object(
            webview2, "query_webview2_version"
        ) as query:
            with self.assertRaisesRegex(RuntimeError, "位数"):
                webview2.validate_webview2_runtime()
            query.assert_not_called()

    def test_reads_real_pe_architecture_field(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / "runtime.exe"
            data = bytearray(134)
            data[:2] = b"MZ"
            struct.pack_into("<I", data, 60, 128)
            data[128:132] = b"PE\0\0"
            struct.pack_into("<H", data, 132, 0x8664)
            executable.write_bytes(data)
            self.assertEqual(webview2.get_pe_machine(executable), 0x8664)
            executable.write_bytes(b"broken")
            with self.assertRaises(ValueError):
                webview2.get_pe_machine(executable)

    def test_framework_registry_checks_both_views(self):
        key = Mock()
        key.__enter__ = Mock(return_value=key)
        key.__exit__ = Mock(return_value=False)
        with patch.object(webview2.winreg, "OpenKey", side_effect=[FileNotFoundError(), key]) as open_key, patch.object(
            webview2.winreg, "QueryValueEx", return_value=(528040, 4)
        ):
            self.assertEqual(webview2.get_net_framework_release(), 528040)
            self.assertEqual(open_key.call_count, 2)
