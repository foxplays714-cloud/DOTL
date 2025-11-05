"""
Import manager for Paint+ - handles file importing
"""

from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image as PILImage

from ..layers.raster_layer import RasterLayer


class ImportManager:
    """Manages file import operations for Paint+"""

    def __init__(self):
        """Initialize import manager"""
        self.supported_formats = {
            '.png': self._import_png,
            '.jpg': self._import_jpg,
            '.jpeg': self._import_jpg,
            '.bmp': self._import_bmp,
            '.tiff': self._import_tiff,
            '.tif': self._import_tiff,
            '.webp': self._import_webp,
        }

    def import_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import a file and return document data

        Args:
            file_path: Path to file to import

        Returns:
            Dictionary containing document data or None if import failed
        """
        path = Path(file_path)

        if not path.exists():
            return None

        file_extension = path.suffix.lower()

        if file_extension not in self.supported_formats:
            return None

        try:
            # Call the appropriate import function
            import_function = self.supported_formats[file_extension]
            return import_function(str(path))
        except Exception as e:
            print(f"Error importing file {file_path}: {str(e)}")
            return None

    def _import_png(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import PNG file"""
        return self._import_generic_image(file_path)

    def _import_jpg(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import JPEG file"""
        return self._import_generic_image(file_path)

    def _import_bmp(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import BMP file"""
        return self._import_generic_image(file_path)

    def _import_tiff(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import TIFF file"""
        return self._import_generic_image(file_path)

    def _import_webp(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import WebP file"""
        return self._import_generic_image(file_path)

    def _import_generic_image(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Generic image import using Qt and PIL

        Args:
            file_path: Path to image file

        Returns:
            Dictionary containing document data
        """
        # Load image using PIL for better format support
        try:
            pil_image = PILImage.open(file_path)

            # Convert to RGBA if needed
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')

            # Get image dimensions
            width, height = pil_image.size

            # Convert to numpy array
            image_data = np.array(pil_image)

            # Create a raster layer
            layer = RasterLayer("Background", width, height)
            layer.set_image_data(image_data)

            # Return document data
            return {
                "width": width,
                "height": height,
                "dpi": 72,  # Default DPI
                "color_mode": "RGB",
                "layers": [layer],
                "layer_stack": None  # Will be created by the application
            }

        except Exception as e:
            # Fallback to Qt image loading
            try:
                qimage = QImage(file_path)
                if qimage.isNull():
                    return None

                # Convert to RGBA format
                if qimage.format() != QImage.Format.Format_RGBA8888:
                    qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)

                width = qimage.width()
                height = qimage.height()

                # Convert to numpy array
                ptr = qimage.bits()
                ptr.setsize(width * height * 4)
                image_data = np.array(ptr).reshape(height, width, 4)

                # Create a raster layer
                layer = RasterLayer("Background", width, height)
                layer.set_image_data(image_data)

                return {
                    "width": width,
                    "height": height,
                    "dpi": 72,  # Default DPI
                    "color_mode": "RGB",
                    "layers": [layer],
                    "layer_stack": None  # Will be created by the application
                }

            except Exception as e2:
                print(f"Failed to import image with both PIL and Qt: {e}, {e2}")
                return None

    def get_supported_formats(self) -> list[str]:
        """Get list of supported file formats

        Returns:
            List of supported file extensions
        """
        return list(self.supported_formats.keys())

    def is_format_supported(self, file_path: str) -> bool:
        """Check if a file format is supported

        Args:
            file_path: Path to file

        Returns:
            True if format is supported
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.supported_formats

    def get_format_filter(self) -> str:
        """Get file dialog filter string

        Returns:
            Filter string for QFileDialog
        """
        format_names = {
            '.png': 'PNG Files (*.png)',
            '.jpg': 'JPEG Files (*.jpg *.jpeg)',
            '.jpeg': 'JPEG Files (*.jpg *.jpeg)',
            '.bmp': 'BMP Files (*.bmp)',
            '.tiff': 'TIFF Files (*.tiff *.tif)',
            '.tif': 'TIFF Files (*.tiff *.tif)',
            '.webp': 'WebP Files (*.webp)',
        }

        filters = []
        for ext, name in format_names.items():
            if ext in self.supported_formats:
                filters.append(name)

        return ";;".join(filters) + ";;All Files (*)"