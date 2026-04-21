"""Controls card with scan inputs and buttons"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)

from ..styles import COLORS


class LabeledInput(QWidget):
    """Input field with label above."""

    def __init__(self, label: str, placeholder: str = "", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setProperty("class", "input-label")

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)

        layout.addWidget(lbl)
        layout.addWidget(self.input)

    def text(self) -> str:
        return self.input.text().strip()

    def set_text(self, text: str):
        self.input.setText(text)

    def set_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)


class ControlsCard(QFrame):
    """Card containing scan parameter inputs and action buttons."""

    start_clicked = Signal()
    cancel_clicked = Signal()
    presets_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Title
        title = QLabel("Scan Parameters")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Inputs row
        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(16)

        self._start_ip = LabeledInput("Start IP", "10.0.0.1")
        self._host_count = LabeledInput("Hosts", "64")
        self._host_count.setFixedWidth(120)
        self._cidr = LabeledInput("CIDR", "24")
        self._cidr.setFixedWidth(120)

        inputs_row.addWidget(self._start_ip)
        inputs_row.addWidget(self._host_count)
        inputs_row.addWidget(self._cidr)
        inputs_row.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self._presets_btn = QPushButton("Presets")
        self._presets_btn.setProperty("class", "secondary")
        self._presets_btn.clicked.connect(self.presets_clicked.emit)

        self._start_btn = QPushButton("Start Scan")
        self._start_btn.setProperty("class", "primary")
        self._start_btn.clicked.connect(self.start_clicked.emit)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setProperty("class", "secondary")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self.cancel_clicked.emit)

        buttons_layout.addWidget(self._presets_btn)
        buttons_layout.addWidget(self._start_btn)
        buttons_layout.addWidget(self._cancel_btn)

        inputs_row.addLayout(buttons_layout)
        layout.addLayout(inputs_row)

        # Error label
        self._error_label = QLabel()
        self._error_label.setStyleSheet(
            f"font-family: monospace; font-size: 12px; font-weight: 500; color: {COLORS['red']};"
        )
        self._error_label.hide()
        layout.addWidget(self._error_label)

    @property
    def start_ip(self) -> str:
        return self._start_ip.text()

    @property
    def host_count(self) -> str:
        return self._host_count.text()

    @property
    def cidr(self) -> str:
        return self._cidr.text()

    def set_values(self, start_ip: str, host_count: str, cidr: str):
        """Set input values (e.g., from preset)."""
        self._start_ip.set_text(start_ip)
        self._host_count.set_text(host_count)
        self._cidr.set_text(cidr)

    def set_scanning(self, scanning: bool):
        """Update UI for scanning state."""
        self._start_ip.set_enabled(not scanning)
        self._host_count.set_enabled(not scanning)
        self._cidr.set_enabled(not scanning)
        self._start_btn.setEnabled(not scanning)
        self._cancel_btn.setEnabled(scanning)
        self._presets_btn.setEnabled(not scanning)

    def show_error(self, message: str):
        """Display error message."""
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self):
        """Hide error message."""
        self._error_label.hide()
