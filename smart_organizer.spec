# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Получаем путь к проекту через sys.argv[0]
spec_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
project_path = spec_dir
src_path = os.path.join(project_path, 'src')

# Все необходимые данные
datas = [
    (os.path.join(src_path, 'assets', '*'), 'assets'),
    (os.path.join(src_path, 'ui', '*'), 'ui'),
    (os.path.join(src_path, '*.db'), '.'),
    (os.path.join(src_path, '*.json'), '.'),
]

# Скрытые импорты
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtNetwork',
    'core',
    'gui',
    'widgets',
]

# Пути для поиска модулей
pathex = [
    project_path,
    src_path,
    os.path.join(src_path, 'core'),
    os.path.join(src_path, 'gui'),
    os.path.join(src_path, 'widgets'),
]

a = Analysis(
    ['src/main.py'],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tests'],
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
    name='SmartOrganizer',
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
    icon=os.path.join(src_path, 'assets', 'icon.ico') if os.path.exists(os.path.join(src_path, 'assets', 'icon.ico')) else None,
)