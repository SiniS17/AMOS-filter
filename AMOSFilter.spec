# AMOSFilter.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from pathlib import Path

# Assume we run `pyinstaller AMOSFilter.spec` from the project root
project_root = Path(".").resolve()
pathex = [str(project_root)]

a = Analysis(
    ['run_gui.py'],
    pathex=pathex,
    binaries=[],
    datas=[
        # include entire bin/ folder → dist/.../bin/
        ('bin', 'bin'),
    ],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AMOSFilter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,          # GUI app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # set to 'icon.ico' later if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AMOSFilter',
    distpath=str(project_root / 'EXE'),   # EXE/AMOSFilter/...
)
