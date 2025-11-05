"""
Base layer class for Paint+ layer system
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QRectF
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor


class BaseLayer(QObject, ABC):
    """Abstract base class for all layer types"""

    # Signals
    layer_changed = pyqtSignal()  # Emitted when layer content changes
    properties_changed = pyqtSignal()  # Emitted when layer properties change
    visibility_changed = pyqtSignal(bool)  # Emitted when visibility toggles

    def __init__(self, name: str = "New Layer", width: int = 1920, height: int = 1080):
        """Initialize base layer

        Args:
            name: Layer name
            width: Layer width in pixels
            height: Layer height in pixels
        """
        super().__init__()

        self.name = name
        self.width = width
        self.height = height

        # Layer properties
        self.visible = True
        self.opacity = 1.0  # 0.0 to 1.0
        self.blend_mode = "normal"
        self.locked = False

        # Layer position and transformation
        self.x = 0
        self.y = 0
        self.rotation = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0

        # Layer bounds
        self.bounds = QRectF(0, 0, width, height)

        # Layer type identifier
        self.layer_type = "base"

    @abstractmethod
    def get_image_data(self) -> np.ndarray:
        """Get the image data as numpy array

        Returns:
            Numpy array of shape (height, width, 4) in RGBA format
        """
        pass

    @abstractmethod
    def set_image_data(self, data: np.ndarray):
        """Set the image data from numpy array

        Args:
            data: Numpy array of shape (height, width, 4) in RGBA format
        """
        pass

    @abstractmethod
    def render_to_pixmap(self) -> QPixmap:
        """Render the layer to a QPixmap

        Returns:
            QPixmap containing the rendered layer
        """
        pass

    def get_bounds(self) -> QRectF:
        """Get the layer's bounding rectangle

        Returns:
            QRectF representing the layer bounds
        """
        return self.bounds

    def set_bounds(self, bounds: QRectF):
        """Set the layer's bounding rectangle

        Args:
            bounds: New bounding rectangle
        """
        self.bounds = bounds
        self.layer_changed.emit()

    def set_size(self, width: int, height: int):
        """Set the layer size

        Args:
            width: New width in pixels
            height: New height in pixels
        """
        self.width = width
        self.height = height
        self.bounds = QRectF(0, 0, width, height)
        self.layer_changed.emit()

    def set_position(self, x: int, y: int):
        """Set the layer position

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
        """
        self.x = x
        self.y = y
        self.properties_changed.emit()

    def set_opacity(self, opacity: float):
        """Set the layer opacity

        Args:
            opacity: Opacity value from 0.0 (transparent) to 1.0 (opaque)
        """
        if 0.0 <= opacity <= 1.0:
            self.opacity = opacity
            self.properties_changed.emit()

    def set_blend_mode(self, blend_mode: str):
        """Set the layer blend mode

        Args:
            blend_mode: Blend mode name (e.g., "normal", "multiply", "screen")
        """
        self.blend_mode = blend_mode
        self.properties_changed.emit()

    def set_visibility(self, visible: bool):
        """Set the layer visibility

        Args:
            visible: True if layer is visible, False if hidden
        """
        if self.visible != visible:
            self.visible = visible
            self.visibility_changed.emit(visible)

    def set_locked(self, locked: bool):
        """Set whether the layer is locked

        Args:
            locked: True if layer is locked, False if editable
        """
        self.locked = locked
        self.properties_changed.emit()

    def is_visible(self) -> bool:
        """Check if the layer is visible

        Returns:
            True if layer is visible, False otherwise
        """
        return self.visible

    def is_locked(self) -> bool:
        """Check if the layer is locked

        Returns:
            True if layer is locked, False otherwise
        """
        return self.locked

    def get_pixel_at(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        """Get the color of a pixel at the given coordinates

        Args:
            x: X coordinate relative to layer
            y: Y coordinate relative to layer

        Returns:
            Tuple of (R, G, B, A) values or None if outside layer bounds
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        data = self.get_image_data()
        if y < data.shape[0] and x < data.shape[1]:
            pixel = data[y, x]
            return tuple(pixel.astype(int))

        return None

    def set_pixel_at(self, x: int, y: int, color: Tuple[int, int, int, int]):
        """Set the color of a pixel at the given coordinates

        Args:
            x: X coordinate relative to layer
            y: Y coordinate relative to layer
            color: Tuple of (R, G, B, A) values (0-255)
        """
        if self.locked:
            return

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        data = self.get_image_data()
        if y < data.shape[0] and x < data.shape[1]:
            data[y, x] = color
            self.set_image_data(data)
            self.layer_changed.emit()

    def get_thumbnail(self, size: int = 64) -> QPixmap:
        """Get a thumbnail representation of the layer

        Args:
            size: Thumbnail size in pixels (square)

        Returns:
            QPixmap containing the thumbnail
        """
        # Render full layer and scale down
        full_pixmap = self.render_to_pixmap()
        return full_pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def duplicate(self) -> 'BaseLayer':
        """Create a duplicate of this layer

        Returns:
            New layer with the same properties and content
        """
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement duplicate()")

    def to_dict(self) -> Dict[str, Any]:
        """Convert layer to dictionary representation

        Returns:
            Dictionary containing layer data for serialization
        """
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "visible": self.visible,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode,
            "locked": self.locked,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "layer_type": self.layer_type,
            "image_data": self.get_image_data().tolist()
        }

    def from_dict(self, data: Dict[str, Any]):
        """Load layer data from dictionary

        Args:
            data: Dictionary containing layer data
        """
        self.name = data.get("name", "Layer")
        self.width = data.get("width", 1920)
        self.height = data.get("height", 1080)
        self.visible = data.get("visible", True)
        self.opacity = data.get("opacity", 1.0)
        self.blend_mode = data.get("blend_mode", "normal")
        self.locked = data.get("locked", False)
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        self.rotation = data.get("rotation", 0.0)
        self.scale_x = data.get("scale_x", 1.0)
        self.scale_y = data.get("scale_y", 1.0)

        if "image_data" in data:
            image_array = np.array(data["image_data"], dtype=np.uint8)
            self.set_image_data(image_array)