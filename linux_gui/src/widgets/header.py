"""Header widget with title and status indicator"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame

from ..styles import COLORS


class StatusIndicator(QFrame):
    """Status capsule showing scanning state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "status-capsule")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {COLORS['gray']}; font-size: 10px;")

        self._label = QLabel("IDLE")
        self._label.setStyleSheet(
            f"font-family: monospace; font-size: 12px; font-weight: 600; color: {COLORS['ink']};"
        )

        layout.addWidget(self._dot)
        layout.addWidget(self._label)

    def set_status(self, text: str, active: bool = False):
        """Update status text and indicator color."""
        self._label.setText(text.upper())
        color = COLORS["green"] if active else COLORS["gray"]
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")


class HeaderWidget(QWidget):
    """Header with title, author, and status indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left side - title and author
        left = QVBoxLayout()
        left.setSpacing(6)

        title = QLabel("Simple Network Host Scanner")
        title.setProperty("class", "title")

        author = QLabel("Richard J. Sears")
        author.setProperty("class", "subtitle")

        left.addWidget(title)
        left.addWidget(author)

        # Right side - status
        self._status = StatusIndicator()

        layout.addLayout(left)
        layout.addStretch()
        layout.addWidget(self._status)

    def set_status(self, text: str, active: bool = False):
        """Update the status indicator."""
        self._status.set_status(text, active)
