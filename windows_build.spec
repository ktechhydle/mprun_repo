# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

# Get the metadata for 'pyicloud'
pyicloud_metadata = copy_metadata('pyicloud')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('mp_software_stylesheets', 'mp_software_stylesheets'),
    ('mprun_assets', 'mprun_assets'),
    ('internal data', 'internal data'),
    ('course elements', 'course elements'),
    ('IMPORTANT', 'IMPORTANT'),
    ] + pyicloud_metadata,
    hiddenimports=['pyicloud'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    noconfirm=True,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MPRUN',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MPRUN',
)
