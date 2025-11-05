"""
Main application window for Paint+
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QSplitter,
    QDockWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from ..app.application import PaintPlusApplication
from ..canvas.graphics_view import GraphicsView
from ..ui.panels.tool_panel import ToolPanel
from ..ui.panels.layer_panel import LayerPanel
from ..ui.panels.color_panel import ColorPanel
from ..ui.panels.properties_panel import PropertiesPanel


class PaintPlusMainWindow(QMainWindow):
    """Main application window with traditional Photoshop layout"""

    def __init__(self, app: PaintPlusApplication):
        super().__init__()

        self.app = app
        self.central_widget = None
        self.canvas_view = None
        self.tool_panel = None
        self.layer_panel = None
        self.color_panel = None
        self.properties_panel = None

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the main window UI components"""
        self.setWindowTitle("Paint+ - Professional Image Editor")
        self.setGeometry(100, 100, 1400, 900)

        # Setup menu bar
        self._setup_menu_bar()

        # Setup toolbars
        self._setup_toolbars()

        # Setup central widget with canvas
        self._setup_central_widget()

        # Setup dockable panels
        self._setup_panels()

        # Setup status bar
        self._setup_status_bar()

    def _setup_menu_bar(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_document)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.app.open_document)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.app.save_document)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.app.save_document_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.app.exit_application)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        view_menu.addAction(zoom_out_action)

        fit_to_screen_action = QAction("Fit to Screen", self)
        fit_to_screen_action.setShortcut(QKeySequence("Ctrl+0"))
        view_menu.addAction(fit_to_screen_action)

        actual_size_action = QAction("Actual Size", self)
        actual_size_action.setShortcut(QKeySequence("Ctrl+1"))
        view_menu.addAction(actual_size_action)

        # Window menu
        window_menu = menubar.addMenu("&Window")

        # Layer menu
        layer_menu = menubar.addMenu("&Layer")

        new_layer_action = QAction("New &Layer", self)
        new_layer_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        layer_menu.addAction(new_layer_action)

        # Filter menu
        filter_menu = menubar.addMenu("&Filter")

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About Paint+", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbars(self):
        """Setup application toolbars"""
        # Main toolbar (options bar)
        options_toolbar = QToolBar("Options")
        self.addToolBar(options_toolbar)
        options_toolbar.setMovable(False)

        # Add tool options placeholder
        # This will be populated dynamically based on selected tool

        # File toolbar
        file_toolbar = QToolBar("File")
        self.addToolBar(file_toolbar)

        new_action = QAction("New", self)
        new_action.triggered.connect(self._new_document)
        file_toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.app.open_document)
        file_toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.app.save_document)
        file_toolbar.addAction(save_action)

    def _setup_central_widget(self):
        """Setup the central widget with canvas"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create canvas view
        self.canvas_view = GraphicsView()
        self.canvas_view.setMinimumSize(400, 300)

        # Add canvas to central widget
        main_layout.addWidget(self.canvas_view)

    def _setup_panels(self):
        """Setup dockable panels"""
        # Left toolbar (tools)
        self.tool_panel = ToolPanel()
        tool_dock = QDockWidget("Tools", self)
        tool_dock.setWidget(self.tool_panel)
        tool_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tool_dock)

        # Right panels
        right_dock_area = Qt.DockWidgetArea.RightDockWidgetArea

        # Layers panel
        self.layer_panel = LayerPanel()
        layer_dock = QDockWidget("Layers", self)
        layer_dock.setWidget(self.layer_panel)
        layer_dock.setAllowedAreas(right_dock_area)
        self.addDockWidget(right_dock_area, layer_dock)

        # Color panel
        self.color_panel = ColorPanel()
        color_dock = QDockWidget("Color", self)
        color_dock.setWidget(self.color_panel)
        color_dock.setAllowedAreas(right_dock_area)
        self.addDockWidget(right_dock_area, color_dock)

        # Properties panel
        self.properties_panel = PropertiesPanel()
        properties_dock = QDockWidget("Properties", self)
        properties_dock.setWidget(self.properties_panel)
        properties_dock.setAllowedAreas(right_dock_area)
        self.addDockWidget(right_dock_area, properties_dock)

        # Tab right panels together
        self.tabifyDockWidget(layer_dock, color_dock)
        self.tabifyDockWidget(color_dock, properties_dock)

        # Show layers panel by default
        layer_dock.raise()

    def _setup_status_bar(self):
        """Setup the status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Add permanent widgets to status bar
        # (Zoom level, cursor position, etc.)

    def _setup_connections(self):
        """Setup signal connections"""
        # Connect application signals
        self.app.document_changed.connect(self._on_document_changed)
        self.app.status_message.connect(self.statusBar().showMessage)
        self.app.progress_updated.connect(self._on_progress_updated)

        # Connect panel signals
        if self.tool_panel:
            self.tool_panel.tool_selected.connect(self._on_tool_selected)

        # Connect canvas signals
        if self.canvas_view:
            self.canvas_view.canvas_clicked.connect(self._on_canvas_clicked)
            self.canvas_view.canvas_dragged.connect(self._on_canvas_dragged)

        # Connect color panel
        if self.color_panel:
            self.color_panel.color_changed.connect(self._on_color_changed)

    def _new_document(self):
        """Create a new document"""
        self.app.new_document()

    def _show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About Paint+",
            "Paint+ Version 0.1.0\n\n"
            "A professional image editor built with PyQt6\n\n"
            "© 2024 Paint+ Team"
        )

    def _on_document_changed(self, document):
        """Handle document change"""
        if document and self.canvas_view:
            # Update canvas with new document
            self.canvas_view.set_scene(document["canvas_scene"])

            # Update panels
            if self.layer_panel:
                self.layer_panel.set_layer_stack(document["layer_stack"])

    def _on_tool_selected(self, tool_name):
        """Handle tool selection"""
        # Update properties panel with tool options
        if self.properties_panel:
            self.properties_panel.set_tool_options(tool_name)

        # Update status bar
        self.statusBar().showMessage(f"Tool: {tool_name}")

    def _on_progress_updated(self, value, message):
        """Handle progress updates"""
        # Update status bar with progress
        self.statusBar().showMessage(f"{message} ({value}%)")

    def _on_canvas_clicked(self, pos, event):
        """Handle canvas click events"""
        # Get current tool and document
        current_tool = self.tool_panel.get_current_tool() if self.tool_panel else None
        if not current_tool or not self.app.current_document:
            return

        # Get active layer
        layer_stack = self.app.current_document["layer_stack"]
        active_layer = layer_stack.get_active_layer()
        if not active_layer:
            return

        # Forward event to tool
        current_tool.mouse_press(event, active_layer, pos)

    def _on_canvas_dragged(self, pos, event):
        """Handle canvas drag events"""
        # Get current tool and document
        current_tool = self.tool_panel.get_current_tool() if self.tool_panel else None
        if not current_tool or not self.app.current_document:
            return

        # Get active layer
        layer_stack = self.app.current_document["layer_stack"]
        active_layer = layer_stack.get_active_layer()
        if not active_layer:
            return

        # Forward event to tool
        current_tool.mouse_move(event, active_layer, pos)

    def _on_color_changed(self, color):
        """Handle color change from color panel"""
        # Get current tool and update its color
        current_tool = self.tool_panel.get_current_tool() if self.tool_panel else None
        if current_tool:
            current_tool.set_color(color)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.app.close_document():
            event.accept()
        else:
            event.ignore()