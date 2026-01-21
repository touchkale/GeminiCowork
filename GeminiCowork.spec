# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Gemini Cowork

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect customtkinter data files (themes, etc.)
datas = collect_data_files('customtkinter')

# Add any additional data files if needed
# datas += [('path/to/source', 'path/in/bundle')]

# Collect all submodules for packages that need them
hiddenimports = collect_submodules('customtkinter')
hiddenimports += collect_submodules('google.generativeai')
hiddenimports += collect_submodules('google.ai')
hiddenimports += collect_submodules('google.api_core')
hiddenimports += collect_submodules('google.auth')
hiddenimports += collect_submodules('pygments')
hiddenimports += [
    'PIL',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GeminiCowork',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)
