# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for POS Monitor
Builds a single executable for the Windows service
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all data files and hidden imports for win32 modules
datas = []
hiddenimports = [
    'win32timezone',
    'win32serviceutil',
    'win32service',
    'win32event',
    'win32evtlog',
    'win32evtlogutil',
    'win32con',
    'servicemanager',
    'pywintypes',
    'psutil',
    'psutil._pswindows',
    'psutil._psutil_windows',
]

# Add win32 service files
tmp_ret = collect_all('win32com')
datas += tmp_ret[0]
hiddenimports += tmp_ret[2]

# Main service executable
a_service = Analysis(
    ['pos-monitor-service.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Core monitor executable (for standalone testing)
a_monitor = Analysis(
    ['pos-monitor-core.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports + [
        'pos_monitor_hang_detector',
        'pos_monitor_event_log',
        'pos_monitor_async_logger',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Merge analyses
MERGE((a_service, 'pos-monitor-service', 'pos-monitor-service'),
      (a_monitor, 'pos-monitor', 'pos-monitor'))

# Service executable
pyz_service = PYZ(a_service.pure, a_service.zipped_data, cipher=block_cipher)

exe_service = EXE(
    pyz_service,
    a_service.scripts,
    a_service.binaries,
    a_service.zipfiles,
    a_service.datas,
    [],
    name='POSMonitorService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version-info.txt',
    icon='assets/pos-monitor.ico',
    uac_admin=True,  # Require admin privileges
)

# Monitor executable
pyz_monitor = PYZ(a_monitor.pure, a_monitor.zipped_data, cipher=block_cipher)

exe_monitor = EXE(
    pyz_monitor,
    a_monitor.scripts,
    a_monitor.binaries,
    a_monitor.zipfiles,
    a_monitor.datas,
    [],
    name='POSMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version-info.txt',
    icon='assets/pos-monitor.ico',
)

# Collect all executables and support files
coll = COLLECT(
    exe_service,
    exe_monitor,
    a_service.binaries,
    a_service.zipfiles,
    a_service.datas,
    a_monitor.binaries,
    a_monitor.zipfiles,
    a_monitor.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='POSMonitor',
)