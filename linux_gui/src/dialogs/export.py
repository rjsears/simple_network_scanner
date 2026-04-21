"""Export dialog for saving results"""
from typing import List
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QFileDialog, QMessageBox
)

from ..models import HostResult
from ..export import export_to_csv, export_to_json
from ..styles import COLORS


class ExportDialog(QDialog):
    """Dialog for exporting scan results."""

    def __init__(self, results: List[HostResult], parent=None):
        super().__init__(parent)
        self._results = results

        self.setWindowTitle("Export Results")
        self.setFixedSize(400, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Title
        title = QLabel("Export Results")
        title.setStyleSheet(
            f"font-family: monospace; font-size: 18px; font-weight: 600; color: {COLORS['ink']};"
        )
        layout.addWidget(title)

        # Format selection
        format_label = QLabel("Select format:")
        format_label.setStyleSheet(
            f"font-family: monospace; font-size: 13px; color: {COLORS['gray']};"
        )
        layout.addWidget(format_label)

        format_row = QHBoxLayout()
        self._format_group = QButtonGroup(self)

        self._csv_radio = QRadioButton("CSV")
        self._csv_radio.setChecked(True)
        self._csv_radio.setStyleSheet("font-family: monospace;")

        self._json_radio = QRadioButton("JSON")
        self._json_radio.setStyleSheet("font-family: monospace;")

        self._format_group.addButton(self._csv_radio, 0)
        self._format_group.addButton(self._json_radio, 1)

        format_row.addWidget(self._csv_radio)
        format_row.addWidget(self._json_radio)
        format_row.addStretch()

        layout.addLayout(format_row)
        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.close)

        export_btn = QPushButton("Export...")
        export_btn.setProperty("class", "primary")
        export_btn.clicked.connect(self._do_export)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(export_btn)

        layout.addLayout(btn_row)

    def _do_export(self):
        """Perform the export."""
        is_csv = self._csv_radio.isChecked()

        if is_csv:
            filter_str = "CSV Files (*.csv)"
            default_name = "scan_results.csv"
        else:
            filter_str = "JSON Files (*.json)"
            default_name = "scan_results.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            str(Path.home() / default_name),
            filter_str
        )

        if not file_path:
            return

        try:
            if is_csv:
                export_to_csv(self._results, file_path)
            else:
                export_to_json(self._results, file_path)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Results exported to:\n{file_path}"
            )
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export: {e}"
            )
