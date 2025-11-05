"""
Brush and painting tools for Paint+
"""

import math
from typing import Optional
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPen, QBrush, QCursor, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QSpinBox

from .base_tool import BaseTool
from ..layers.base_layer import BaseLayer


class BrushTool(BaseTool):
    """Basic brush tool for painting"""

    def __init__(self):
        super().__init__("Brush")
        self.description = "Paint smooth brush strokes"
        self.category = "painting"

        # Brush-specific settings
        self.smoothing = 0.5  # 0.0 to 1.0
        self.spacing = 0.1  # 0.0 to 1.0 (as fraction of brush size)
        self.pressure = 1.0  # Simulated tablet pressure

        # Brush stroke state
        self.last_draw_pos = None
        self.stroke_points = []

        # Override base class defaults
        self.has_hardness = True
        self.has_flow = True
        self.has_color = True

        # Create cursor
        self._update_cursor()

    def create_options_widget(self) -> QWidget:
        """Create the options widget for brush tool"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Size control
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 500)
        self.size_slider.setValue(self.size)
        self.size_slider.valueChanged.connect(self.set_size)
        size_layout.addWidget(self.size_slider)
        self.size_label = QLabel(str(self.size))
        size_layout.addWidget(self.size_label)
        layout.addLayout(size_layout)

        # Opacity control
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.opacity * 100))
        self.opacity_slider.valueChanged.connect(
            lambda v: self.set_opacity(v / 100.0)
        )
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel(f"{int(self.opacity * 100)}%")
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)

        # Hardness control
        hardness_layout = QHBoxLayout()
        hardness_layout.addWidget(QLabel("Hardness:"))
        self.hardness_slider = QSlider(Qt.Orientation.Horizontal)
        self.hardness_slider.setRange(0, 100)
        self.hardness_slider.setValue(int(self.hardness * 100))
        self.hardness_slider.valueChanged.connect(
            lambda v: self.set_hardness(v / 100.0)
        )
        hardness_layout.addWidget(self.hardness_slider)
        self.hardness_label = QLabel(f"{int(self.hardness * 100)}%")
        hardness_layout.addWidget(self.hardness_label)
        layout.addLayout(hardness_layout)

        # Flow control
        flow_layout = QHBoxLayout()
        flow_layout.addWidget(QLabel("Flow:"))
        self.flow_slider = QSlider(Qt.Orientation.Horizontal)
        self.flow_slider.setRange(1, 100)
        self.flow_slider.setValue(int(self.flow * 100))
        self.flow_slider.valueChanged.connect(
            lambda v: self.set_flow(v / 100.0)
        )
        flow_layout.addWidget(self.flow_slider)
        self.flow_label = QLabel(f"{int(self.flow * 100)}%")
        flow_layout.addWidget(self.flow_label)
        layout.addLayout(flow_layout)

        # Spacing control
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Spacing:"))
        self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.spacing_slider.setRange(1, 100)
        self.spacing_slider.setValue(int(self.spacing * 100))
        self.spacing_slider.valueChanged.connect(
            lambda v: setattr(self, 'spacing', v / 100.0)
        )
        spacing_layout.addWidget(self.spacing_slider)
        self.spacing_label = QLabel(f"{int(self.spacing * 100)}%")
        spacing_layout.addWidget(self.spacing_label)
        layout.addLayout(spacing_layout)

        # Connect label updates
        self.size_slider.valueChanged.connect(
            lambda v: self.size_label.setText(str(v))
        )
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        self.hardness_slider.valueChanged.connect(
            lambda v: self.hardness_label.setText(f"{v}%")
        )
        self.flow_slider.valueChanged.connect(
            lambda v: self.flow_label.setText(f"{v}%")
        )
        self.spacing_slider.valueChanged.connect(
            lambda v: self.spacing_label.setText(f"{v}%")
        )

        layout.addStretch()
        return widget

    def mouse_press(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse press event"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._start_operation()
        self.start_point = canvas_pos
        self.current_point = canvas_pos
        self.last_point = canvas_pos
        self.last_draw_pos = canvas_pos
        self.stroke_points = [canvas_pos]

        # Draw initial point
        self._draw_brush_point(canvas_pos, layer)

    def mouse_move(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse move event"""
        if not self.in_operation:
            return

        self.current_point = canvas_pos
        self.stroke_points.append(canvas_pos)

        # Draw brush stroke from last point to current point
        self._draw_brush_stroke(self.last_point, canvas_pos, layer)

        self.last_point = canvas_pos
        self.last_draw_pos = canvas_pos

    def mouse_release(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse release event"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.current_point = canvas_pos
        self._finish_operation()

    def key_press(self, event):
        """Handle key press event"""
        # Handle tool-specific shortcuts
        if event.key() == Qt.Key.Key_BracketRight:
            self.set_size(min(self.size + 5, 500))
        elif event.key() == Qt.Key.Key_BracketLeft:
            self.set_size(max(self.size - 5, 1))

    def _draw_brush_point(self, pos: QPointF, layer: BaseLayer):
        """Draw a single brush point

        Args:
            pos: Position to draw at
            layer: Target layer
        """
        layer_pos = self.canvas_to_layer_coords(pos, layer)
        x, y = int(layer_pos.x()), int(layer_pos.y())

        if not self.is_valid_layer_position(x, y, layer):
            return

        # Get brush stamp (circular brush with hardness falloff)
        brush_data = self._create_brush_stamp()

        # Apply brush to layer
        self._apply_brush_stamp(brush_data, x, y, layer)

    def _draw_brush_stroke(self, start_pos: QPointF, end_pos: QPointF, layer: BaseLayer):
        """Draw a brush stroke between two points

        Args:
            start_pos: Starting position
            end_pos: Ending position
            layer: Target layer
        """
        # Calculate distance and number of intermediate points
        distance = math.sqrt(
            (end_pos.x() - start_pos.x()) ** 2 +
            (end_pos.y() - start_pos.y()) ** 2
        )

        if distance < 1:
            self._draw_brush_point(end_pos, layer)
            return

        # Calculate spacing between brush stamps
        spacing_pixels = self.size * self.spacing
        num_points = max(2, int(distance / spacing_pixels))

        # Draw brush stamps along the line
        for i in range(num_points + 1):
            t = i / num_points
            x = start_pos.x() + t * (end_pos.x() - start_pos.x())
            y = start_pos.y() + t * (end_pos.y() - start_pos.y())
            pos = QPointF(x, y)
            self._draw_brush_point(pos, layer)

    def _create_brush_stamp(self) -> np.ndarray:
        """Create a brush stamp with current settings

        Returns:
            2D numpy array representing brush opacity
        """
        size = self.size * 2  # Make brush larger for smooth edges
        center = size // 2

        # Create coordinate grids
        y, x = np.ogrid[:size, :size]
        distance = np.sqrt((x - center) ** 2 + (y - center) ** 2)

        # Create brush with hardness falloff
        radius = self.size / 2
        if self.hardness >= 1.0:
            # Hard brush
            brush = np.where(distance <= radius, 1.0, 0.0)
        else:
            # Soft brush with falloff
            falloff_start = radius * (1.0 - self.hardness)
            brush = np.zeros_like(distance)

            # Inner area (full opacity)
            inner_mask = distance <= falloff_start
            brush[inner_mask] = 1.0

            # Falloff area (gradient)
            falloff_mask = (distance > falloff_start) & (distance <= radius)
            if np.any(falloff_mask):
                falloff_distance = distance[falloff_mask] - falloff_start
                falloff_range = radius - falloff_start
                brush[falloff_mask] = 1.0 - (falloff_distance / falloff_range)

        # Apply flow and pressure
        brush *= self.flow * self.pressure

        return brush

    def _apply_brush_stamp(self, brush_stamp: np.ndarray, x: int, y: int, layer: BaseLayer):
        """Apply a brush stamp to the layer

        Args:
            brush_stamp: 2D array of opacity values
            x, y: Center position on layer
            layer: Target layer
        """
        if layer.is_locked():
            return

        # Get layer image data
        image_data = layer.get_image_data()

        # Calculate stamp bounds
        brush_size = brush_stamp.shape[0]
        half_size = brush_size // 2

        start_x = max(0, x - half_size)
        start_y = max(0, y - half_size)
        end_x = min(image_data.shape[1], x + half_size + 1)
        end_y = min(image_data.shape[0], y + half_size + 1)

        if start_x >= end_x or start_y >= end_y:
            return

        # Extract relevant areas
        layer_area = image_data[start_y:end_y, start_x:end_x]

        # Calculate brush stamp area
        brush_start_x = half_size - (x - start_x)
        brush_start_y = half_size - (y - start_y)
        brush_end_x = brush_start_x + (end_x - start_x)
        brush_end_y = brush_start_y + (end_y - start_y)

        brush_area = brush_stamp[brush_start_y:brush_end_y, brush_start_x:brush_end_x]

        # Apply color with brush stamp
        color_array = np.array(self.color, dtype=np.float32)

        for i in range(layer_area.shape[0]):
            for j in range(layer_area.shape[1]):
                if brush_area[i, j] > 0:
                    # Blend color with existing pixel
                    existing_color = layer_area[i, j].astype(np.float32)
                    brush_opacity = brush_area[i, j] * self.opacity

                    # Alpha compositing
                    new_alpha = existing_color[3] + (255 - existing_color[3]) * brush_opacity * (color_array[3] / 255.0)
                    if new_alpha > 0:
                        new_color = (
                            existing_color[:3] * (existing_color[3] / new_alpha) +
                            color_array[:3] * brush_opacity * (255 - existing_color[3]) / 255.0
                        )
                        layer_area[i, j, :3] = np.clip(new_color, 0, 255).astype(np.uint8)
                        layer_area[i, j, 3] = int(new_alpha)

        # Update layer
        layer.set_image_data(image_data)

    def _update_cursor(self):
        """Update the cursor for brush tool"""
        # Create a circular cursor showing brush size
        cursor_size = max(16, min(64, self.size))

        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw circle
        center = cursor_size // 2
        radius = min(center - 2, self.size // 2)
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)

        # Draw crosshair for larger brushes
        if self.size > 20:
            painter.drawLine(center - 4, center, center + 4, center)
            painter.drawLine(center, center - 4, center, center + 4)

        painter.end()

        self.cursor = QCursor(pixmap)
        if self.active:
            self.cursor_changed.emit(self.cursor)

    def get_tool_info(self) -> dict:
        """Get tool information"""
        info = super().get_tool_info()
        info.update({
            "has_hardness": True,
            "has_flow": True,
            "has_color": True,
            "current_hardness": self.hardness,
            "current_flow": self.flow,
            "current_color": self.color
        })
        return info