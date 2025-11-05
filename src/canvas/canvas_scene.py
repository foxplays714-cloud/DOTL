"""
Canvas scene for Paint+ graphics system
"""

from typing import Optional, List, Tuple
import numpy as np
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QTransform


class CanvasScene(QGraphicsScene):
    """Custom graphics scene for canvas management"""

    # Signals
    canvas_clicked = pyqtSignal(QPointF)  # Emitted when canvas is clicked
    canvas_mouse_moved = pyqtSignal(QPointF)  # Emitted when mouse moves on canvas

    def __init__(self, width: int, height: int):
        """Initialize the canvas scene

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        super().__init__()

        self.width = width
        self.height = height
        self.dpi = 72
        self.color_mode = "RGB"

        # Set scene rectangle
        self.setSceneRect(0, 0, width, height)

        # Background configuration
        self.show_transparency = True
        self.transparency_size = 16
        self.transparency_color1 = QColor(255, 255, 255)
        self.transparency_color2 = QColor(204, 204, 204)

        # Canvas background item
        self.background_item = None
        self._create_background()

        # Layer items container
        self.layer_items: List[QGraphicsItem] = []

    def _create_background(self):
        """Create the canvas background"""
        if self.background_item:
            self.removeItem(self.background_item)

        # Create background item based on transparency setting
        if self.show_transparency:
            # Create checkerboard pattern for transparency
            background_brush = self._create_checkerboard_brush()
        else:
            # Solid color background
            bg_color = self.transparency_color1
            background_brush = QBrush(bg_color)

        # Add background rectangle
        self.setBackgroundBrush(background_brush)

    def _create_checkerboard_brush(self) -> QBrush:
        """Create a checkerboard pattern brush for transparency

        Returns:
            QBrush with checkerboard pattern
        """
        # Create a pixmap for the pattern
        size = self.transparency_size * 2
        from PyQt6.QtGui import QPixmap, QPainter

        pixmap = QPixmap(size, size)
        pixmap.fill(self.transparency_color1)

        painter = QPainter(pixmap)
        painter.setBrush(self.transparency_color2)

        # Draw the checkerboard pattern
        painter.drawRect(0, 0, self.transparency_size, self.transparency_size)
        painter.drawRect(self.transparency_size, self.transparency_size,
                        self.transparency_size, self.transparency_size)

        painter.end()

        return QBrush(pixmap)

    def set_size(self, width: int, height: int):
        """Set the canvas size

        Args:
            width: New canvas width
            height: New canvas height
        """
        self.width = width
        self.height = height
        self.setSceneRect(0, 0, width, height)

    def set_transparency_background(self, show: bool):
        """Set whether to show transparency checkerboard

        Args:
            show: True to show transparency pattern, False for solid background
        """
        self.show_transparency = show
        self._create_background()

    def add_layer_item(self, item: QGraphicsItem):
        """Add a layer item to the scene

        Args:
            item: Graphics item representing a layer
        """
        self.addItem(item)
        self.layer_items.append(item)

    def remove_layer_item(self, item: QGraphicsItem):
        """Remove a layer item from the scene

        Args:
            item: Graphics item to remove
        """
        if item in self.layer_items:
            self.layer_items.remove(item)
        self.removeItem(item)

    def clear_layers(self):
        """Clear all layer items from the scene"""
        for item in self.layer_items[:]:  # Copy list to avoid modification during iteration
            self.removeItem(item)
        self.layer_items.clear()

    def get_pixel_at(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        """Get the color of a pixel at the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of (R, G, B, A) values or None if outside canvas
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        # This would need to be implemented based on the active layer
        # For now, return a default color
        return (255, 255, 255, 255)

    def set_pixel_at(self, x: int, y: int, color: Tuple[int, int, int, int]):
        """Set the color of a pixel at the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate
            color: Tuple of (R, G, B, A) values
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        # This would need to be implemented based on the active layer
        pass

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            self.canvas_clicked.emit(pos)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        pos = event.scenePos()
        self.canvas_mouse_moved.emit(pos)

        super().mouseMoveEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Custom background drawing"""
        # Call parent implementation
        super().drawBackground(painter, rect)

        # Draw canvas border if needed
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.PenStyle.SolidLine))
        painter.drawRect(0, 0, self.width, self.height)