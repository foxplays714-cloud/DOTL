"""
Graphics view for canvas display and interaction
"""

from typing import Optional
from PyQt6.QtWidgets import QGraphicsView, QWidget
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QMouseEvent, QWheelEvent, QKeyEvent


class GraphicsView(QGraphicsView):
    """Custom graphics view for canvas with zoom, pan, and rotation support"""

    # Signals
    zoom_changed = pyqtSignal(float)  # Emitted when zoom level changes
    canvas_clicked = pyqtSignal(QPointF, QMouseEvent)  # Canvas click with position
    canvas_dragged = pyqtSignal(QPointF, QMouseEvent)  # Canvas drag with position
    tool_cursor_changed = pyqtSignal(str)  # Emitted when tool cursor changes

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the graphics view

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initial zoom and view settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.01  # 1%
        self.max_zoom = 32.0  # 3200%

        # Pan settings
        self.panning = False
        self.pan_start = QPointF()
        self.last_pan_point = QPointF()

        # Interaction settings
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # View modes
        self.view_mode = "fit"  # Can be "fit", "actual", "custom"
        self.current_tool = "cursor"

        # Performance settings
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

    def set_scene(self, scene):
        """Set the scene for this view

        Args:
            scene: The scene to display
        """
        self.setScene(scene)

        # Connect scene signals
        if hasattr(scene, 'canvas_clicked'):
            scene.canvas_clicked.connect(self._on_canvas_clicked)

        # Fit to window initially
        self.fit_to_window()

    def zoom_in(self, factor: float = 1.2):
        """Zoom in by the given factor

        Args:
            factor: Zoom factor (default 1.2 = 20% zoom in)
        """
        new_zoom = self.zoom_factor * factor
        if new_zoom <= self.max_zoom:
            self.set_zoom(new_zoom)

    def zoom_out(self, factor: float = 1.2):
        """Zoom out by the given factor

        Args:
            factor: Zoom factor (default 1.2 = 20% zoom out)
        """
        new_zoom = self.zoom_factor / factor
        if new_zoom >= self.min_zoom:
            self.set_zoom(new_zoom)

    def set_zoom(self, zoom_level: float):
        """Set the zoom level

        Args:
            zoom_level: Zoom level (1.0 = 100%)
        """
        # Clamp zoom to valid range
        zoom_level = max(self.min_zoom, min(self.max_zoom, zoom_level))

        if zoom_level != self.zoom_factor:
            self.zoom_factor = zoom_level

            # Reset the view transform
            self.resetTransform()

            # Apply zoom
            self.scale(zoom_level, zoom_level)

            # Update view mode
            if abs(zoom_level - 1.0) < 0.01:
                self.view_mode = "actual"
            else:
                self.view_mode = "custom"

            # Emit zoom changed signal
            self.zoom_changed.emit(zoom_level)

    def fit_to_window(self):
        """Fit the entire scene within the viewport"""
        if not self.scene():
            return

        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom_factor = self.transform().m11()  # Get current scale factor
        self.view_mode = "fit"
        self.zoom_changed.emit(self.zoom_factor)

    def actual_size(self):
        """Set view to actual pixel size (100% zoom)"""
        self.set_zoom(1.0)
        self.view_mode = "actual"

    def reset_view(self):
        """Reset view to fit to window"""
        self.fit_to_window()

    def set_tool(self, tool_name: str):
        """Set the current tool

        Args:
            tool_name: Name of the tool to activate
        """
        self.current_tool = tool_name
        self._update_cursor()

    def _update_cursor(self):
        """Update the cursor based on the current tool"""
        cursor_map = {
            "brush": Qt.CursorShape.CrossCursor,
            "eraser": Qt.CursorShape.CrossCursor,
            "eyedropper": Qt.CursorShape.CrossCursor,
            "move": Qt.CursorShape.SizeAllCursor,
            "hand": Qt.CursorShape.OpenHandCursor,
            "zoom": Qt.CursorShape.CrossCursor,
            "text": Qt.CursorShape.IBeamCursor,
            "selection": Qt.CursorShape.CrossCursor,
            "crop": Qt.CursorShape.CrossCursor,
        }

        cursor = cursor_map.get(self.current_tool, Qt.CursorShape.ArrowCursor)
        self.setCursor(cursor)

        self.tool_cursor_changed.emit(self.current_tool)

    def _on_canvas_clicked(self, pos: QPointF):
        """Handle canvas click from scene

        Args:
            pos: Position where canvas was clicked
        """
        # Convert to view coordinates if needed
        # Emit signal for tools to handle
        pass

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming

        Args:
            event: Wheel event
        """
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            angle_delta = event.angleDelta().y()
            if angle_delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and
            event.modifiers() & Qt.KeyboardModifier.AltModifier
        ):
            # Start panning
            self.panning = True
            self.pan_start = event.position()
            self.last_pan_point = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # Handle tool-specific mouse events
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.canvas_clicked.emit(scene_pos, event)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events

        Args:
            event: Mouse event
        """
        if self.panning:
            # Pan the view
            delta = event.position() - self.last_pan_point
            self.last_pan_point = event.position()

            # Translate the view
            self.translate(delta.x(), delta.y())
            event.accept()
            return

        # Handle tool-specific mouse move
        if event.buttons() & Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.canvas_dragged.emit(scene_pos, event)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and
            self.panning
        ):
            # End panning
            self.panning = False
            self._update_cursor()  # Restore tool cursor
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events

        Args:
            event: Key event
        """
        # Keyboard shortcuts
        if event.key() == Qt.Key.Key_Space:
            # Temporarily switch to hand tool for panning
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                self.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_0:
                self.fit_to_window()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_1:
                self.actual_size()
                event.accept()
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release events

        Args:
            event: Key event
        """
        if event.key() == Qt.Key.Key_Space:
            # Restore tool cursor
            self._update_cursor()

        super().keyReleaseEvent(event)

    def resizeEvent(self, event):
        """Handle view resize events

        Args:
            event: Resize event
        """
        # Maintain view mode on resize
        if self.view_mode == "fit" and self.scene():
            self.fit_to_window()

        super().resizeEvent(event)