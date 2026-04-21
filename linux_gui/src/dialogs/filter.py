"""Filter dialog showing hosts by status"""
from typing import List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem
)

from ..models import HostResult, HostStatus
from ..styles import COLORS


class FilterDialog(QDialog):
    """Dialog showing filtered list of hosts by status."""

    def __init__(self, status: HostStatus, results: List[HostResult], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{status.value} Hosts")
        self.setMinimumSize(360, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()

        title = QLabel(f"{status.value} Hosts ({len(results)})")
        title.setStyleSheet(
            f"font-family: monospace; font-size: 18px; font-weight: 600; color: {COLORS['ink']};"
        )

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.close)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)

        layout.addLayout(header)

        # List
        list_widget = QListWidget()
        list_widget.setStyleSheet(
            f"""
            QListWidget {{
                font-family: monospace;
                font-size: 12px;
                font-weight: 500;
                background: white;
                border: 1px solid {COLORS["gray_soft"]};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QListWidget::item:alternate {{
                background: rgba(77, 192, 204, 0.05);
            }}
            """
        )
        list_widget.setAlternatingRowColors(True)

        for result in results:
            item = QListWidgetItem(f"{result.ip}  —  {result.hostname}")
            list_widget.addItem(item)

        layout.addWidget(list_widget)
