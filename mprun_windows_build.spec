# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os

# Update your datas tuple to use collect_data_files
windows_style_path = os.path.abspath('windows_style.css')
mac_style_path = os.path.abspath('mac_style.css')
recent_files_path = os.path.abspath('internal data/_recent_files.json')
settings_path = os.path.abspath('internal data/_settings.json')

# Update the datas list with absolute paths
datas = [
    (windows_style_path, 'windows_style.css'),
    (mac_style_path, 'mac_style.css'),
    (recent_files_path, 'internal data/_recent_files.json'),
    (settings_path, 'internal data/_settings.json')
]

a = Analysis(
    ['main.py'],
    pathex=[r'C:\Users\kelle\PycharmProjects\mprun_repo\main.py'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='MPRUN',
    icon='MPRUN_icon.ico',
    uac_admin=False,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
