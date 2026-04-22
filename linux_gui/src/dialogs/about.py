"""About dialog"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtGui import QDesktopServices

from ..styles import COLORS


class AboutDialog(QDialog):
    """About dialog showing app info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(550, 620)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {COLORS['surface_light']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # App name
        app_name = QLabel("Simple Network\nHost Scanner")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet(
            f"font-family: monospace; font-size: 22px; font-weight: 700; "
            f"color: {COLORS['ink']}; line-height: 1.3;"
        )
        layout.addWidget(app_name)

        # Version and date row
        version_row = QHBoxLayout()
        version_row.setAlignment(Qt.AlignCenter)
        version_row.setSpacing(12)

        version_badge = QLabel("V1.0.0b")
        version_badge.setStyleSheet(
            f"font-family: monospace; font-size: 12px; font-weight: 600; "
            f"padding: 6px 14px; background: rgba(77, 192, 204, 0.3); "
            f"border-radius: 12px; color: {COLORS['teal_strong']};"
        )

        date_label = QLabel("2026-04-21")
        date_label.setStyleSheet(
            f"font-family: monospace; font-size: 12px; color: {COLORS['gray']};"
        )

        version_row.addWidget(version_badge)
        version_row.addWidget(date_label)
        layout.addLayout(version_row)

        layout.addSpacing(8)

        # Platform
        platform_label = QLabel("Linux Desktop Edition")
        platform_label.setAlignment(Qt.AlignCenter)
        platform_label.setStyleSheet(
            f"font-family: monospace; font-size: 13px; font-weight: 500; "
            f"color: {COLORS['teal_strong']};"
        )
        layout.addWidget(platform_label)

        layout.addSpacing(16)
        layout.addWidget(self._divider())
        layout.addSpacing(16)

        # Description
        desc = QLabel(
            "A simple, fast network host scanner for\n"
            "spotting live hosts and performing basic\n"
            "hostname discovery on local subnets."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(
            f"font-family: monospace; font-size: 13px; color: {COLORS['gray']}; "
            f"line-height: 1.5;"
        )
        layout.addWidget(desc)

        layout.addSpacing(16)
        layout.addWidget(self._divider())
        layout.addSpacing(16)

        # Author section
        dev_label = QLabel("Developed by")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet(
            f"font-family: monospace; font-size: 11px; color: {COLORS['gray']};"
        )
        layout.addWidget(dev_label)

        author = QLabel("Richard J. Sears")
        author.setAlignment(Qt.AlignCenter)
        author.setStyleSheet(
            f"font-family: monospace; font-size: 15px; font-weight: 600; "
            f"color: {COLORS['ink']};"
        )
        layout.addWidget(author)

        email = QLabel("richardjsears@protonmail.com")
        email.setAlignment(Qt.AlignCenter)
        email.setStyleSheet(
            f"font-family: monospace; font-size: 12px; color: {COLORS['teal_strong']};"
        )
        layout.addWidget(email)

        layout.addStretch()

        # GitHub button
        github_btn = QPushButton("View on GitHub")
        github_btn.setFixedWidth(180)
        github_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: monospace;
                font-size: 13px;
                font-weight: 600;
                padding: 12px 20px;
                background: {COLORS["gray_soft"]};
                border: none;
                border-radius: 8px;
                color: {COLORS["ink"]};
            }}
            QPushButton:hover {{
                background: #d8dce3;
            }}
            """
        )
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/rjsears/simple_network_scanner"))
        )

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(github_btn)
        layout.addLayout(btn_layout)

        layout.addSpacing(12)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: monospace;
                font-size: 13px;
                font-weight: 600;
                padding: 12px 20px;
                background: {COLORS["teal_strong"]};
                border: none;
                border-radius: 8px;
                color: white;
            }}
            QPushButton:hover {{
                background: #007a8a;
            }}
            """
        )
        close_btn.clicked.connect(self.close)

        close_layout = QHBoxLayout()
        close_layout.setAlignment(Qt.AlignCenter)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def _divider(self) -> QFrame:
        """Create a horizontal divider."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {COLORS['gray_soft']};")
        return line
