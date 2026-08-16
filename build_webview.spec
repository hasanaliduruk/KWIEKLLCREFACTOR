# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the webview version of Operations Toolkit.
#
# onedir mode: produces dist\OperationsToolkit_Webview\ (exe + _internal).
#   - upx=False on purpose: UPX-packed executables are a well-known Windows
#     Defender false-positive trigger. If you want a smaller bundle AND have
#     a code-signing certificate, sign the output instead of packing it.
#   - version file: embeds Windows file properties (company, description,
#     version) from the repo-root version.txt.
#
# Run with:  pyinstaller build_webview.spec --clean

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui_web', 'gui_web'),
        ('core', 'core'),
        ('utils', 'utils'),
        ('assets/icon.ico', 'assets'),
    ],
    hiddenimports=[
        'webview',
        'webview.dom',
        'keyring',
        'keyring.backends',
        'requests',
        'screeninfo',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'tkinterdnd2',
        'PIL',
        'screeninfo',
        'matplotlib',
        'unittest',
        'test',
        'pydoc',
        'doctest',
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
    name='OperationsToolkit_Webview',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='assets/icon.ico',
    version='version.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='OperationsToolkit_Webview',
    # Place data files in the base directory alongside the exe
    # This ensures Settings folder is not in _internal
    path='.',
)
