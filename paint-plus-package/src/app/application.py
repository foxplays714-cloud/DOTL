"""
Main Paint+ application class
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QCloseEvent

from .config import Config
from ..ui.main_window import PaintPlusMainWindow
from ..canvas.canvas_scene import CanvasScene
from ..layers.layer_stack import LayerStack
from ..io.import_manager import ImportManager
from ..io.export_manager import ExportManager


class PaintPlusApplication(QObject):
    """Main application class that manages the overall Paint+ application"""

    # Signals
    document_changed = pyqtSignal(object)  # Emitted when current document changes
    status_message = pyqtSignal(str)  # For status bar messages
    progress_updated = pyqtSignal(int, str)  # Progress updates

    def __init__(self, config: Config):
        """Initialize the Paint+ application

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config
        self.main_window: Optional[PaintPlusMainWindow] = None
        self.current_document: Optional[dict] = None

        # Initialize managers
        self.import_manager = ImportManager()
        self.export_manager = ExportManager()

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)

        # Setup auto-save
        auto_save_interval = self.config.get("ui.auto_save_interval_minutes", 10)
        if auto_save_interval > 0:
            self.auto_save_timer.start(auto_save_interval * 60 * 1000)  # Convert to milliseconds

    def show_main_window(self) -> None:
        """Create and show the main application window"""
        self.main_window = PaintPlusMainWindow(self)
        self.main_window.show()

        # Create a new blank document
        self.new_document()

    def new_document(self, width: int = 1920, height: int = 1080,
                    dpi: int = 72, color_mode: str = "RGB") -> None:
        """Create a new document

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            dpi: Resolution in dots per inch
            color_mode: Color mode (RGB, CMYK, Grayscale)
        """
        # Create new document structure
        self.current_document = {
            "width": width,
            "height": height,
            "dpi": dpi,
            "color_mode": color_mode,
            "file_path": None,
            "modified": False,
            "layer_stack": LayerStack(),
            "canvas_scene": CanvasScene(width, height)
        }

        # Setup the canvas with a background layer
        self.current_document["layer_stack"].add_background_layer(width, height)

        # Update UI
        self.document_changed.emit(self.current_document)
        self.status_message.emit(f"New document: {width}x{height} pixels")

    def open_document(self) -> None:
        """Open an existing document"""
        if not self.main_window:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Image",
            "",
            "Supported Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif);;All Files (*)"
        )

        if file_path:
            self._open_file(file_path)

    def save_document(self) -> bool:
        """Save the current document

        Returns:
            True if save was successful, False otherwise
        """
        if not self.current_document:
            return False

        file_path = self.current_document.get("file_path")

        if not file_path:
            return self.save_document_as()

        return self._save_file(file_path)

    def save_document_as(self) -> bool:
        """Save the current document with a new file name

        Returns:
            True if save was successful, False otherwise
        """
        if not self.current_document or not self.main_window:
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save As",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
        )

        if file_path:
            return self._save_file(file_path)

        return False

    def _open_file(self, file_path: str) -> None:
        """Open a file from the given path

        Args:
            file_path: Path to the file to open
        """
        try:
            # Show progress
            self.status_message.emit("Loading...")
            self.progress_updated.emit(0, "Loading file...")

            # Import the file
            document_data = self.import_manager.import_file(file_path)

            if document_data:
                # Create new document with imported data
                self.current_document = {
                    "width": document_data["width"],
                    "height": document_data["height"],
                    "dpi": document_data.get("dpi", 72),
                    "color_mode": document_data.get("color_mode", "RGB"),
                    "file_path": file_path,
                    "modified": False,
                    "layer_stack": document_data.get("layer_stack", LayerStack()),
                    "canvas_scene": CanvasScene(document_data["width"], document_data["height"])
                }

                # Setup layers from imported data
                if "layers" in document_data:
                    for layer_data in document_data["layers"]:
                        self.current_document["layer_stack"].import_layer(layer_data)

                # Update UI
                self.document_changed.emit(self.current_document)
                self.status_message.emit(f"Opened: {Path(file_path).name}")
                self.progress_updated.emit(100, "File loaded")
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Could not open file: {file_path}"
                )

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to open file: {str(e)}"
            )
            self.status_message.emit("Failed to open file")

    def _save_file(self, file_path: str) -> bool:
        """Save the current document to the given file path

        Args:
            file_path: Path to save the file

        Returns:
            True if save was successful, False otherwise
        """
        try:
            if not self.current_document:
                return False

            # Show progress
            self.status_message.emit("Saving...")
            self.progress_updated.emit(0, "Preparing to save...")

            # Prepare document data for export
            document_data = {
                "width": self.current_document["width"],
                "height": self.current_document["height"],
                "dpi": self.current_document["dpi"],
                "color_mode": self.current_document["color_mode"],
                "layers": []
            }

            # Export layer data
            for layer in self.current_document["layer_stack"].get_layers():
                layer_data = {
                    "name": layer.name,
                    "visible": layer.visible,
                    "opacity": layer.opacity,
                    "blend_mode": layer.blend_mode,
                    "image_data": layer.get_image_data()
                }
                document_data["layers"].append(layer_data)

            # Save the file
            success = self.export_manager.export_file(file_path, document_data)

            if success:
                self.current_document["file_path"] = file_path
                self.current_document["modified"] = False
                self.status_message.emit(f"Saved: {Path(file_path).name}")
                self.progress_updated.emit(100, "File saved")
                return True
            else:
                raise Exception("Export failed")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to save file: {str(e)}"
            )
            self.status_message.emit("Failed to save file")
            return False

    def _auto_save(self) -> None:
        """Auto-save the current document if modified"""
        if (self.current_document and
            self.current_document.get("modified", False) and
            self.current_document.get("file_path")):

            try:
                file_path = self.current_document["file_path"]
                # Create auto-save file path
                auto_save_path = Path(file_path).with_suffix(
                    f".autosave{Path(file_path).suffix}"
                )

                if self._save_file(str(auto_save_path)):
                    self.status_message.emit("Auto-saved")
            except Exception:
                # Auto-save failed, but don't bother the user
                pass

    def close_document(self) -> bool:
        """Close the current document

        Returns:
            True if document was closed, False if user cancelled
        """
        if not self.current_document:
            return True

        # Check if document needs saving
        if self.current_document.get("modified", False):
            file_name = Path(self.current_document.get("file_path", "Untitled")).name

            reply = QMessageBox.question(
                self.main_window,
                "Save Changes?",
                f"Save changes to {file_name} before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self.save_document():
                    return False  # Save failed or cancelled
            elif reply == QMessageBox.StandardButton.Cancel:
                return False  # User cancelled

        # Close document
        self.current_document = None
        self.document_changed.emit(None)
        self.status_message.emit("Document closed")
        return True

    def exit_application(self) -> None:
        """Exit the application"""
        if self.close_document():
            QApplication.quit()