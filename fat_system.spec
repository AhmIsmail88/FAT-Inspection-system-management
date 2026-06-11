# fat_system.spec
# PyInstaller specification file for HAC FAT & Inspection System
# Run with:  pyinstaller fat_system.spec

import sys
from pathlib import Path

block_cipher = None
APP_NAME     = "HAC_FAT_System"

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        # Include assets folder (logo, icons)
        ("assets",   "assets"),
    ],
    hiddenimports=[
        # SQLAlchemy dialects
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.pool",
        "sqlalchemy.event",

        # PyQt6 modules that get missed
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtCharts",
        "PyQt6.sip",

        # bcrypt
        "bcrypt",

        # OpenPyXL
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.utils",
        
        # Environment configuration
        "dotenv",

        # Standard library extras
        "email",
        "email.mime",
        "email.mime.text",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy unused packages
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "PIL",
        "cv2",
        "pytest",
        "IPython",
        "jupyter",
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
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No black console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",   # Uncomment when you have an .ico file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
