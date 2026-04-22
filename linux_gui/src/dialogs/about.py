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
        self.setFixedSize(520, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Header
        header = QHBoxLayout()

        title_section = QHBoxLayout()
        title_section.setSpacing(10)

        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 24px;")

        about_label = QLabel("About")
        about_label.setStyleSheet(
            f"font-family: monospace; font-size: 16px; font-weight: 600; color: {COLORS['ink']};"
        )

        title_section.addWidget(info_icon)
        title_section.addWidget(about_label)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {COLORS["gray_soft"]};
                border: none;
                border-radius: 14px;
                font-size: 14px;
                color: {COLORS["gray"]};
            }}
            QPushButton:hover {{
                background: #d8dce3;
            }}
            """
        )
        close_btn.clicked.connect(self.close)

        header.addLayout(title_section)
        header.addStretch()
        header.addWidget(close_btn)

        layout.addLayout(header)

        # Divider
        layout.addWidget(self._divider())

        # App info
        app_name = QLabel("Simple Network Host Scanner")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet(
            f"font-family: monospace; font-size: 20px; font-weight: 600; color: {COLORS['ink']};"
        )

        app_type = QLabel("Linux Desktop Utility")
        app_type.setAlignment(Qt.AlignCenter)
        app_type.setStyleSheet(
            f"font-family: monospace; font-size: 12px; font-weight: 500; color: {COLORS['gray']};"
        )

        version_row = QHBoxLayout()
        version_row.setAlignment(Qt.AlignCenter)
        version_row.setSpacing(10)

        version_badge = QLabel("V1.0.0b")
        version_badge.setStyleSheet(
            f"""
            font-family: monospace;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            background: rgba(77, 192, 204, 0.35);
            border-radius: 10px;
            color: {COLORS["teal_strong"]};
            """
        )

        date_label = QLabel("2026-04-21")
        date_label.setStyleSheet(
            f"font-family: monospace; font-size: 11px; font-weight: 500; color: {COLORS['gray']};"
        )

        version_row.addWidget(version_badge)
        version_row.addWidget(date_label)

        layout.addWidget(app_name)
        layout.addWidget(app_type)
        layout.addLayout(version_row)

        # Divider
        layout.addWidget(self._divider())

        # Description
        desc = QLabel(
            "A simple, fast network host scanner for spotting live hosts "
            "and basic hostname discovery on local subnets."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(
            f"font-family: monospace; font-size: 12px; color: {COLORS['gray']};"
        )
        layout.addWidget(desc)

        # Divider
        layout.addWidget(self._divider())

        # Author
        dev_label = QLabel("Developed by")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet(
            f"font-family: monospace; font-size: 11px; font-weight: 500; color: {COLORS['gray']};"
        )

        author = QLabel("Richard J. Sears")
        author.setAlignment(Qt.AlignCenter)
        author.setStyleSheet(
            f"font-family: monospace; font-size: 13px; font-weight: 600; color: {COLORS['ink']};"
        )

        email = QLabel("richardjsears@protonmail.com")
        email.setAlignment(Qt.AlignCenter)
        email.setStyleSheet(
            f"font-family: monospace; font-size: 12px; font-weight: 500; color: {COLORS['teal_strong']};"
        )

        layout.addWidget(dev_label)
        layout.addWidget(author)
        layout.addWidget(email)

        # Divider
        layout.addWidget(self._divider())

        # GitHub link
        github_btn = QPushButton("🔗  View on GitHub  ↗")
        github_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: monospace;
                font-size: 12px;
                font-weight: 600;
                padding: 10px 16px;
                background: {COLORS["gray_soft"]};
                border: none;
                border-radius: 10px;
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

        # Close button
        layout.addStretch()

        close_btn2 = QPushButton("Close")
        close_btn2.setProperty("class", "primary")
        close_btn2.clicked.connect(self.close)

        btn_layout2 = QHBoxLayout()
        btn_layout2.setAlignment(Qt.AlignCenter)
        btn_layout2.addWidget(close_btn2)
        layout.addLayout(btn_layout2)

    def _divider(self) -> QFrame:
        """Create a horizontal divider."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {COLORS['gray_soft']}; max-height: 1px;")
        return line
