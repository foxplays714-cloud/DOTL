#!/usr/bin/env python3
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

    # Set application icon (if available)
    icon_path = Path(__file__).parent / "resources" / "icons" / "app.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

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