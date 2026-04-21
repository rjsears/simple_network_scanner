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
