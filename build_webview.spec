# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the webview version of Operations Toolkit.
#
# onedir mode: produces dist\OperationsToolkit_Webview\ (exe + _internal).
#   - upx=False on purpose: UPX-packed executables are a well-known Windows
#     Defender false-positive trigger. If you want a smaller bundle AND have
#     a code-signing certificate, sign the output instead of packing it.
#   - VERSION is the single source for the app and Windows file properties.
#
# Run with:  pyinstaller build_webview.spec --clean

from pathlib import Path

from core.versioning import read_version, render_version_resource


block_cipher = None
release_version = read_version()
resource_template = Path('version.txt').read_text(encoding='utf-8')
generated_resource = Path('build') / 'generated_webview_version.txt'
generated_resource.parent.mkdir(exist_ok=True)
generated_resource.write_text(render_version_resource(resource_template, release_version), encoding='utf-8')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('VERSION', '.'),
        ('gui_web', 'gui_web'),
        ('core', 'core'),
        ('utils', 'utils'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'rust_core',
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
    version=str(generated_resource),
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
import sys

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='OperationsToolkit_Webview.app',
        icon='assets/icon.icns',
        bundle_identifier='com.kwiekllc.operationstoolkit',
    )
