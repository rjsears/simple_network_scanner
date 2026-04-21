"""Progress card with progress bar"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar

from ..styles import COLORS


class ProgressCard(QFrame):
    """Card showing scan progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header row
        header = QHBoxLayout()

        title = QLabel("Progress")
        title.setProperty("class", "progress-label")

        self._count_label = QLabel("0 / 0")
        self._count_label.setProperty("class", "progress-count")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._count_label)

        layout.addLayout(header)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)

        layout.addWidget(self._progress_bar)

        # Status text
        self._status_label = QLabel("Idle")
        self._status_label.setStyleSheet(
            f"font-family: monospace; font-size: 11px; font-weight: 500; color: {COLORS['gray']};"
        )

        layout.addWidget(self._status_label)

    def set_progress(self, current: int, total: int):
        """Update progress values."""
        self._count_label.setText(f"{current} / {total}")
        if total > 0:
            percentage = int((current / total) * 100)
            self._progress_bar.setValue(percentage)
        else:
            self._progress_bar.setValue(0)

    def set_status(self, status: str):
        """Update status text."""
        self._status_label.setText(status)

    def reset(self):
        """Reset to initial state."""
        self._progress_bar.setValue(0)
        self._count_label.setText("0 / 0")
        self._status_label.setText("Idle")
