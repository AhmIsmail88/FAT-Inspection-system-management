"""
build.py
────────
One-command build script.
Run from the fat_system folder:

    python build.py

What it does:
  1. Checks requirements are installed
  2. Runs PyInstaller
  3. Verifies output
  4. Prints next steps for Inno Setup
"""

import subprocess
import sys
import shutil
from pathlib import Path

ROOT     = Path(__file__).parent
DIST_DIR = ROOT / "dist" / "HAC_FAT_System"
SPEC     = ROOT / "fat_system.spec"


def log(msg, ok=True):
    mark = "[OK]" if ok else "[FAIL]"
    print(f"  {mark}  {msg}")

def check_requirements():
    print("\n-- Checking requirements ----------------------")
    required = [
        "PyQt6", "sqlalchemy", "bcrypt", "openpyxl",
        "PyInstaller",
    ]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.split(".")[0])
            log(pkg)
        except ImportError:
            log(pkg, ok=False)
            missing.append(pkg)

    if missing:
        print(f"\n  Install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def run_pyinstaller():
    print("\n-- Running PyInstaller ------------------------")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC), "--clean", "--noconfirm"],
        cwd=ROOT,
    )
    if result.returncode != 0:
        log("PyInstaller failed", ok=False)
        sys.exit(1)
    log("PyInstaller completed")


def verify_output():
    print("\n-- Verifying output ---------------------------")
    exe = DIST_DIR / "HAC_FAT_System.exe"
    if exe.exists():
        size_mb = exe.stat().st_size / 1024 / 1024
        log(f"Executable: {exe.name}  ({size_mb:.1f} MB)")
    else:
        log(f"Executable not found: {exe}", ok=False)
        sys.exit(1)

    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        log("Assets folder included")
    else:
        log("Assets folder missing — copy manually", ok=False)


def print_next_steps():
    print("\n-- Next Steps ---------------------------------")
    print("""
  The application is ready in:
    dist\\HAC_FAT_System\\

  To create Setup.exe:
  ---------------------------------------------
  1. Download Inno Setup (free):
     https://jrsoftware.org/isdl.php

  2. Open:  installer\\setup.iss

  3. Click:  Build -> Compile  (or press F9)

  4. Your installer will be at:
     installer\\HAC_FAT_System_Setup_v1.0.0.exe

  To test WITHOUT installer (direct run):
  ---------------------------------------------
  Double-click:  dist\\HAC_FAT_System\\HAC_FAT_System.exe
""")


if __name__ == "__main__":
    print("=" * 52)
    print("  HAC FAT System — Build Script")
    print("=" * 52)

    check_requirements()
    run_pyinstaller()
    verify_output()
    print_next_steps()

    print("=" * 52)
    print("  Build complete!")
    print("=" * 52)
