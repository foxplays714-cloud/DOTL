"""
Layer stack management for Paint+ layer system
"""

from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from .base_layer import BaseLayer
from .raster_layer import RasterLayer


class LayerStack(QObject):
    """Manages the stack of layers in a document"""

    # Signals
    layer_added = pyqtSignal(int, BaseLayer)  # Index and layer
    layer_removed = pyqtSignal(int)  # Index
    layer_moved = pyqtSignal(int, int)  # Old index, new index
    active_layer_changed = pyqtSignal(int, BaseLayer)  # Index and layer
    stack_changed = pyqtSignal()  # Emitted when any layer changes

    def __init__(self):
        """Initialize layer stack"""
        super().__init__()

        self.layers: List[BaseLayer] = []
        self.active_layer_index = -1
        self.width = 1920
        self.height = 1080

    def add_layer(self, layer: BaseLayer, index: Optional[int] = None) -> int:
        """Add a layer to the stack

        Args:
            layer: Layer to add
            index: Position to insert at (None for top)

        Returns:
            Index where layer was added
        """
        if index is None:
            index = len(self.layers)

        self.layers.insert(index, layer)

        # Connect layer signals
        layer.layer_changed.connect(self._on_layer_changed)
        layer.properties_changed.connect(self._on_layer_properties_changed)

        # Update active layer if needed
        if self.active_layer_index == -1:
            self.set_active_layer(index)

        self.layer_added.emit(index, layer)
        self.stack_changed.emit()

        return index

    def remove_layer(self, index: int) -> Optional[BaseLayer]:
        """Remove a layer from the stack

        Args:
            index: Index of layer to remove

        Returns:
            Removed layer or None if index invalid
        """
        if index < 0 or index >= len(self.layers):
            return None

        layer = self.layers.pop(index)

        # Disconnect layer signals
        try:
            layer.layer_changed.disconnect(self._on_layer_changed)
            layer.properties_changed.disconnect(self._on_layer_properties_changed)
        except:
            pass  # Already disconnected

        # Update active layer
        if self.active_layer_index == index:
            if len(self.layers) > 0:
                self.active_layer_index = min(index, len(self.layers) - 1)
                self.active_layer_changed.emit(self.active_layer_index,
                                             self.layers[self.active_layer_index])
            else:
                self.active_layer_index = -1
        elif self.active_layer_index > index:
            self.active_layer_index -= 1

        self.layer_removed.emit(index)
        self.stack_changed.emit()

        return layer

    def move_layer(self, from_index: int, to_index: int) -> bool:
        """Move a layer to a new position

        Args:
            from_index: Current index of layer
            to_index: New index for layer

        Returns:
            True if move was successful
        """
        if (from_index < 0 or from_index >= len(self.layers) or
            to_index < 0 or to_index >= len(self.layers)):
            return False

        if from_index == to_index:
            return True

        layer = self.layers.pop(from_index)
        self.layers.insert(to_index, layer)

        # Update active layer index
        if self.active_layer_index == from_index:
            self.active_layer_index = to_index
        elif from_index < self.active_layer_index <= to_index:
            self.active_layer_index -= 1
        elif to_index <= self.active_layer_index < from_index:
            self.active_layer_index += 1

        self.layer_moved.emit(from_index, to_index)
        self.stack_changed.emit()

        return True

    def get_layer(self, index: int) -> Optional[BaseLayer]:
        """Get a layer by index

        Args:
            index: Layer index

        Returns:
            Layer or None if index invalid
        """
        if index < 0 or index >= len(self.layers):
            return None
        return self.layers[index]

    def get_layer_count(self) -> int:
        """Get the number of layers

        Returns:
            Number of layers in the stack
        """
        return len(self.layers)

    def get_layers(self) -> List[BaseLayer]:
        """Get all layers in the stack

        Returns:
            List of all layers (bottom to top)
        """
        return self.layers.copy()

    def get_active_layer(self) -> Optional[BaseLayer]:
        """Get the currently active layer

        Returns:
            Active layer or None if no active layer
        """
        if self.active_layer_index >= 0 and self.active_layer_index < len(self.layers):
            return self.layers[self.active_layer_index]
        return None

    def get_active_layer_index(self) -> int:
        """Get the index of the active layer

        Returns:
            Index of active layer, -1 if no active layer
        """
        return self.active_layer_index

    def set_active_layer(self, index: int) -> bool:
        """Set the active layer

        Args:
            index: Index of layer to make active

        Returns:
            True if successful
        """
        if index < 0 or index >= len(self.layers):
            return False

        if index != self.active_layer_index:
            self.active_layer_index = index
            self.active_layer_changed.emit(index, self.layers[index])

        return True

    def add_new_raster_layer(self, name: str = None) -> int:
        """Add a new raster layer

        Args:
            name: Layer name (auto-generated if None)

        Returns:
            Index of new layer
        """
        if name is None:
            layer_num = len(self.layers) + 1
            name = f"Layer {layer_num}"

        layer = RasterLayer(name, self.width, self.height)
        return self.add_layer(layer)

    def add_background_layer(self, width: int, height: int) -> int:
        """Add a background layer (white, locked)

        Args:
            width: Canvas width
            height: Canvas height

        Returns:
            Index of background layer
        """
        self.width = width
        self.height = height

        background = RasterLayer("Background", width, height, (255, 255, 255, 255))
        background.set_locked(True)
        return self.add_layer(background, 0)  # Add at bottom

    def duplicate_layer(self, index: int) -> Optional[int]:
        """Duplicate a layer

        Args:
            index: Index of layer to duplicate

        Returns:
            Index of duplicated layer or None if failed
        """
        layer = self.get_layer(index)
        if not layer:
            return None

        duplicate = layer.duplicate()
        return self.add_layer(duplicate, index + 1)

    def merge_down(self) -> bool:
        """Merge the active layer with the one below it

        Returns:
            True if merge was successful
        """
        if self.active_layer_index <= 0:
            return False  # No layer below to merge with

        active_layer = self.get_layer(self.active_layer_index)
        below_layer = self.get_layer(self.active_layer_index - 1)

        if not active_layer or not below_layer:
            return False

        # Simple merge: combine the image data
        # In a full implementation, this would handle blend modes, opacity, etc.
        try:
            active_data = active_layer.get_image_data()
            below_data = below_layer.get_image_data()

            # Simple alpha compositing
            merged_data = self._composite_images(below_data, active_data)
            below_layer.set_image_data(merged_data)

            # Remove the active layer
            self.remove_layer(self.active_layer_index)

            return True
        except Exception:
            return False

    def flatten(self) -> bool:
        """Flatten all visible layers into a single layer

        Returns:
            True if flatten was successful
        """
        if len(self.layers) <= 1:
            return True

        # Get all visible layers from bottom to top
        visible_layers = [layer for layer in self.layers if layer.is_visible()]

        if not visible_layers:
            return False

        # Start with the bottom layer
        merged_data = visible_layers[0].get_image_data()

        # Composite remaining layers
        for layer in visible_layers[1:]:
            layer_data = layer.get_image_data()
            merged_data = self._composite_images(merged_data, layer_data)

        # Create a new flattened layer
        flattened = RasterLayer("Flattened", self.width, self.height)
        flattened.set_image_data(merged_data)

        # Clear all layers and add flattened layer
        self.layers.clear()
        self.active_layer_index = -1
        self.add_layer(flattened)

        return True

    def _composite_images(self, bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
        """Composite two image arrays

        Args:
            bottom: Bottom image data
            top: Top image data

        Returns:
            Composited image data
        """
        # Simple alpha compositing
        # In a full implementation, this would handle different blend modes
        if bottom.shape != top.shape:
            # Resize top image to match bottom if needed
            from scipy.ndimage import zoom
            scale_y = bottom.shape[0] / top.shape[0]
            scale_x = bottom.shape[1] / top.shape[1]
            top = zoom(top, (scale_y, scale_x, 1), order=1)
            top = top.astype(np.uint8)

        # Alpha compositing formula
        alpha_top = top[:, :, 3:4].astype(np.float32) / 255.0
        alpha_bottom = bottom[:, :, 3:4].astype(np.float32) / 255.0

        alpha_out = alpha_top + alpha_bottom * (1 - alpha_top)
        color_out = (top[:, :, :3].astype(np.float32) * alpha_top +
                    bottom[:, :, :3].astype(np.float32) * alpha_bottom * (1 - alpha_top))

        # Handle division by zero
        mask = alpha_out > 0
        color_out[mask] /= alpha_out[mask]

        # Combine with alpha
        result = np.zeros_like(bottom)
        result[:, :, :3] = color_out.astype(np.uint8)
        result[:, :, 3] = (alpha_out * 255).astype(np.uint8)

        return result

    def _on_layer_changed(self):
        """Handle layer content changes"""
        self.stack_changed.emit()

    def _on_layer_properties_changed(self):
        """Handle layer property changes"""
        self.stack_changed.emit()

    def clear_all(self):
        """Clear all layers from the stack"""
        for layer in self.layers:
            try:
                layer.layer_changed.disconnect(self._on_layer_changed)
                layer.properties_changed.disconnect(self._on_layer_properties_changed)
            except:
                pass

        self.layers.clear()
        self.active_layer_index = -1
        self.stack_changed.emit()

    def to_dict(self) -> Dict[str, Any]:
        """Convert layer stack to dictionary

        Returns:
            Dictionary containing layer stack data
        """
        return {
            "layers": [layer.to_dict() for layer in self.layers],
            "active_layer_index": self.active_layer_index,
            "width": self.width,
            "height": self.height
        }

    def from_dict(self, data: Dict[str, Any]):
        """Load layer stack from dictionary

        Args:
            data: Dictionary containing layer stack data
        """
        self.clear_all()

        self.width = data.get("width", 1920)
        self.height = data.get("height", 1080)

        for layer_data in data.get("layers", []):
            layer_type = layer_data.get("layer_type", "raster")

            if layer_type == "raster":
                layer = RasterLayer()
                layer.from_dict(layer_data)
                self.add_layer(layer)

        # Set active layer
        active_index = data.get("active_layer_index", -1)
        if 0 <= active_index < len(self.layers):
            self.set_active_layer(active_index)