"""
Build script to compile Telegram Simulator into a standalone Windows .exe
using PyInstaller.
"""

import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def build():
    print("=" * 65)
    print("🔨 Starting build of Telegram Simulator standalone executable...")
    print("=" * 65)

    dist_dir = ROOT_DIR / "frontend" / "dist"
    if not dist_dir.exists():
        print("❌ Error: frontend/dist does not exist! Run 'npm run build' first.")
        sys.exit(1)

    # PyInstaller arguments
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name", "telegram-simulator",
        "--add-data", f"{ROOT_DIR / 'frontend' / 'dist'};frontend/dist",
        "--add-data", f"{ROOT_DIR / 'examples'};examples",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.loops.asyncio",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "aiosqlite",
        "--hidden-import", "sqlalchemy.dialects.sqlite.aiosqlite",
        "--hidden-import", "greenlet",
        "--hidden-import", "websockets",
        # Exclude unrelated heavy packages in user environment
        "--exclude-module", "PyQt6",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas",
        "--exclude-module", "scipy",
        "--exclude-module", "numpy",
        "--exclude-module", "tensorflow",
        "--exclude-module", "torch",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "--exclude-module", "botocore",
        "--exclude-module", "boto3",
        "--exclude-module", "tkinter",
        "--exclude-module", "_tkinter",
        "--clean",
        str(ROOT_DIR / "run.py")
    ]

    print("Running command:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print("❌ Build failed with exit code:", res.returncode)
        sys.exit(res.returncode)

    exe_path = ROOT_DIR / "dist" / "telegram-simulator.exe"
    if not exe_path.exists():
        print("❌ Expected exe not found at:", exe_path)
        sys.exit(1)

    print("\n✅ Build succeeded! Created executable at:", exe_path)
    file_size_mb = round(exe_path.stat().st_size / (1024 * 1024), 2)
    print(f"📦 Executable Size: {file_size_mb} MB")

    # Create ZIP archive for release
    zip_path = ROOT_DIR / "dist" / "telegram-simulator-windows-x64.zip"
    print(f"📦 Creating release archive: {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, arcname="telegram-simulator.exe")
        # Add quick start readme for release
        readme_text = (
            "Telegram Simulator - Portable Windows Release\n"
            "=============================================\n\n"
            "Quick Start:\n"
            "1. Double-click 'telegram-simulator.exe'\n"
            "2. Your browser will automatically open at http://127.0.0.1:8000\n"
            "3. Your database and files will be saved in the 'data/' folder next to the .exe\n\n"
            "Documentation & Source: https://github.com/rillside/telegram-bot-simulator\n"
        )
        zf.writestr("README_RELEASE.txt", readme_text)

    zip_size_mb = round(zip_path.stat().st_size / (1024 * 1024), 2)
    print(f"🎉 Successfully created release package: {zip_path} ({zip_size_mb} MB)")

if __name__ == "__main__":
    build()
