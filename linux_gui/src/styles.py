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
