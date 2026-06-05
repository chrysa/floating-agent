# PyInstaller spec — floating-agent (onefile, GUI).
# Build from the repo root: `pyinstaller --noconfirm packaging/floating-agent.spec`
# PySide6 is bundled automatically via PyInstaller's built-in Qt hooks.
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ["floating_agent/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("floating_agent"),
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="floating-agent",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
