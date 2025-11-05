"""
Base tool class for Paint+ tool system
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QPointF, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QCursor
from PyQt6.QtWidgets import QWidget

from ..layers.base_layer import BaseLayer


class BaseTool(QObject, ABC):
    """Abstract base class for all drawing and editing tools"""

    # Signals
    tool_started = pyqtSignal()  # Emitted when tool operation starts
    tool_finished = pyqtSignal()  # Emitted when tool operation finishes
    tool_changed = pyqtSignal()  # Emitted when tool settings change
    cursor_changed = pyqtSignal(QCursor)  # Emitted when cursor changes

    def __init__(self, name: str, icon_path: Optional[str] = None):
        """Initialize base tool

        Args:
            name: Tool name
            icon_path: Path to tool icon (optional)
        """
        super().__init__()

        self.name = name
        self.icon_path = icon_path
        self.description = ""
        self.category = "general"

        # Tool settings
        self.size = 10
        self.opacity = 1.0
        self.hardness = 1.0
        self.flow = 1.0
        self.color = (0, 0, 0, 255)  # Black

        # Tool state
        self.active = False
        self.in_operation = False
        self.start_point = QPointF()
        self.current_point = QPointF()
        self.last_point = QPointF()

        # Cursor
        self.cursor = QCursor()

        # Target layer
        self.target_layer: Optional[BaseLayer] = None

    @abstractmethod
    def create_options_widget(self) -> QWidget:
        """Create the options widget for this tool

        Returns:
            QWidget containing tool-specific options
        """
        pass

    @abstractmethod
    def mouse_press(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse press event

        Args:
            event: Mouse event
            layer: Target layer for tool operation
            canvas_pos: Position on canvas
        """
        pass

    @abstractmethod
    def mouse_move(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse move event

        Args:
            event: Mouse event
            layer: Target layer for tool operation
            canvas_pos: Position on canvas
        """
        pass

    @abstractmethod
    def mouse_release(self, event: QMouseEvent, layer: BaseLayer, canvas_pos: QPointF):
        """Handle mouse release event

        Args:
            event: Mouse event
            layer: Target layer for tool operation
            canvas_pos: Position on canvas
        """
        pass

    @abstractmethod
    def key_press(self, event: QKeyEvent):
        """Handle key press event

        Args:
            event: Key event
        """
        pass

    def activate(self):
        """Called when tool is activated"""
        self.active = True
        self.cursor_changed.emit(self.cursor)

    def deactivate(self):
        """Called when tool is deactivated"""
        self.active = False
        if self.in_operation:
            self._finish_operation()

    def set_target_layer(self, layer: BaseLayer):
        """Set the target layer for tool operations

        Args:
            layer: Target layer
        """
        self.target_layer = layer

    def set_size(self, size: int):
        """Set tool size

        Args:
            size: Tool size in pixels
        """
        if size > 0:
            self.size = size
            self._update_cursor()
            self.tool_changed.emit()

    def set_opacity(self, opacity: float):
        """Set tool opacity

        Args:
            opacity: Opacity value from 0.0 to 1.0
        """
        if 0.0 <= opacity <= 1.0:
            self.opacity = opacity
            self.tool_changed.emit()

    def set_hardness(self, hardness: float):
        """Set tool hardness (for brush-like tools)

        Args:
            hardness: Hardness value from 0.0 (soft) to 1.0 (hard)
        """
        if 0.0 <= hardness <= 1.0:
            self.hardness = hardness
            self.tool_changed.emit()

    def set_flow(self, flow: float):
        """Set tool flow (for brush-like tools)

        Args:
            flow: Flow value from 0.0 to 1.0
        """
        if 0.0 <= flow <= 1.0:
            self.flow = flow
            self.tool_changed.emit()

    def set_color(self, color: tuple):
        """Set tool color

        Args:
            color: Color as (R, G, B, A) tuple
        """
        self.color = color
        self.tool_changed.emit()

    def _start_operation(self):
        """Start a tool operation"""
        if not self.in_operation:
            self.in_operation = True
            self.tool_started.emit()

    def _finish_operation(self):
        """Finish a tool operation"""
        if self.in_operation:
            self.in_operation = False
            self.tool_finished.emit()

    def _update_cursor(self):
        """Update the cursor based on tool settings"""
        # Subclasses should override this to create custom cursors
        pass

    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for UI display

        Returns:
            Dictionary containing tool metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "icon_path": self.icon_path,
            "has_size": True,
            "has_opacity": True,
            "has_hardness": False,
            "has_flow": False,
            "has_color": False,
            "current_size": self.size,
            "current_opacity": self.opacity,
            "current_hardness": self.hardness,
            "current_flow": self.flow,
            "current_color": self.color
        }

    def get_shortcuts(self) -> Dict[str, str]:
        """Get keyboard shortcuts for this tool

        Returns:
            Dictionary of shortcut descriptions
        """
        return {
            "activate": f"Press {self.name[0].upper() if self.name else 'B'} key",
            "increase_size": "]",
            "decrease_size": "[",
            "increase_opacity": "Shift + ]",
            "decrease_opacity": "Shift + ["
        }

    def reset_settings(self):
        """Reset tool settings to defaults"""
        self.size = 10
        self.opacity = 1.0
        self.hardness = 1.0
        self.flow = 1.0
        self.color = (0, 0, 0, 255)
        self.tool_changed.emit()

    def save_settings(self) -> Dict[str, Any]:
        """Save tool settings to dictionary

        Returns:
            Dictionary containing current tool settings
        """
        return {
            "size": self.size,
            "opacity": self.opacity,
            "hardness": self.hardness,
            "flow": self.flow,
            "color": self.color
        }

    def load_settings(self, settings: Dict[str, Any]):
        """Load tool settings from dictionary

        Args:
            settings: Dictionary containing tool settings
        """
        if "size" in settings:
            self.set_size(settings["size"])
        if "opacity" in settings:
            self.set_opacity(settings["opacity"])
        if "hardness" in settings:
            self.set_hardness(settings["hardness"])
        if "flow" in settings:
            self.set_flow(settings["flow"])
        if "color" in settings:
            self.set_color(settings["color"])

    def canvas_to_layer_coords(self, canvas_pos: QPointF, layer: BaseLayer) -> QPointF:
        """Convert canvas coordinates to layer coordinates

        Args:
            canvas_pos: Position on canvas
            layer: Target layer

        Returns:
            Position in layer coordinates
        """
        # Account for layer position and transformation
        layer_pos = QPointF(
            canvas_pos.x() - layer.x,
            canvas_pos.y() - layer.y
        )
        return layer_pos

    def is_valid_layer_position(self, x: int, y: int, layer: BaseLayer) -> bool:
        """Check if coordinates are valid for the given layer

        Args:
            x, y: Coordinates to check
            layer: Target layer

        Returns:
            True if coordinates are within layer bounds
        """
        return (0 <= x < layer.width and 0 <= y < layer.height and
                not layer.is_locked())