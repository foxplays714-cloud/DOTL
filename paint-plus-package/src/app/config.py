"""
Configuration management for Paint+
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtCore import QStandardPaths, QSettings


class Config:
    """Configuration manager for Paint+ application"""

    def __init__(self):
        self._settings = QSettings("Paint+ Team", "Paint+")
        self._config_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        ))
        self._config_dir.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self._defaults = {
            "canvas": {
                "background_color": "#808080",
                "transparency_background": "#ffffff",
                "zoom_wheel_invert": False,
                "zoom_fit_to_window": True
            },
            "performance": {
                "enable_gpu_acceleration": True,
                "tile_size": 512,
                "memory_limit_mb": 2048,
                "max_undo_levels": 50
            },
            "ui": {
                "theme": "default",
                "font_size": 12,
                "show_tooltips": True,
                "auto_save_interval_minutes": 10
            },
            "tools": {
                "brush_size": 10,
                "brush_hardness": 100,
                "brush_opacity": 100,
                "eraser_hardness": 100
            },
            "panels": {
                "layers_visible": True,
                "tools_visible": True,
                "colors_visible": True,
                "properties_visible": True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key

        Args:
            key: Configuration key in dot notation (e.g., 'canvas.background_color')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        # Try QSettings first
        value = self._settings.value(key)
        if value is not None:
            return value

        # Try defaults
        keys = key.split('.')
        current = self._defaults

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        self._settings.setValue(key, value)
        self._settings.sync()

    def get_config_dir(self) -> Path:
        """Get application configuration directory"""
        return self._config_dir

    def get_user_presets_dir(self) -> Path:
        """Get user presets directory"""
        presets_dir = self._config_dir / "presets"
        presets_dir.mkdir(exist_ok=True)
        return presets_dir

    def get_user_plugins_dir(self) -> Path:
        """Get user plugins directory"""
        plugins_dir = self._config_dir / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        return plugins_dir

    def get_user_temp_dir(self) -> Path:
        """Get user temporary directory"""
        temp_dir = self._config_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self._settings.clear()
        self._settings.sync()

    def export_settings(self, file_path: Path) -> None:
        """Export current settings to file

        Args:
            file_path: Path to export file
        """
        settings_dict = {}

        for key in self._settings.allKeys():
            settings_dict[key] = self._settings.value(key)

        with open(file_path, 'w') as f:
            json.dump(settings_dict, f, indent=2)

    def import_settings(self, file_path: Path) -> None:
        """Import settings from file

        Args:
            file_path: Path to import file
        """
        with open(file_path, 'r') as f:
            settings_dict = json.load(f)

        for key, value in settings_dict.items():
            self._settings.setValue(key, value)

        self._settings.sync()