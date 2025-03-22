import PyInstaller.__main__
import os
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# Define the assets directory
assets_dir = current_dir / "assets"

# Create the spec file content with additional hidden imports
spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['overlay_appv2.py'],
    pathex=[r'{current_dir}'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pydantic',
        'pydantic_core',
        'pydantic_core._pydantic_core',
        'pydantic.errors',
        'typing_extensions'
    ],
    hookspath=[],
    hooksconfig={{}},
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
    name='StudyHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/icon.ico'
)
"""

# Write the spec file
with open("StudyHelper.spec", "w") as f:
    f.write(spec_content)

# Create necessary directories
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/gifs", exist_ok=True)

# Clean previous build
import shutil
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

# Run PyInstaller
PyInstaller.__main__.run([
    'StudyHelper.spec',
    '--clean',
]) 