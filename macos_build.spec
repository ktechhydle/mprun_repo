# -*- mode: python ; coding: utf-8 -*-

import os

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('mp_software_stylesheets', 'mp_software_stylesheets'),
    ('internal data', 'internal data'),
    ('course elements', 'course elements'),
    ('ui', 'ui'),
    ('IMPORTANT', 'IMPORTANT'),
    ],
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
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
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

app = BUNDLE(
    coll,
    name='MPRUN.app',
    icon='icon.icns',
    bundle_identifier=None,
)
