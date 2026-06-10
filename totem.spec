# -*- mode: python ; coding: utf-8 -*-
import sys

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# PyQt6 WebEngine exige binários e recursos Qt adicionais no bundle.
pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all("PyQt6")
datas = pkg_datas
binaries = pkg_binaries
hiddenimports = pkg_hiddenimports

if sys.platform == "win32":
    hiddenimports += ["win32print", "win32api", "pywintypes"]

hiddenimports += ["PyQt6.QtWebChannel"]

a = Analysis(
    ["totem/__main__.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FilaflowTotem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FilaflowTotem",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="FilaflowTotem.app",
        icon=None,
        bundle_identifier="com.filaflow.totem",
    )
