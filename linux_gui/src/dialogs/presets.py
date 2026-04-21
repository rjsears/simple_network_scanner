"""Presets dialog for managing scan configurations"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit,
    QMessageBox, QFrame
)

from ..presets import PresetManager, Preset
from ..styles import COLORS


class PresetsDialog(QDialog):
    """Dialog for managing scan presets."""

    preset_selected = Signal(str, str, str)  # start_ip, host_count, cidr

    def __init__(self, preset_manager: PresetManager, parent=None):
        super().__init__(parent)
        self._manager = preset_manager

        self.setWindowTitle("Scan Presets")
        self.setMinimumSize(450, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Scan Presets")
        title.setStyleSheet(
            f"font-family: monospace; font-size: 18px; font-weight: 600; color: {COLORS['ink']};"
        )
        layout.addWidget(title)

        # List
        self._list = QListWidget()
        self._list.setStyleSheet(
            f"""
            QListWidget {{
                font-family: monospace;
                font-size: 13px;
                background: white;
                border: 1px solid {COLORS["gray_soft"]};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background: rgba(77, 192, 204, 0.2);
                color: {COLORS["ink"]};
            }}
            """
        )
        self._list.itemDoubleClicked.connect(self._load_selected)
        layout.addWidget(self._list)

        # Action buttons
        action_row = QHBoxLayout()

        load_btn = QPushButton("Load")
        load_btn.setProperty("class", "primary")
        load_btn.clicked.connect(self._load_selected)

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "secondary")
        delete_btn.clicked.connect(self._delete_selected)

        action_row.addWidget(load_btn)
        action_row.addWidget(delete_btn)
        action_row.addStretch()

        layout.addLayout(action_row)

        # Save new preset section
        layout.addWidget(self._divider())

        save_label = QLabel("Save Current Settings as Preset:")
        save_label.setStyleSheet(
            f"font-family: monospace; font-size: 13px; font-weight: 600; color: {COLORS['ink']};"
        )
        layout.addWidget(save_label)

        save_row = QHBoxLayout()

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Preset name...")

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self._save_preset)

        save_row.addWidget(self._name_input)
        save_row.addWidget(save_btn)

        layout.addLayout(save_row)

        # Close button
        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.close)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

        # Load presets
        self._refresh_list()

    def set_current_values(self, start_ip: str, host_count: str, cidr: str):
        """Set values to save as new preset."""
        self._current_start_ip = start_ip
        self._current_host_count = host_count
        self._current_cidr = cidr

    def _refresh_list(self):
        """Reload the presets list."""
        self._list.clear()
        for preset in self._manager.get_all():
            text = f"{preset.name}  —  {preset.start_ip}/{preset.cidr} ({preset.host_count} hosts)"
            item = QListWidgetItem(text)
            item.setData(256, preset.name)  # Store name in user role
            self._list.addItem(item)

    def _load_selected(self):
        """Load the selected preset."""
        item = self._list.currentItem()
        if not item:
            return

        name = item.data(256)
        preset = self._manager.get(name)
        if preset:
            self.preset_selected.emit(preset.start_ip, preset.host_count, preset.cidr)
            self.close()

    def _delete_selected(self):
        """Delete the selected preset."""
        item = self._list.currentItem()
        if not item:
            return

        name = item.data(256)
        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f"Delete preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._manager.delete(name)
            self._refresh_list()

    def _save_preset(self):
        """Save a new preset."""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a preset name.")
            return

        # Get current values from parent window's controls
        parent = self.parent()
        if hasattr(parent, "_controls"):
            controls = parent._controls
            preset = Preset(
                name=name,
                start_ip=controls.start_ip,
                host_count=controls.host_count,
                cidr=controls.cidr
            )
            self._manager.save(preset)
            self._name_input.clear()
            self._refresh_list()
            QMessageBox.information(self, "Saved", f"Preset '{name}' saved.")

    def _divider(self):
        """Create horizontal divider."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {COLORS['gray_soft']}; max-height: 1px;")
        return line
