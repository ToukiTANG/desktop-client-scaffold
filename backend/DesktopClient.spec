from pathlib import Path

from PyInstaller.utils.hooks import collect_all


backend_dir = Path(SPECPATH)
project_root = backend_dir.parent

frontend_dist = project_root / "frontend" / "dist"
alembic_dir = backend_dir / "alembic"
alembic_ini = backend_dir / "alembic.ini"


datas = [
    (str(frontend_dist), "frontend/dist"),
    (str(alembic_dir), "backend/alembic"),
    (str(alembic_ini), "backend"),
]

binaries = []
hiddenimports = []


for package in ["webview", "pythonnet", "clr_loader"]:
    package_datas, package_binaries, package_hiddenimports = collect_all(package)

    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports


hiddenimports += [
    "logging.config",
    "core.schema",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.pysqlite",
]


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

pyz = PYZ(a.pure)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DesktopClient",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DesktopClient",
)