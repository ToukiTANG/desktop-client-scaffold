import tomli
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


# ============================================================
# Paths
# ============================================================

backend_dir = Path(SPECPATH)
project_root = backend_dir.parent

frontend_dist = project_root / "frontend" / "dist"
alembic_dir = backend_dir / "alembic"
alembic_ini = backend_dir / "alembic.ini"
pyproject_file = backend_dir / "pyproject.toml"
icon_file = backend_dir / "build_resources" / "app.ico"


# ============================================================
# Application version
# pyproject.toml is the single source of truth
# ============================================================

with pyproject_file.open("rb") as f:
    pyproject = tomli.load(f)

app_version = pyproject["project"]["version"]

version_parts = app_version.split(".")

if len(version_parts) > 4 or not all(part.isdigit() for part in version_parts):
    raise ValueError(f"Unsupported application version: {app_version}")

version_tuple = tuple(int(part) for part in version_parts)
version_tuple += (0,) * (4 - len(version_tuple))


# ============================================================
# Generate Windows version resource
# ============================================================

version_file = Path(workpath) / "version_info.txt"
version_file.parent.mkdir(parents=True, exist_ok=True)

version_file.write_text(
    f"""VSVersionInfo(
    ffi=FixedFileInfo(
        filevers={version_tuple},
        prodvers={version_tuple},
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "080404B0",
                    [
                        StringStruct("CompanyName", ""),
                        StringStruct("FileDescription", "Desktop Client"),
                        StringStruct("FileVersion", "{app_version}"),
                        StringStruct("InternalName", "DesktopClient"),
                        StringStruct("OriginalFilename", "DesktopClient.exe"),
                        StringStruct("ProductName", "Desktop Client"),
                        StringStruct("ProductVersion", "{app_version}"),
                    ],
                )
            ]
        ),
        VarFileInfo(
            [
                VarStruct("Translation", [2052, 1200]),
            ]
        ),
    ],
)
""",
    encoding="utf-8",
)


# ============================================================
# Data files
# ============================================================

datas = [
    (str(frontend_dist), "frontend/dist"),
    (str(alembic_dir), "backend/alembic"),
    (str(alembic_ini), "backend"),
    (str(pyproject_file), "backend"),
]

binaries = []
hiddenimports = []


# ============================================================
# PyWebView / pythonnet runtime dependencies
# ============================================================

for package in ["webview", "pythonnet", "clr_loader"]:
    package_datas, package_binaries, package_hiddenimports = collect_all(package)

    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports


# ============================================================
# Dynamic imports
#
# alembic/env.py is loaded dynamically at runtime, so
# PyInstaller cannot discover these imports automatically.
# ============================================================

hiddenimports += [
    "logging.config",
    "core.schema",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.pysqlite",
]


# ============================================================
# Analysis
# ============================================================

a = Analysis(
    ["main.py"],
    pathex=[str(backend_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)


# ============================================================
# Python archive
# ============================================================

pyz = PYZ(a.pure)


# ============================================================
# Executable
# ============================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DesktopClient",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    version=str(version_file),
    icon=str(icon_file),
)


# ============================================================
# onedir distribution
# ============================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DesktopClient",
)