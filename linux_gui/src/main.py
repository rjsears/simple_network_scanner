#!/usr/bin/env python3
"""Simple Network Scanner - Linux Desktop Application"""
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from pathlib import Path

from .app import MainWindow
from .styles import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Network Host Scanner")
    app.setOrganizationName("RJSears")
    app.setApplicationVersion("1.0.0")

    # Set app icon
    assets_dir = Path(__file__).parent.parent / "assets"
    icon_path = assets_dir / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Apply stylesheet
    app.setStyleSheet(STYLESHEET)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
