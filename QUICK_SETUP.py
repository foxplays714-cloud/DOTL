#!/usr/bin/env python3
"""
Quick setup script to recreate Paint+ locally
Just copy this entire file and run it in your local directory!
"""

import os
import subprocess
from pathlib import Path

def create_project_structure():
    """Create the project directory structure"""

    directories = [
        "src/app",
        "src/ui/panels",
        "src/ui/widgets",
        "src/ui/dialogs",
        "src/canvas",
        "src/tools",
        "src/layers",
        "src/io/format_handlers",
        "src/image_processing/filters",
        "src/performance",
        "src/plugins/api",
        "src/utils",
        "tests/unit_tests",
        "tests/integration_tests",
        "tests/performance_tests",
        "docs/user_manual",
        "docs/api_reference",
        "docs/developer_guide",
        "scripts",
        "resources/icons",
        "resources/brushes",
        "resources/gradients",
        "resources/patterns",
        "resources/fonts",
        "resources/themes"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory.startswith("src/") or directory.startswith("tests/"):
            Path(f"{directory}/__init__.py").touch()

def create_main_files():
    """Create essential files"""

    # requirements.txt
    requirements = """PyQt6>=6.5.0
PyQt6-tools>=6.5.0
numpy>=1.24.0
Pillow>=10.0.0
opencv-python>=4.8.0
PyOpenGL>=3.1.0
PyOpenGL-accelerate>=3.1.0
scipy>=1.10.0
pytest>=7.0.0
pytest-qt>=4.2.0
setuptools>=65.0.0
wheel>=0.37.0
pyinstaller>=5.0.0"""

    Path("requirements.txt").write_text(requirements)

    # main.py
    main_py = '''#!/usr/bin/env python3
"""
Paint+ - Professional Image Editor
Main application entry point
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QIcon

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.application import PaintPlusApplication
from src.app.config import Config

def main():
    """Main application entry point"""

    # Set high DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Paint+")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Paint+ Team")
    app.setOrganizationDomain("paintplus.app")

    # Initialize configuration
    config = Config()

    # Create main application
    paint_app = PaintPlusApplication(config)

    # Show main window
    paint_app.show_main_window()

    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''

    Path("main.py").write_text(main_py)

    # README.md
    readme = """# Paint+

A professional image editor built with PyQt6.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Features

- Professional image editing interface
- Layer system with blend modes
- Brush tool with advanced controls
- File I/O (PNG, JPEG, TIFF, WebP, BMP)
- Traditional Photoshop-style layout

## Requirements

- Python 3.11+
- PyQt6
- NumPy, Pillow, SciPy, OpenCV

## License

MIT License
"""

    Path("README.md").write_text(readme)

def run_setup():
    """Run the complete setup"""
    print("🎨 Setting up Paint+...")

    create_project_structure()
    print("✅ Created project structure")

    create_main_files()
    print("✅ Created main files")

    # Try to install dependencies
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Installed dependencies")
    except subprocess.CalledProcessError:
        print("⚠️  Could not install dependencies automatically")
        print("   Please run: pip install -r requirements.txt")

    print("\n🎉 Paint+ setup complete!")
    print("\nNext steps:")
    print("1. python main.py    # Run the application")
    print("2. Read README.md    # For more information")
    print("3. Enjoy Paint+! 🎨")

if __name__ == "__main__":
    run_setup()