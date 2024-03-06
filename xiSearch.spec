# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_data_files

datas = [
    ('D:\\workspace\\xiSearch-flet\\config.ini', '.'),
    ('D:\\workspace\\xiSearch-flet\\html', 'html')
]
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('numpy')
datas += copy_metadata('pillow')


block_cipher = None


a = Analysis(
    ['src/main.py'],
    pathex=['D:\\workspace\\xiSearch-flet'],
    binaries=[],
    datas=datas,
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
    [],
    exclude_binaries=True,
    name='xiSearch-flet',
    debug=False,
    icon='D:\\workspace\\xiSearch-flet\\icon.ico',
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
    name='xiSearch-flet',
)
