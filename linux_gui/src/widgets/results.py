"""Results table widget"""
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor

from ..models import HostResult, HostStatus
from ..styles import COLORS, get_status_color


class ResultsCard(QFrame):
    """Card containing the results table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Title
        title = QLabel("Results")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["IP", "Status", "Hostname"])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        # Column widths
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 120)
        self._table.setColumnWidth(1, 80)

        layout.addWidget(self._table)

        self._results: List[HostResult] = []

    def add_result(self, result: HostResult):
        """Add a single result and re-sort."""
        self._results.append(result)
        self._results.sort()
        self._refresh_table()

    def set_results(self, results: List[HostResult]):
        """Set all results at once."""
        self._results = sorted(results)
        self._refresh_table()

    def clear(self):
        """Clear all results."""
        self._results = []
        self._table.setRowCount(0)

    def get_results(self) -> List[HostResult]:
        """Get current results."""
        return self._results.copy()

    def _refresh_table(self):
        """Rebuild table from results."""
        self._table.setRowCount(len(self._results))

        for row, result in enumerate(self._results):
            # IP column
            ip_item = QTableWidgetItem(result.ip)
            ip_color = self._get_ip_color(result.status)
            ip_item.setForeground(QColor(ip_color))
            self._table.setItem(row, 0, ip_item)

            # Status column
            status_text = result.status.value
            if result.status in (HostStatus.UP, HostStatus.DOWN):
                status_text = f"● {status_text}"
            else:
                status_text = f"◆ {status_text}"

            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(get_status_color(result.status.value)))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 1, status_item)

            # Hostname column
            hostname = result.hostname
            if len(hostname) > 50:
                hostname = hostname[:47] + "..."
            hostname_item = QTableWidgetItem(hostname)
            self._table.setItem(row, 2, hostname_item)

    def _get_ip_color(self, status: HostStatus) -> str:
        """Get IP text color based on status."""
        if status == HostStatus.UP:
            return COLORS["ink"]
        elif status == HostStatus.DOWN:
            return "#b8860b"  # Dark goldenrod
        elif status == HostStatus.NETWORK:
            return COLORS["cyan"]
        elif status == HostStatus.BROADCAST:
            return COLORS["purple"]
        return COLORS["ink"]
