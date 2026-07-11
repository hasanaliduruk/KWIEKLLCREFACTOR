# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the tkinter version of Operations Toolkit.
# Builds main.py into a onedir bundle (not onefile) so the _internal folder
# can be shared with the webview build.
#
# IMPORTANT: tkinterdnd2 must be collected in full (not just the top-level
# module) or drag-and-drop will silently fail at runtime. We use
# collect_submodules + collect_data_files to grab everything.
#
# Run with:  pyinstaller build_tkinter.spec --clean

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Grab every tkinterdnd2 submodule and its data files (the .tcl scripts
# it needs at runtime). Without this, DnD works in dev but not in the build.
tkdnd2_hiddenimports = collect_submodules('tkinterdnd2')
tkdnd2_datas = collect_data_files('tkinterdnd2')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui', 'gui'),
        ('core', 'core'),
        ('utils', 'utils'),
        ('assets', 'assets'),
        ('Settings', 'Settings'),
    ] + tkdnd2_datas,
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'screeninfo',
    ] + tkdnd2_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'webview',
        'webview.dom',
    ],
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
    name='OperationsToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OperationsToolkit',
)
