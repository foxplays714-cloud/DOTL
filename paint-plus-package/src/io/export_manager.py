"""
Export manager for Paint+ - handles file exporting
"""

from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from PyQt6.QtGui import QImage
from PIL import Image as PILImage


class ExportManager:
    """Manages file export operations for Paint+"""

    def __init__(self):
        """Initialize export manager"""
        self.supported_formats = {
            '.png': self._export_png,
            '.jpg': self._export_jpg,
            '.jpeg': self._export_jpg,
            '.bmp': self._export_bmp,
            '.tiff': self._export_tiff,
            '.tif': self._export_tiff,
            '.webp': self._export_webp,
        }

        self.format_quality = {
            '.jpg': 95,
            '.jpeg': 95,
            '.webp': 90,
        }

    def export_file(self, file_path: str, document_data: Dict[str, Any],
                   quality: Optional[int] = None) -> bool:
        """Export document data to file

        Args:
            file_path: Path to save file
            document_data: Document data to export
            quality: Optional quality setting for lossy formats

        Returns:
            True if export was successful
        """
        path = Path(file_path)
        file_extension = path.suffix.lower()

        if file_extension not in self.supported_formats:
            return False

        try:
            # Use provided quality or default for format
            if quality is None:
                quality = self.format_quality.get(file_extension, 100)

            # Call the appropriate export function
            export_function = self.supported_formats[file_extension]
            return export_function(file_path, document_data, quality)

        except Exception as e:
            print(f"Error exporting file {file_path}: {str(e)}")
            return False

    def _export_png(self, file_path: str, document_data: Dict[str, Any],
                   quality: int) -> bool:
        """Export as PNG"""
        return self._export_generic_image(file_path, document_data, "PNG")

    def _export_jpg(self, file_path: str, document_data: Dict[str, Any],
                   quality: int) -> bool:
        """Export as JPEG"""
        return self._export_generic_image(file_path, document_data, "JPEG", quality)

    def _export_bmp(self, file_path: str, document_data: Dict[str, Any],
                   quality: int) -> bool:
        """Export as BMP"""
        return self._export_generic_image(file_path, document_data, "BMP")

    def _export_tiff(self, file_path: str, document_data: Dict[str, Any],
                    quality: int) -> bool:
        """Export as TIFF"""
        return self._export_generic_image(file_path, document_data, "TIFF")

    def _export_webp(self, file_path: str, document_data: Dict[str, Any],
                    quality: int) -> bool:
        """Export as WebP"""
        return self._export_generic_image(file_path, document_data, "WEBP", quality)

    def _export_generic_image(self, file_path: str, document_data: Dict[str, Any],
                             format_name: str, quality: int = 100) -> bool:
        """Generic image export

        Args:
            file_path: Path to save file
            document_data: Document data to export
            format_name: PIL format name
            quality: Quality for lossy formats

        Returns:
            True if export was successful
        """
        try:
            # Composite all layers into a single image
            final_image = self._composite_layers(document_data)

            if final_image is None:
                return False

            # Convert numpy array to PIL Image
            pil_image = PILImage.fromarray(final_image, 'RGBA')

            # Handle JPEG format (no alpha)
            if format_name in ['JPEG', 'JPG']:
                # Create white background
                background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'RGBA':
                    background.paste(pil_image, mask=pil_image.split()[-1])
                else:
                    background.paste(pil_image)
                pil_image = background

                # Save with quality
                pil_image.save(file_path, format=format_name, quality=quality)
            else:
                # Save other formats
                save_kwargs = {}
                if format_name == 'WEBP':
                    save_kwargs['quality'] = quality
                    save_kwargs['method'] = 6  # Best compression

                pil_image.save(file_path, format=format_name, **save_kwargs)

            return True

        except Exception as e:
            print(f"Error in generic image export: {str(e)}")
            return False

    def _composite_layers(self, document_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Composite all layers into a single image

        Args:
            document_data: Document data containing layers

        Returns:
            Composited image as numpy array or None if failed
        """
        try:
            width = document_data.get("width", 1920)
            height = document_data.get("height", 1080)

            # Create transparent background
            composited = np.zeros((height, width, 4), dtype=np.uint8)

            # Get layers (if available)
            layers = document_data.get("layers", [])

            if not layers:
                # No layers, return transparent background
                return composited

            # Composite layers from bottom to top
            for layer in layers:
                if hasattr(layer, 'is_visible') and not layer.is_visible():
                    continue

                if hasattr(layer, 'get_image_data'):
                    layer_data = layer.get_image_data()

                    # Simple alpha compositing
                    composited = self._alpha_composite(composited, layer_data)

            return composited

        except Exception as e:
            print(f"Error compositing layers: {str(e)}")
            return None

    def _alpha_composite(self, bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
        """Alpha composite two image arrays

        Args:
            bottom: Bottom image data
            top: Top image data

        Returns:
            Composited image data
        """
        # Ensure same size
        if bottom.shape != top.shape:
            # Resize top to match bottom if needed
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
        result[:, :, :3] = np.clip(color_out, 0, 255).astype(np.uint8)
        result[:, :, 3] = np.clip(alpha_out * 255, 0, 255).astype(np.uint8)

        return result

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

    def set_quality(self, format_extension: str, quality: int):
        """Set default quality for a format

        Args:
            format_extension: File extension (e.g., '.jpg')
            quality: Quality value (1-100)
        """
        if format_extension in self.format_quality:
            self.format_quality[format_extension] = max(1, min(100, quality))

    def get_quality(self, format_extension: str) -> int:
        """Get default quality for a format

        Args:
            format_extension: File extension (e.g., '.jpg')

        Returns:
            Quality value (1-100)
        """
        return self.format_quality.get(format_extension, 100)