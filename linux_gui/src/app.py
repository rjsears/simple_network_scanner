"""Main application window"""
from typing import List

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedLayout

from .models import HostResult, HostStatus, create_scan_request
from .scanner import NetworkScanner, ScannerThread
from .widgets import (
    TechBackground,
    HeaderWidget,
    ControlsCard,
    ProgressCard,
    ResultsCard,
    SummaryCard,
)
from .dialogs import AboutDialog, FilterDialog, ExportDialog, PresetsDialog
from .presets import PresetManager


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Network Host Scanner")
        self.setMinimumSize(1100, 760)
        self.resize(1200, 820)

        self._scanner = NetworkScanner()
        self._scanner_thread: ScannerThread | None = None
        self._results: List[HostResult] = []
        self._preset_manager = PresetManager()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Build the UI layout."""
        # Central widget with stacked layout for background
        central = QWidget()
        self.setCentralWidget(central)

        stack = QStackedLayout(central)
        stack.setStackingMode(QStackedLayout.StackAll)

        # Background layer
        self._background = TechBackground()
        stack.addWidget(self._background)

        # Content layer
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground)
        stack.addWidget(content)

        # Main layout
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Widgets
        self._header = HeaderWidget()
        self._controls = ControlsCard()
        self._progress = ProgressCard()
        self._results_card = ResultsCard()
        self._summary = SummaryCard()

        layout.addWidget(self._header)
        layout.addWidget(self._controls)
        layout.addWidget(self._progress)
        layout.addWidget(self._results_card, 1)  # Stretch
        layout.addWidget(self._summary)

        # Menu bar
        self._setup_menu()

    def _setup_menu(self):
        """Set up the menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("&Export Results...", self._show_export_dialog)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("&About", self._show_about_dialog)

    def _connect_signals(self):
        """Connect widget signals to slots."""
        # Controls
        self._controls.start_clicked.connect(self._start_scan)
        self._controls.cancel_clicked.connect(self._cancel_scan)
        self._controls.presets_clicked.connect(self._show_presets_dialog)

        # Scanner
        self._scanner.progress_updated.connect(self._on_progress)
        self._scanner.result_ready.connect(self._on_result)
        self._scanner.scan_complete.connect(self._on_scan_complete)
        self._scanner.scan_cancelled.connect(self._on_scan_cancelled)

        # Summary pills
        self._summary.status_clicked.connect(self._show_filter_dialog)

    @Slot()
    def _start_scan(self):
        """Start a network scan."""
        self._controls.clear_error()

        request = create_scan_request(
            self._controls.start_ip,
            self._controls.host_count,
            self._controls.cidr
        )

        if request is None:
            self._controls.show_error("Invalid input. Check IP, host count, and CIDR.")
            return

        # Reset state
        self._results = []
        self._results_card.clear()
        self._summary.reset()
        self._progress.reset()
        self._progress.set_progress(0, len(request.ip_list))

        # Update UI
        self._controls.set_scanning(True)
        self._header.set_status("Scanning", active=True)
        self._progress.set_status("Active scan")

        # Start scan thread
        self._scanner_thread = ScannerThread(self._scanner, request)
        self._scanner_thread.start()

    @Slot()
    def _cancel_scan(self):
        """Cancel the current scan."""
        if self._scanner_thread and self._scanner_thread.isRunning():
            self._scanner.cancel()

    @Slot(int, int)
    def _on_progress(self, current: int, total: int):
        """Handle progress updates."""
        self._progress.set_progress(current, total)

    @Slot(HostResult)
    def _on_result(self, result: HostResult):
        """Handle a new scan result."""
        self._results.append(result)
        self._results_card.add_result(result)
        self._summary.update_counts(self._results)

    @Slot()
    def _on_scan_complete(self):
        """Handle scan completion."""
        self._controls.set_scanning(False)
        self._header.set_status("Complete", active=False)
        self._progress.set_status("Scan complete")
        self._scanner_thread = None

    @Slot()
    def _on_scan_cancelled(self):
        """Handle scan cancellation."""
        self._controls.set_scanning(False)
        self._header.set_status("Cancelled", active=False)
        self._progress.set_status("Scan cancelled")
        self._scanner_thread = None

    @Slot(HostStatus)
    def _show_filter_dialog(self, status: HostStatus):
        """Show filtered list dialog."""
        filtered = [r for r in self._results if r.status == status]
        dialog = FilterDialog(status, filtered, self)
        dialog.exec()

    def _show_about_dialog(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_export_dialog(self):
        """Show export dialog."""
        if not self._results:
            return
        dialog = ExportDialog(self._results, self)
        dialog.exec()

    def _show_presets_dialog(self):
        """Show presets dialog."""
        dialog = PresetsDialog(self._preset_manager, self)
        dialog.preset_selected.connect(self._load_preset)
        dialog.exec()

    @Slot(str, str, str)
    def _load_preset(self, start_ip: str, host_count: str, cidr: str):
        """Load a preset into the controls."""
        self._controls.set_values(start_ip, host_count, cidr)
