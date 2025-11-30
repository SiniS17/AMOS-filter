# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Collect resources
datas = [
    ('bin', 'bin'),
    ('doc_validator/resources', 'doc_validator/resources'),
]

# Hidden imports for packages that might not be detected
hidden_imports = [
    'googleapiclient.discovery',
    'googleapiclient.http',
    'pandas',
    'openpyxl',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    name='AMOS Validation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Change to False once working
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='doc_validator/resources/icons/app_logo.ico',  # Make sure this .ico file exists!
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AMOS Validation',
)

# Override DISTPATH to output to EXE folder
DISTPATH = 'EXE'