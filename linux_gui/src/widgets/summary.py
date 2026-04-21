"""Summary card with clickable status pills"""
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton

from ..models import HostResult, HostStatus
from ..styles import COLORS, get_status_color


class SummaryPill(QPushButton):
    """Clickable pill showing status count."""

    def __init__(self, label: str, color: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "pill")
        self._label = label
        self._color = color
        self._count = 0
        self._update_text()

    def set_count(self, count: int):
        """Update the count value."""
        self._count = count
        self._update_text()

    def _update_text(self):
        """Update button text with colored dot."""
        self.setText(f"● {self._label}  {self._count}")
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS["card_solid"]};
                border: 1px solid {self._color}99;
                border-radius: 16px;
                padding: 8px 12px;
                font-family: monospace;
                font-size: 12px;
                font-weight: 600;
                color: {COLORS["ink"]};
            }}
            QPushButton:hover {{
                background-color: {self._color}15;
            }}
            """
        )


class SummaryCard(QFrame):
    """Card with summary pills for each status type."""

    status_clicked = Signal(HostStatus)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        self._pills = {}

        for status, label in [
            (HostStatus.UP, "UP"),
            (HostStatus.DOWN, "DOWN"),
            (HostStatus.NETWORK, "NET"),
            (HostStatus.BROADCAST, "BCAST"),
        ]:
            color = get_status_color(status.value)
            pill = SummaryPill(label, color)
            pill.clicked.connect(lambda checked, s=status: self.status_clicked.emit(s))
            layout.addWidget(pill)
            self._pills[status] = pill

        layout.addStretch()

    def update_counts(self, results: List[HostResult]):
        """Update all pill counts from results."""
        counts = {status: 0 for status in HostStatus}
        for result in results:
            counts[result.status] += 1

        for status, pill in self._pills.items():
            pill.set_count(counts[status])

    def reset(self):
        """Reset all counts to zero."""
        for pill in self._pills.values():
            pill.set_count(0)
