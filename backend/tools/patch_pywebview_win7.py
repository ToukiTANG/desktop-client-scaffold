from importlib.metadata import version
from pathlib import Path

import webview

EXPECTED_PYWEBVIEW_VERSION = "4.2.2"

ORIGINAL_CODE = """                self.scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100"""

PATCHED_CODE = """                try:
                    self.scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100
                except (OSError, AttributeError):
                    self.scale_factor = 1.0"""


def main() -> None:
    pywebview_version = version("pywebview")

    if pywebview_version != EXPECTED_PYWEBVIEW_VERSION:
        raise RuntimeError(
            f"Unsupported pywebview version: {pywebview_version}. "
            f"Expected: {EXPECTED_PYWEBVIEW_VERSION}"
        )

    webview_dir = Path(webview.__file__).resolve().parent
    winforms_file = webview_dir / "platforms" / "winforms.py"

    if not winforms_file.is_file():
        raise FileNotFoundError(
            f"pywebview winforms.py not found: {winforms_file}"
        )

    source = winforms_file.read_text(encoding="utf-8")

    if PATCHED_CODE in source:
        print(
            f"pywebview {pywebview_version} Win7 patch already applied"
        )
        return

    count = source.count(ORIGINAL_CODE)

    if count != 1:
        raise RuntimeError(
            "Unable to apply pywebview Win7 patch: "
            f"expected exactly one target, found {count}"
        )

    source = source.replace(
        ORIGINAL_CODE,
        PATCHED_CODE,
        1,
    )

    winforms_file.write_text(
        source,
        encoding="utf-8",
    )

    print(
        f"pywebview {pywebview_version} Win7 patch applied successfully"
    )


if __name__ == "__main__":
    main()