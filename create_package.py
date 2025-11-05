#!/usr/bin/env python3
"""
Create a distributable package for Paint+
"""

import os
import shutil
import subprocess
from pathlib import Path

def create_package():
    """Create a downloadable package"""

    # Clean up any existing packages
    for item in Path(".").glob("paint-plus*"):
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Create package directory
    package_dir = Path("paint-plus-package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    # Copy essential files
    essential_files = [
        "main.py",
        "requirements.txt",
        "setup.py",
        "README.md",
        "IMPLEMENTATION_SUMMARY.md"
    ]

    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, package_dir / file)

    # Copy source directory
    if Path("src").exists():
        shutil.copytree("src", package_dir / "src")

    # Copy resources if exists
    if Path("resources").exists():
        shutil.copytree("resources", package_dir / "resources")

    # Create run script
    run_script = package_dir / "run.sh"
    run_script.write_text("""#!/bin/bash
echo "Installing dependencies..."
pip install PyQt6 numpy Pillow scipy opencv-python

echo "Starting Paint+..."
python main.py
""")
    run_script.chmod(0o755)

    # Create Windows batch file
    batch_script = package_dir / "run.bat"
    batch_script.write_text("""@echo off
echo Installing dependencies...
pip install PyQt6 numpy Pillow scipy opencv-python

echo Starting Paint+...
python main.py
pause
""")

    # Create README for package
    package_readme = package_dir / "PACKAGE_README.md"
    package_readme.write_text("""# Paint+ - Professional Image Editor

## Quick Start

### Linux/Mac:
```bash
chmod +x run.sh
./run.sh
```

### Windows:
```cmd
run.bat
```

### Manual Installation:
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python main.py`

## Requirements
- Python 3.11+
- PyQt6
- NumPy, Pillow, SciPy, OpenCV

## Features
- Professional image editing interface
- Layer system with blend modes
- Brush tool with advanced controls
- File I/O (PNG, JPEG, TIFF, WebP, BMP)
- Traditional Photoshop-style layout

## Documentation
See IMPLEMENTATION_SUMMARY.md for detailed documentation.
""")

    # Create ZIP archive
    shutil.make_archive("paint-plus-complete", "zip", ".", package_dir.name)

    # Create tar.gz archive
    shutil.make_archive("paint-plus-complete", "gztar", ".", package_dir.name)

    print("✅ Package created successfully!")
    print("📦 Files created:")
    print("   - paint-plus-complete.zip")
    print("   - paint-plus-complete.tar.gz")
    print(f"   - {package_dir.name}/ directory with all files")

    # Show package contents
    print(f"\n📋 Package contents:")
    for item in sorted(package_dir.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(package_dir)
            size = item.stat().st_size
            print(f"   {rel_path} ({size:,} bytes)")

if __name__ == "__main__":
    create_package()