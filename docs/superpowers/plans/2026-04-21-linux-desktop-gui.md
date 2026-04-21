# Linux Desktop GUI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished PySide6 desktop application for Ubuntu 25 that matches the macOS SwiftUI version's visual design and adds export/preset features.

**Architecture:** Card-based UI with QSS styling matching the macOS teal theme. NetworkScanner runs in QThread for non-blocking UI. Signals connect scanner progress/results to UI updates. Presets stored in ~/.config, exports via file dialogs.

**Tech Stack:** Python 3.10+, PySide6, concurrent.futures for parallel scanning

---

## Chunk 1: Project Setup & Core Models

### Task 1.1: Create Directory Structure

**Files:**
- Create: `linux_gui/src/__init__.py`
- Create: `linux_gui/src/widgets/__init__.py`
- Create: `linux_gui/src/dialogs/__init__.py`
- Create: `linux_gui/assets/.gitkeep`
- Create: `linux_gui/packaging/debian/.gitkeep`
- Create: `linux_gui/packaging/appimage/.gitkeep`
- Create: `linux_gui/requirements.txt`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p linux_gui/src/widgets linux_gui/src/dialogs linux_gui/assets linux_gui/packaging/debian linux_gui/packaging/appimage
```

- [ ] **Step 2: Create __init__.py files**

Create `linux_gui/src/__init__.py`:
```python
"""Simple Network Scanner - Linux Desktop GUI"""
__version__ = "1.0.0"
```

Create `linux_gui/src/widgets/__init__.py`:
```python
"""UI widget components"""
```

Create `linux_gui/src/dialogs/__init__.py`:
```python
"""Dialog components"""
```

- [ ] **Step 3: Create requirements.txt**

Create `linux_gui/requirements.txt`:
```
PySide6>=6.6.0
```

- [ ] **Step 4: Commit**

```bash
git add linux_gui/
git commit -m "feat(linux): initialize project structure"
```

---

### Task 1.2: Create Data Models

**Files:**
- Create: `linux_gui/src/models.py`

- [ ] **Step 1: Create models.py with enums and dataclasses**

Create `linux_gui/src/models.py`:
```python
"""Data models for network scanner"""
from dataclasses import dataclass
from enum import Enum
from typing import List


class HostStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    NETWORK = "NTWRK"
    BROADCAST = "BCAST"


class IPType(Enum):
    HOST = "HOST"
    NETWORK = "NETWORK"
    BROADCAST = "BROADCAST"


@dataclass
class IPInfo:
    ip: str
    ip_type: IPType
    ip_int: int


@dataclass
class HostResult:
    ip: str
    status: HostStatus
    hostname: str
    ip_int: int

    def __lt__(self, other):
        return self.ip_int < other.ip_int


@dataclass
class ScanRequest:
    start_ip: str
    host_count: int
    cidr: int
    ip_list: List[IPInfo]


def ip_to_int(ip: str) -> int:
    """Convert IP address string to integer."""
    parts = ip.split(".")
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def int_to_ip(num: int) -> str:
    """Convert integer to IP address string."""
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def get_ip_type(ip_int: int, cidr: int) -> IPType:
    """Determine if IP is network, broadcast, or host address."""
    if cidr >= 31:
        return IPType.HOST
    
    block_size = 1 << (32 - cidr)
    network = (ip_int // block_size) * block_size
    broadcast = network + block_size - 1
    
    if ip_int == network:
        return IPType.NETWORK
    elif ip_int == broadcast:
        return IPType.BROADCAST
    return IPType.HOST


def is_valid_ip(ip: str) -> bool:
    """Validate IP address format."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except ValueError:
        return False


def generate_ip_list(start_ip: str, num_hosts: int, cidr: int) -> List[IPInfo]:
    """Generate list of IP addresses to scan."""
    if not is_valid_ip(start_ip):
        return []
    
    ip_list = []
    current = ip_to_int(start_ip)
    hosts_found = 0
    
    while hosts_found < num_hosts:
        if current > 0xFFFFFFFF:
            break
        
        ip_type = get_ip_type(current, cidr)
        ip_list.append(IPInfo(
            ip=int_to_ip(current),
            ip_type=ip_type,
            ip_int=current
        ))
        
        if ip_type == IPType.HOST:
            hosts_found += 1
        
        current += 1
    
    return ip_list


def create_scan_request(start_ip: str, host_count: str, cidr: str) -> ScanRequest | None:
    """Create a ScanRequest from user input, or None if invalid."""
    try:
        host_count_int = int(host_count)
        cidr_int = int(cidr)
    except ValueError:
        return None
    
    if host_count_int <= 0 or not (8 <= cidr_int <= 32):
        return None
    
    if not is_valid_ip(start_ip):
        return None
    
    ip_list = generate_ip_list(start_ip, host_count_int, cidr_int)
    if not ip_list:
        return None
    
    return ScanRequest(
        start_ip=start_ip,
        host_count=host_count_int,
        cidr=cidr_int,
        ip_list=ip_list
    )
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/models.py
git commit -m "feat(linux): add data models for scanner"
```

---

## Chunk 2: Network Scanner

### Task 2.1: Create Network Scanner with QThread

**Files:**
- Create: `linux_gui/src/scanner.py`

- [ ] **Step 1: Create scanner.py**

Create `linux_gui/src/scanner.py`:
```python
"""Network scanner with Qt threading support"""
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from PySide6.QtCore import QObject, Signal, QThread

from .models import IPInfo, IPType, HostResult, HostStatus, ScanRequest


class NetworkScanner(QObject):
    """Performs network scanning operations."""
    
    progress_updated = Signal(int, int)  # current, total
    result_ready = Signal(HostResult)
    scan_complete = Signal()
    scan_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False
    
    def cancel(self):
        """Request scan cancellation."""
        self._cancelled = True
    
    def scan(self, request: ScanRequest):
        """Run the scan. Call from a worker thread."""
        self._cancelled = False
        total = len(request.ip_list)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {
                executor.submit(self._scan_host, ip_info): ip_info 
                for ip_info in request.ip_list
            }
            
            for future in as_completed(futures):
                if self._cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    self.scan_cancelled.emit()
                    return
                
                result = future.result()
                self.result_ready.emit(result)
                completed += 1
                self.progress_updated.emit(completed, total)
        
        self.scan_complete.emit()
    
    def _scan_host(self, ip_info: IPInfo) -> HostResult:
        """Scan a single host."""
        if ip_info.ip_type == IPType.NETWORK:
            return HostResult(
                ip=ip_info.ip,
                status=HostStatus.NETWORK,
                hostname="-",
                ip_int=ip_info.ip_int
            )
        
        if ip_info.ip_type == IPType.BROADCAST:
            return HostResult(
                ip=ip_info.ip,
                status=HostStatus.BROADCAST,
                hostname="-",
                ip_int=ip_info.ip_int
            )
        
        is_up = self._ping_host(ip_info.ip)
        hostname = self._reverse_dns(ip_info.ip)
        
        return HostResult(
            ip=ip_info.ip,
            status=HostStatus.UP if is_up else HostStatus.DOWN,
            hostname=hostname,
            ip_int=ip_info.ip_int
        )
    
    def _ping_host(self, ip: str) -> bool:
        """Ping host and return True if it responds."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _reverse_dns(self, ip: str) -> str:
        """Get hostname via reverse DNS lookup."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except (socket.herror, socket.gaierror):
            return "-"
        except Exception:
            return "-"


class ScannerThread(QThread):
    """Worker thread for running scans."""
    
    def __init__(self, scanner: NetworkScanner, request: ScanRequest, parent=None):
        super().__init__(parent)
        self.scanner = scanner
        self.request = request
    
    def run(self):
        self.scanner.scan(self.request)
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/scanner.py
git commit -m "feat(linux): add network scanner with threading"
```

---

## Chunk 3: Styling

### Task 3.1: Create QSS Stylesheet

**Files:**
- Create: `linux_gui/src/styles.py`

- [ ] **Step 1: Create styles.py with color palette and QSS**

Create `linux_gui/src/styles.py`:
```python
"""Qt Style Sheets for the application"""

# Color palette matching macOS version
COLORS = {
    "surface_light": "#f2f7fc",
    "surface_mid": "#e0e8f0",
    "card": "rgba(255, 255, 255, 0.9)",
    "card_solid": "#ffffff",
    "input": "#ffffff",
    "ink": "#141f2e",
    "gray": "#596b7d",
    "gray_soft": "#e6eaef",
    "teal_strong": "#008c9e",
    "teal_soft": "#4dc0cc",
    "green": "#1a994d",
    "red": "#d13e33",
    "cyan": "#1a99b3",
    "purple": "#735ab3",
    "shadow": "rgba(0, 0, 0, 0.08)",
}

STYLESHEET = f"""
/* Main Window */
QMainWindow {{
    background: transparent;
}}

/* Cards */
QFrame[class="card"] {{
    background-color: {COLORS["card"]};
    border: 1px solid rgba(77, 192, 204, 0.7);
    border-radius: 16px;
}}

/* Labels */
QLabel {{
    color: {COLORS["ink"]};
    font-family: monospace;
}}

QLabel[class="title"] {{
    font-size: 28px;
    font-weight: 600;
}}

QLabel[class="subtitle"] {{
    font-size: 14px;
    font-weight: 500;
    color: {COLORS["teal_strong"]};
}}

QLabel[class="section-title"] {{
    font-size: 16px;
    font-weight: 600;
}}

QLabel[class="input-label"] {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS["gray"]};
}}

QLabel[class="progress-label"] {{
    font-size: 14px;
    font-weight: 600;
}}

QLabel[class="progress-count"] {{
    font-size: 12px;
    font-weight: 500;
    color: {COLORS["teal_strong"]};
}}

/* Input Fields */
QLineEdit {{
    background-color: {COLORS["input"]};
    border: 1px solid {COLORS["teal_soft"]};
    border-radius: 6px;
    padding: 8px;
    font-family: monospace;
    font-size: 13px;
    color: {COLORS["ink"]};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS["teal_strong"]};
}}

/* Buttons */
QPushButton {{
    font-family: monospace;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 8px;
    border: none;
}}

QPushButton[class="primary"] {{
    background-color: {COLORS["teal_strong"]};
    color: white;
}}

QPushButton[class="primary"]:hover {{
    background-color: #007a8a;
}}

QPushButton[class="primary"]:pressed {{
    background-color: #006778;
}}

QPushButton[class="primary"]:disabled {{
    background-color: {COLORS["gray_soft"]};
    color: {COLORS["gray"]};
}}

QPushButton[class="secondary"] {{
    background-color: {COLORS["gray_soft"]};
    color: {COLORS["ink"]};
}}

QPushButton[class="secondary"]:hover {{
    background-color: #d8dce3;
}}

QPushButton[class="secondary"]:disabled {{
    color: #aaa;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS["gray_soft"]};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS["teal_strong"]};
    border-radius: 4px;
}}

/* Table */
QTableWidget {{
    background-color: {COLORS["card_solid"]};
    border: none;
    border-radius: 8px;
    gridline-color: {COLORS["gray_soft"]};
    font-family: monospace;
    font-size: 12px;
}}

QTableWidget::item {{
    padding: 8px;
    color: {COLORS["ink"]};
}}

QTableWidget::item:alternate {{
    background-color: rgba(77, 192, 204, 0.05);
}}

QHeaderView::section {{
    background-color: {COLORS["gray_soft"]};
    color: {COLORS["ink"]};
    font-family: monospace;
    font-size: 12px;
    font-weight: 600;
    padding: 10px;
    border: none;
}}

/* Scroll Bar */
QScrollBar:vertical {{
    background: {COLORS["gray_soft"]};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS["teal_soft"]};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* Summary Pills */
QPushButton[class="pill"] {{
    background-color: {COLORS["card_solid"]};
    border: 1px solid rgba(77, 192, 204, 0.6);
    border-radius: 16px;
    padding: 8px 12px;
    font-size: 12px;
}}

QPushButton[class="pill"]:hover {{
    background-color: rgba(77, 192, 204, 0.1);
}}

/* Status Capsule */
QFrame[class="status-capsule"] {{
    background-color: {COLORS["card_solid"]};
    border: 1px solid {COLORS["teal_soft"]};
    border-radius: 16px;
    padding: 8px 12px;
}}

/* Dialogs */
QDialog {{
    background-color: {COLORS["surface_light"]};
}}
"""


def get_status_color(status_name: str) -> str:
    """Get color for a status type."""
    colors = {
        "UP": COLORS["green"],
        "DOWN": COLORS["red"],
        "NTWRK": COLORS["cyan"],
        "BCAST": COLORS["purple"],
    }
    return colors.get(status_name, COLORS["gray"])
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/styles.py
git commit -m "feat(linux): add QSS stylesheet with teal theme"
```

---

### Task 3.2: Create Background Widget

**Files:**
- Create: `linux_gui/src/widgets/background.py`

- [ ] **Step 1: Create background.py with tech grid overlay**

Create `linux_gui/src/widgets/background.py`:
```python
"""Tech-styled background widget with grid overlay"""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPixmap, QBrush
from PySide6.QtWidgets import QWidget


class TechBackground(QWidget):
    """Background widget with gradient, optional image, and grid overlay."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._background_image = None
        self._load_background_image()
    
    def _load_background_image(self):
        """Try to load the background image."""
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        image_path = assets_dir / "map_background.png"
        if image_path.exists():
            self._background_image = QPixmap(str(image_path))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        
        # Draw background image or gradient
        if self._background_image and not self._background_image.isNull():
            scaled = self._background_image.scaled(
                rect.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (rect.width() - scaled.width()) // 2
            y = (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            
            # White overlay for readability
            painter.fillRect(rect, QColor(255, 255, 255, 70))
        else:
            # Gradient fallback
            gradient = QLinearGradient(0, 0, rect.width(), rect.height())
            gradient.setColorAt(0, QColor("#f2f7fc"))
            gradient.setColorAt(1, QColor("#e0e8f0"))
            painter.fillRect(rect, gradient)
        
        # Radial glow in top-right
        glow_center_x = rect.width() - 100
        glow_center_y = 100
        for radius in range(400, 50, -50):
            alpha = int(30 * (1 - radius / 400))
            color = QColor(77, 192, 204, alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                glow_center_x - radius,
                glow_center_y - radius,
                radius * 2,
                radius * 2
            )
        
        # Grid overlay
        self._draw_grid(painter, rect)
    
    def _draw_grid(self, painter: QPainter, rect):
        """Draw a subtle grid overlay."""
        pen = QPen(QColor(77, 192, 204, 40))
        pen.setWidth(1)
        painter.setPen(pen)
        
        step = 40
        
        # Vertical lines
        x = 0
        while x <= rect.width():
            painter.drawLine(x, 0, x, rect.height())
            x += step
        
        # Horizontal lines
        y = 0
        while y <= rect.height():
            painter.drawLine(0, y, rect.width(), y)
            y += step
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/background.py
git commit -m "feat(linux): add tech background widget with grid"
```

---

## Chunk 4: Core Widgets

### Task 4.1: Create Header Widget

**Files:**
- Create: `linux_gui/src/widgets/header.py`

- [ ] **Step 1: Create header.py**

Create `linux_gui/src/widgets/header.py`:
```python
"""Header widget with title and status indicator"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QColor

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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/header.py
git commit -m "feat(linux): add header widget"
```

---

### Task 4.2: Create Controls Card

**Files:**
- Create: `linux_gui/src/widgets/controls.py`

- [ ] **Step 1: Create controls.py**

Create `linux_gui/src/widgets/controls.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/controls.py
git commit -m "feat(linux): add controls card widget"
```

---

### Task 4.3: Create Progress Card

**Files:**
- Create: `linux_gui/src/widgets/progress.py`

- [ ] **Step 1: Create progress.py**

Create `linux_gui/src/widgets/progress.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/progress.py
git commit -m "feat(linux): add progress card widget"
```

---

### Task 4.4: Create Results Table

**Files:**
- Create: `linux_gui/src/widgets/results.py`

- [ ] **Step 1: Create results.py**

Create `linux_gui/src/widgets/results.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/results.py
git commit -m "feat(linux): add results table widget"
```

---

### Task 4.5: Create Summary Card

**Files:**
- Create: `linux_gui/src/widgets/summary.py`

- [ ] **Step 1: Create summary.py with clickable pills**

Create `linux_gui/src/widgets/summary.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/summary.py
git commit -m "feat(linux): add summary card with pills"
```

---

### Task 4.6: Update widgets __init__.py

**Files:**
- Modify: `linux_gui/src/widgets/__init__.py`

- [ ] **Step 1: Export all widgets**

Update `linux_gui/src/widgets/__init__.py`:
```python
"""UI widget components"""
from .background import TechBackground
from .header import HeaderWidget
from .controls import ControlsCard
from .progress import ProgressCard
from .results import ResultsCard
from .summary import SummaryCard

__all__ = [
    "TechBackground",
    "HeaderWidget", 
    "ControlsCard",
    "ProgressCard",
    "ResultsCard",
    "SummaryCard",
]
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/widgets/__init__.py
git commit -m "feat(linux): export all widgets"
```

---

## Chunk 5: Main Application

### Task 5.1: Create Main Window

**Files:**
- Create: `linux_gui/src/app.py`

- [ ] **Step 1: Create app.py with MainWindow**

Create `linux_gui/src/app.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/app.py
git commit -m "feat(linux): add main window"
```

---

### Task 5.2: Create Entry Point

**Files:**
- Create: `linux_gui/src/main.py`

- [ ] **Step 1: Create main.py**

Create `linux_gui/src/main.py`:
```python
#!/usr/bin/env python3
"""Simple Network Scanner - Linux Desktop Application"""
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from pathlib import Path

from .app import MainWindow
from .styles import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Network Host Scanner")
    app.setOrganizationName("RJSears")
    app.setApplicationVersion("1.0.0")
    
    # Set app icon
    assets_dir = Path(__file__).parent.parent / "assets"
    icon_path = assets_dir / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Apply stylesheet
    app.setStyleSheet(STYLESHEET)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/main.py
git commit -m "feat(linux): add application entry point"
```

---

## Chunk 6: Dialogs

### Task 6.1: Create About Dialog

**Files:**
- Create: `linux_gui/src/dialogs/about.py`

- [ ] **Step 1: Create about.py**

Create `linux_gui/src/dialogs/about.py`:
```python
"""About dialog"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

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
        
        version_badge = QLabel("v1.0.0")
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/dialogs/about.py
git commit -m "feat(linux): add about dialog"
```

---

### Task 6.2: Create Filter Dialog

**Files:**
- Create: `linux_gui/src/dialogs/filter.py`

- [ ] **Step 1: Create filter.py**

Create `linux_gui/src/dialogs/filter.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/dialogs/filter.py
git commit -m "feat(linux): add filter dialog"
```

---

### Task 6.3: Create Export Dialog

**Files:**
- Create: `linux_gui/src/dialogs/export.py`

- [ ] **Step 1: Create export.py**

Create `linux_gui/src/dialogs/export.py`:
```python
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
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/dialogs/export.py
git commit -m "feat(linux): add export dialog"
```

---

### Task 6.4: Create Presets Dialog

**Files:**
- Create: `linux_gui/src/dialogs/presets.py`

- [ ] **Step 1: Create presets.py**

Create `linux_gui/src/dialogs/presets.py`:
```python
"""Presets dialog for managing scan configurations"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QLineEdit,
    QInputDialog, QMessageBox
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
        from PySide6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {COLORS['gray_soft']}; max-height: 1px;")
        return line
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/dialogs/presets.py
git commit -m "feat(linux): add presets dialog"
```

---

### Task 6.5: Update dialogs __init__.py

**Files:**
- Modify: `linux_gui/src/dialogs/__init__.py`

- [ ] **Step 1: Export all dialogs**

Update `linux_gui/src/dialogs/__init__.py`:
```python
"""Dialog components"""
from .about import AboutDialog
from .filter import FilterDialog
from .export import ExportDialog
from .presets import PresetsDialog

__all__ = [
    "AboutDialog",
    "FilterDialog",
    "ExportDialog",
    "PresetsDialog",
]
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/dialogs/__init__.py
git commit -m "feat(linux): export all dialogs"
```

---

## Chunk 7: Export & Presets Logic

### Task 7.1: Create Export Module

**Files:**
- Create: `linux_gui/src/export.py`

- [ ] **Step 1: Create export.py**

Create `linux_gui/src/export.py`:
```python
"""Export functionality for scan results"""
import csv
import json
from typing import List

from .models import HostResult


def export_to_csv(results: List[HostResult], file_path: str):
    """Export results to CSV file."""
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IP Address", "Status", "Hostname"])
        for result in sorted(results):
            writer.writerow([result.ip, result.status.value, result.hostname])


def export_to_json(results: List[HostResult], file_path: str):
    """Export results to JSON file."""
    data = {
        "scan_results": [
            {
                "ip": result.ip,
                "status": result.status.value,
                "hostname": result.hostname
            }
            for result in sorted(results)
        ],
        "summary": {
            "total": len(results),
            "up": sum(1 for r in results if r.status.value == "UP"),
            "down": sum(1 for r in results if r.status.value == "DOWN"),
            "network": sum(1 for r in results if r.status.value == "NTWRK"),
            "broadcast": sum(1 for r in results if r.status.value == "BCAST"),
        }
    }
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/export.py
git commit -m "feat(linux): add CSV/JSON export"
```

---

### Task 7.2: Create Presets Module

**Files:**
- Create: `linux_gui/src/presets.py`

- [ ] **Step 1: Create presets.py**

Create `linux_gui/src/presets.py`:
```python
"""Preset management for scan configurations"""
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Preset:
    name: str
    start_ip: str
    host_count: str
    cidr: str


class PresetManager:
    """Manages saved scan presets."""
    
    def __init__(self):
        self._config_dir = Path.home() / ".config" / "network-scanner"
        self._presets_file = self._config_dir / "presets.json"
        self._presets: dict[str, Preset] = {}
        self._load()
    
    def _load(self):
        """Load presets from disk."""
        if not self._presets_file.exists():
            return
        
        try:
            with open(self._presets_file) as f:
                data = json.load(f)
            
            self._presets = {}
            for name, values in data.items():
                self._presets[name] = Preset(
                    name=name,
                    start_ip=values.get("start_ip", ""),
                    host_count=values.get("host_count", ""),
                    cidr=values.get("cidr", "")
                )
        except Exception:
            self._presets = {}
    
    def _save_to_disk(self):
        """Save presets to disk."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for name, preset in self._presets.items():
            data[name] = {
                "start_ip": preset.start_ip,
                "host_count": preset.host_count,
                "cidr": preset.cidr
            }
        
        with open(self._presets_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_all(self) -> List[Preset]:
        """Get all presets."""
        return list(self._presets.values())
    
    def get(self, name: str) -> Optional[Preset]:
        """Get a preset by name."""
        return self._presets.get(name)
    
    def save(self, preset: Preset):
        """Save or update a preset."""
        self._presets[preset.name] = preset
        self._save_to_disk()
    
    def delete(self, name: str):
        """Delete a preset by name."""
        if name in self._presets:
            del self._presets[name]
            self._save_to_disk()
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/src/presets.py
git commit -m "feat(linux): add preset management"
```

---

## Chunk 8: Assets & Packaging

### Task 8.1: Copy Assets

**Files:**
- Create: `linux_gui/assets/map_background.png` (copy from macos_gui)
- Create: `linux_gui/assets/app_icon.png`

- [ ] **Step 1: Copy background image**

```bash
cp macos_gui/assets/map_background.png linux_gui/assets/
```

- [ ] **Step 2: Copy/create app icon**

```bash
cp macos_gui/assets/AppIcon.png linux_gui/assets/app_icon.png
```

- [ ] **Step 3: Commit**

```bash
git add linux_gui/assets/
git commit -m "feat(linux): add app assets"
```

---

### Task 8.2: Create Desktop Entry

**Files:**
- Create: `linux_gui/packaging/debian/network-scanner.desktop`
- Create: `linux_gui/packaging/appimage/network-scanner.desktop`

- [ ] **Step 1: Create desktop entry files**

Create `linux_gui/packaging/debian/network-scanner.desktop`:
```ini
[Desktop Entry]
Name=Network Scanner
Comment=Simple Network Host Scanner
Exec=/opt/network-scanner/run.sh
Icon=/opt/network-scanner/assets/app_icon.png
Terminal=false
Type=Application
Categories=Network;Utility;
Keywords=network;scanner;ping;host;
```

Create `linux_gui/packaging/appimage/network-scanner.desktop`:
```ini
[Desktop Entry]
Name=Network Scanner
Comment=Simple Network Host Scanner
Exec=network-scanner
Icon=network-scanner
Terminal=false
Type=Application
Categories=Network;Utility;
Keywords=network;scanner;ping;host;
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/packaging/
git commit -m "feat(linux): add desktop entry files"
```

---

### Task 8.3: Create Build Scripts

**Files:**
- Create: `linux_gui/build_deb.sh`
- Create: `linux_gui/build_appimage.sh`
- Create: `linux_gui/run.sh`

- [ ] **Step 1: Create run.sh launcher**

Create `linux_gui/run.sh`:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
python3 -m src.main
```

- [ ] **Step 2: Create build_deb.sh**

Create `linux_gui/build_deb.sh`:
```bash
#!/bin/bash
set -e

VERSION="1.0.0"
PKG_NAME="network-scanner"
BUILD_DIR="build/deb"
INSTALL_DIR="$BUILD_DIR/$PKG_NAME/opt/network-scanner"

echo "Building .deb package..."

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BUILD_DIR/$PKG_NAME/DEBIAN"
mkdir -p "$BUILD_DIR/$PKG_NAME/usr/share/applications"

# Copy application files
cp -r src "$INSTALL_DIR/"
cp -r assets "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp run.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/run.sh"

# Copy desktop entry
cp packaging/debian/network-scanner.desktop "$BUILD_DIR/$PKG_NAME/usr/share/applications/"

# Create control file
cat > "$BUILD_DIR/$PKG_NAME/DEBIAN/control" << EOF
Package: network-scanner
Version: $VERSION
Section: net
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-pyside6
Maintainer: Richard J. Sears <richardjsears@protonmail.com>
Description: Simple Network Host Scanner
 A desktop application for scanning network hosts,
 identifying live systems, and performing reverse DNS lookups.
EOF

# Create postinst script
cat > "$BUILD_DIR/$PKG_NAME/DEBIAN/postinst" << 'EOF'
#!/bin/bash
chmod +x /opt/network-scanner/run.sh
EOF
chmod 755 "$BUILD_DIR/$PKG_NAME/DEBIAN/postinst"

# Build package
dpkg-deb --build "$BUILD_DIR/$PKG_NAME"
mv "$BUILD_DIR/$PKG_NAME.deb" "build/network-scanner_${VERSION}_all.deb"

echo "Package built: build/network-scanner_${VERSION}_all.deb"
```

- [ ] **Step 3: Create build_appimage.sh**

Create `linux_gui/build_appimage.sh`:
```bash
#!/bin/bash
set -e

VERSION="1.0.0"
BUILD_DIR="build/appimage"
APP_DIR="$BUILD_DIR/NetworkScanner.AppDir"

echo "Building AppImage..."

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy application files
cp -r src "$APP_DIR/usr/bin/"
cp -r assets "$APP_DIR/usr/bin/"
cp requirements.txt "$APP_DIR/usr/bin/"

# Copy desktop entry and icon
cp packaging/appimage/network-scanner.desktop "$APP_DIR/"
cp packaging/appimage/network-scanner.desktop "$APP_DIR/usr/share/applications/"
cp assets/app_icon.png "$APP_DIR/network-scanner.png"
cp assets/app_icon.png "$APP_DIR/usr/share/icons/hicolor/256x256/apps/network-scanner.png"

# Create AppRun
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:$PATH"
cd "${HERE}/usr/bin"
exec python3 -m src.main "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Download appimagetool if needed
if [ ! -f "build/appimagetool" ]; then
    echo "Downloading appimagetool..."
    curl -Lo build/appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x build/appimagetool
fi

# Build AppImage
ARCH=x86_64 ./build/appimagetool "$APP_DIR" "build/NetworkScanner-${VERSION}-x86_64.AppImage"

echo "AppImage built: build/NetworkScanner-${VERSION}-x86_64.AppImage"
```

- [ ] **Step 4: Make scripts executable and commit**

```bash
chmod +x linux_gui/run.sh linux_gui/build_deb.sh linux_gui/build_appimage.sh
git add linux_gui/run.sh linux_gui/build_deb.sh linux_gui/build_appimage.sh
git commit -m "feat(linux): add build scripts"
```

---

### Task 8.4: Create README

**Files:**
- Create: `linux_gui/README.md`

- [ ] **Step 1: Create README.md**

Create `linux_gui/README.md`:
```markdown
# Simple Network Scanner - Linux Desktop

A PySide6 desktop application for Ubuntu 25 (and other Linux distributions).

## Requirements

- Python 3.10+
- PySide6

## Installation

### From Source

```bash
cd linux_gui
pip install -r requirements.txt
python -m src.main
```

### From .deb Package (Ubuntu/Debian)

```bash
sudo dpkg -i network-scanner_1.0.0_all.deb
```

### From AppImage

```bash
chmod +x NetworkScanner-1.0.0-x86_64.AppImage
./NetworkScanner-1.0.0-x86_64.AppImage
```

## Building Packages

### Build .deb Package

```bash
./build_deb.sh
# Output: build/network-scanner_1.0.0_all.deb
```

### Build AppImage

```bash
./build_appimage.sh
# Output: build/NetworkScanner-1.0.0-x86_64.AppImage
```

## Features

- Network host scanning with parallel ping
- Reverse DNS hostname lookup
- Real-time progress display
- Results filtering by status
- Export to CSV/JSON
- Save/load scan presets

## License

MIT License - see LICENSE file in repository root.
```

- [ ] **Step 2: Commit**

```bash
git add linux_gui/README.md
git commit -m "docs(linux): add README"
```

---

## Final: Test Run

### Task 9.1: Test Application Launch

- [ ] **Step 1: Install dependencies**

```bash
cd linux_gui
pip install -r requirements.txt
```

- [ ] **Step 2: Run the application**

```bash
python -m src.main
```

Expected: Application window opens with teal-themed UI, all widgets visible.

- [ ] **Step 3: Test a scan**

Enter test values:
- Start IP: 127.0.0.1
- Hosts: 1
- CIDR: 32

Click "Start Scan". Expected: Progress bar animates, result appears showing localhost.

- [ ] **Step 4: Test export**

File > Export Results > Select CSV > Save. Expected: CSV file created with scan results.

- [ ] **Step 5: Test presets**

Click "Presets" > Enter name "test" > Click Save. Expected: Preset appears in list.

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-21-linux-desktop-gui.md`. Ready to execute?**
