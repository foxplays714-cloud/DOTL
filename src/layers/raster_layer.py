"""
Raster layer implementation for Paint+ layer system
"""

from typing import Optional, Tuple
import numpy as np
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QRectF

from .base_layer import BaseLayer


class RasterLayer(BaseLayer):
    """Raster layer containing pixel-based image data"""

    def __init__(self, name: str = "Raster Layer", width: int = 1920, height: int = 1080,
                 background_color: Tuple[int, int, int, int] = (255, 255, 255, 0)):
        """Initialize raster layer

        Args:
            name: Layer name
            width: Layer width in pixels
            height: Layer height in pixels
            background_color: Background color as (R, G, B, A) tuple
        """
        super().__init__(name, width, height)

        self.layer_type = "raster"

        # Initialize image data with transparent background
        self._image_data = np.full(
            (height, width, 4),
            background_color,
            dtype=np.uint8
        )

        # Cached pixmap for performance
        self._cached_pixmap: Optional[QPixmap] = None
        self._pixmap_dirty = True

    def get_image_data(self) -> np.ndarray:
        """Get the image data as numpy array

        Returns:
            Numpy array of shape (height, width, 4) in RGBA format
        """
        return self._image_data.copy()

    def set_image_data(self, data: np.ndarray):
        """Set the image data from numpy array

        Args:
            data: Numpy array of shape (height, width, 4) in RGBA format
        """
        if data.shape[2] != 4:
            raise ValueError("Image data must have 4 channels (RGBA)")

        self._image_data = data.astype(np.uint8)
        self.width = data.shape[1]
        self.height = data.shape[0]
        self.bounds = QRectF(0, 0, self.width, self.height)

        # Invalidate cached pixmap
        self._pixmap_dirty = True
        self.layer_changed.emit()

    def render_to_pixmap(self) -> QPixmap:
        """Render the layer to a QPixmap

        Returns:
            QPixmap containing the rendered layer
        """
        if self._cached_pixmap is None or self._pixmap_dirty:
            self._cached_pixmap = self._create_pixmap()
            self._pixmap_dirty = False

        return self._cached_pixmap

    def _create_pixmap(self) -> QPixmap:
        """Create a QPixmap from the current image data

        Returns:
            QPixmap representing the layer
        """
        # Convert numpy array to QImage
        height, width = self._image_data.shape[:2]
        qimage = QImage(
            self._image_data.data,
            width,
            height,
            width * 4,  # bytes per line
            QImage.Format.Format_RGBA8888
        )

        # Convert to QPixmap
        pixmap = QPixmap.fromImage(qimage)

        # Apply opacity if needed
        if self.opacity < 1.0:
            # Create a new pixmap with applied opacity
            opacity_pixmap = QPixmap(pixmap.size())
            opacity_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(opacity_pixmap)
            painter.setOpacity(self.opacity)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            return opacity_pixmap

        return pixmap

    def fill_color(self, color: Tuple[int, int, int, int]):
        """Fill the entire layer with a solid color

        Args:
            color: Fill color as (R, G, B, A) tuple
        """
        if self.locked:
            return

        self._image_data[:] = color
        self._pixmap_dirty = True
        self.layer_changed.emit()

    def clear(self):
        """Clear the layer (make it fully transparent)"""
        self.fill_color((0, 0, 0, 0))

    def draw_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]):
        """Draw a single pixel

        Args:
            x: X coordinate
            y: Y coordinate
            color: Color as (R, G, B, A) tuple
        """
        if self.locked:
            return

        if 0 <= x < self.width and 0 <= y < self.height:
            self._image_data[y, x] = color
            self._pixmap_dirty = True
            self.layer_changed.emit()

    def draw_line(self, x1: int, y1: int, x2: int, y2: int,
                  color: Tuple[int, int, int, int], width: int = 1):
        """Draw a line between two points

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            color: Line color as (R, G, B, A) tuple
            width: Line width in pixels
        """
        if self.locked:
            return

        # Simple line drawing using Bresenham's algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1

        while True:
            # Draw a pixel (or a small circle for thicker lines)
            if width == 1:
                self.draw_pixel(x, y, color)
            else:
                # Draw a small circle for thicker lines
                radius = width // 2
                for px in range(max(0, x - radius), min(self.width, x + radius + 1)):
                    for py in range(max(0, y - radius), min(self.height, y + radius + 1)):
                        if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                            self.draw_pixel(px, py, color)

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = False):
        """Draw a rectangle

        Args:
            x, y: Top-left corner
            width, height: Rectangle dimensions
            color: Rectangle color as (R, G, B, A) tuple
            filled: If True, fill the rectangle; otherwise draw outline
        """
        if self.locked:
            return

        if filled:
            # Fill the rectangle
            for px in range(max(0, x), min(self.width, x + width)):
                for py in range(max(0, y), min(self.height, y + height)):
                    self.draw_pixel(px, py, color)
        else:
            # Draw outline
            # Top edge
            for px in range(max(0, x), min(self.width, x + width)):
                self.draw_pixel(px, y, color)
            # Bottom edge
            for px in range(max(0, x), min(self.width, x + width)):
                self.draw_pixel(px, y + height - 1, color)
            # Left edge
            for py in range(max(0, y), min(self.height, y + height)):
                self.draw_pixel(x, py, color)
            # Right edge
            for py in range(max(0, y), min(self.height, y + height)):
                self.draw_pixel(x + width - 1, py, color)

    def draw_circle(self, center_x: int, center_y: int, radius: int,
                   color: Tuple[int, int, int, int], filled: bool = False):
        """Draw a circle

        Args:
            center_x, center_y: Center coordinates
            radius: Circle radius
            color: Circle color as (R, G, B, A) tuple
            filled: If True, fill the circle; otherwise draw outline
        """
        if self.locked:
            return

        if filled:
            # Fill the circle
            for y in range(max(0, center_y - radius),
                         min(self.height, center_y + radius + 1)):
                for x in range(max(0, center_x - radius),
                             min(self.width, center_x + radius + 1)):
                    if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                        self.draw_pixel(x, y, color)
        else:
            # Draw outline using midpoint circle algorithm
            x = radius
            y = 0
            decision_over_2 = 1 - x

            while x >= y:
                # Draw 8 symmetric points
                points = [
                    (center_x + x, center_y + y),
                    (center_x + y, center_y + x),
                    (center_x - y, center_y + x),
                    (center_x - x, center_y + y),
                    (center_x - x, center_y - y),
                    (center_x - y, center_y - x),
                    (center_x + y, center_y - x),
                    (center_x + x, center_y - y)
                ]

                for px, py in points:
                    self.draw_pixel(px, py, color)

                y += 1
                if decision_over_2 <= 0:
                    decision_over_2 += 2 * y + 1
                else:
                    decision_over_2 += 2 * (y - x) + 1
                    x -= 1

    def duplicate(self) -> 'RasterLayer':
        """Create a duplicate of this layer

        Returns:
            New RasterLayer with the same properties and content
        """
        new_layer = RasterLayer(f"{self.name} copy", self.width, self.height)
        new_layer._image_data = self._image_data.copy()
        new_layer.visible = self.visible
        new_layer.opacity = self.opacity
        new_layer.blend_mode = self.blend_mode
        new_layer.locked = self.locked
        new_layer.x = self.x
        new_layer.y = self.y
        new_layer.rotation = self.rotation
        new_layer.scale_x = self.scale_x
        new_layer.scale_y = self.scale_y

        return new_layer

    def resize(self, new_width: int, new_height: int,
               maintain_aspect: bool = False) -> None:
        """Resize the layer

        Args:
            new_width: New width in pixels
            new_height: New height in pixels
            maintain_aspect: If True, maintain aspect ratio
        """
        if maintain_aspect:
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = self.width / self.height
            if new_width / new_height > aspect_ratio:
                new_width = int(new_height * aspect_ratio)
            else:
                new_height = int(new_width / aspect_ratio)

        # Resize image data using bilinear interpolation
        from scipy.ndimage import zoom

        scale_x = new_width / self.width
        scale_y = new_height / self.height

        # Resample the image
        resized_data = zoom(self._image_data, (scale_y, scale_x, 1), order=1)
        resized_data = resized_data.astype(np.uint8)

        # Update layer
        self.set_image_data(resized_data)

    def crop(self, x: int, y: int, width: int, height: int) -> None:
        """Crop the layer to the specified rectangle

        Args:
            x, y: Top-left corner of crop area
            width, height: Dimensions of crop area
        """
        if self.locked:
            return

        # Calculate valid crop area
        crop_x = max(0, x)
        crop_y = max(0, y)
        crop_width = min(width, self.width - crop_x)
        crop_height = min(height, self.height - crop_y)

        if crop_width <= 0 or crop_height <= 0:
            return

        # Crop the image data
        cropped_data = self._image_data[
            crop_y:crop_y + crop_height,
            crop_x:crop_x + crop_width
        ]

        # Update layer
        self.set_image_data(cropped_data)
        self.x += crop_x
        self.y += crop_y