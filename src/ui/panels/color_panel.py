"""
Color panel for Paint+ UI
"""

from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QSlider, QFrame, QGridLayout, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QBrush

class ColorPanel(QWidget):
    """Color panel for color selection and management"""

    # Signals
    color_changed = pyqtSignal(tuple)  # (R, G, B, A) tuple

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_color = (0, 0, 0, 255)  # Black by default
        self.background_color = (255, 255, 255, 255)  # White by default

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """Setup the color panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Title
        title_label = QLabel("Color")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title_label)

        # Color swatches (foreground/background)
        swatch_layout = QHBoxLayout()

        # Current color (foreground)
        self.foreground_swatch = ColorSwatch()
        self.foreground_swatch.clicked.connect(self._pick_color)
        swatch_layout.addWidget(self.foreground_swatch)

        # Background color
        self.background_swatch = ColorSwatch()
        self.background_swatch.clicked.connect(self._pick_background_color)
        swatch_layout.addWidget(self.background_swatch)

        layout.addLayout(swatch_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # RGB sliders
        rgb_label = QLabel("RGB")
        rgb_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(rgb_label)

        # Red
        red_layout = QHBoxLayout()
        red_layout.addWidget(QLabel("R:"))
        self.red_slider = QSlider(Qt.Orientation.Horizontal)
        self.red_slider.setRange(0, 255)
        self.red_slider.setValue(self.current_color[0])
        self.red_slider.valueChanged.connect(self._on_rgb_changed)
        red_layout.addWidget(self.red_slider)
        self.red_spinbox = QSpinBox()
        self.red_spinbox.setRange(0, 255)
        self.red_spinbox.setValue(self.current_color[0])
        self.red_spinbox.valueChanged.connect(self._on_red_spinbox_changed)
        red_layout.addWidget(self.red_spinbox)
        layout.addLayout(red_layout)

        # Green
        green_layout = QHBoxLayout()
        green_layout.addWidget(QLabel("G:"))
        self.green_slider = QSlider(Qt.Orientation.Horizontal)
        self.green_slider.setRange(0, 255)
        self.green_slider.setValue(self.current_color[1])
        self.green_slider.valueChanged.connect(self._on_rgb_changed)
        green_layout.addWidget(self.green_slider)
        self.green_spinbox = QSpinBox()
        self.green_spinbox.setRange(0, 255)
        self.green_spinbox.setValue(self.current_color[1])
        self.green_spinbox.valueChanged.connect(self._on_green_spinbox_changed)
        green_layout.addWidget(self.green_spinbox)
        layout.addLayout(green_layout)

        # Blue
        blue_layout = QHBoxLayout()
        blue_layout.addWidget(QLabel("B:"))
        self.blue_slider = QSlider(Qt.Orientation.Horizontal)
        self.blue_slider.setRange(0, 255)
        self.blue_slider.setValue(self.current_color[2])
        self.blue_slider.valueChanged.connect(self._on_rgb_changed)
        blue_layout.addWidget(self.blue_slider)
        self.blue_spinbox = QSpinBox()
        self.blue_spinbox.setRange(0, 255)
        self.blue_spinbox.setValue(self.current_color[2])
        self.blue_spinbox.valueChanged.connect(self._on_blue_spinbox_changed)
        blue_layout.addWidget(self.blue_spinbox)
        layout.addLayout(blue_layout)

        # Alpha (opacity)
        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(QLabel("A:"))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(self.current_color[3])
        self.alpha_slider.valueChanged.connect(self._on_rgb_changed)
        alpha_layout.addWidget(self.alpha_slider)
        self.alpha_spinbox = QSpinBox()
        self.alpha_spinbox.setRange(0, 255)
        self.alpha_spinbox.setValue(self.current_color[3])
        self.alpha_spinbox.valueChanged.connect(self._on_alpha_spinbox_changed)
        alpha_layout.addWidget(self.alpha_spinbox)
        layout.addLayout(alpha_layout)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        # Hex color input
        hex_layout = QHBoxLayout()
        hex_layout.addWidget(QLabel("Hex:"))
        self.hex_input = QLineEdit()
        self.hex_input.setText("#000000")
        self.hex_input.textChanged.connect(self._on_hex_changed)
        hex_layout.addWidget(self.hex_input)
        layout.addLayout(hex_layout)

        # Color presets
        preset_label = QLabel("Presets")
        preset_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(preset_label)

        # Preset color grid
        preset_layout = QGridLayout()
        preset_colors = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 128, 128), (64, 64, 64), (192, 192, 192), (128, 0, 0),
            (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128)
        ]

        for i, (r, g, b) in enumerate(preset_colors):
            row = i // 4
            col = i % 4
            preset_btn = PresetColorButton(r, g, b)
            preset_btn.color_selected.connect(self._set_rgb_color)
            preset_layout.addWidget(preset_btn, row, col)

        layout.addLayout(preset_layout)

        layout.addStretch()

    def _update_display(self):
        """Update all display elements with current color"""
        r, g, b, a = self.current_color

        # Update sliders and spinboxes (without triggering signals)
        self.red_slider.blockSignals(True)
        self.green_slider.blockSignals(True)
        self.blue_slider.blockSignals(True)
        self.alpha_slider.blockSignals(True)

        self.red_slider.setValue(r)
        self.green_slider.setValue(g)
        self.blue_slider.setValue(b)
        self.alpha_slider.setValue(a)

        self.red_slider.blockSignals(False)
        self.green_slider.blockSignals(False)
        self.blue_slider.blockSignals(False)
        self.alpha_slider.blockSignals(False)

        self.red_spinbox.blockSignals(True)
        self.green_spinbox.blockSignals(True)
        self.blue_spinbox.blockSignals(True)
        self.alpha_spinbox.blockSignals(True)

        self.red_spinbox.setValue(r)
        self.green_spinbox.setValue(g)
        self.blue_spinbox.setValue(b)
        self.alpha_spinbox.setValue(a)

        self.red_spinbox.blockSignals(False)
        self.green_spinbox.blockSignals(False)
        self.blue_spinbox.blockSignals(False)
        self.alpha_spinbox.blockSignals(False)

        # Update hex input
        self.hex_input.blockSignals(True)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.hex_input.setText(hex_color.upper())
        self.hex_input.blockSignals(False)

        # Update swatches
        self.foreground_swatch.set_color(self.current_color)
        self.background_swatch.set_color(self.background_color)

    def _on_rgb_changed(self):
        """Handle RGB slider changes"""
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        a = self.alpha_slider.value()

        self.current_color = (r, g, b, a)
        self._update_display()
        self.color_changed.emit(self.current_color)

    def _on_red_spinbox_changed(self, value):
        self.red_slider.setValue(value)

    def _on_green_spinbox_changed(self, value):
        self.green_slider.setValue(value)

    def _on_blue_spinbox_changed(self, value):
        self.blue_slider.setValue(value)

    def _on_alpha_spinbox_changed(self, value):
        self.alpha_slider.setValue(value)

    def _on_hex_changed(self, text):
        """Handle hex color input changes"""
        hex_text = text.lstrip('#')
        if len(hex_text) == 6:
            try:
                r = int(hex_text[0:2], 16)
                g = int(hex_text[2:4], 16)
                b = int(hex_text[4:6], 16)
                self.current_color = (r, g, b, self.current_color[3])
                self._update_display()
                self.color_changed.emit(self.current_color)
            except ValueError:
                pass  # Invalid hex, ignore

    def _set_rgb_color(self, r: int, g: int, b: int):
        """Set RGB color (maintains current alpha)"""
        self.current_color = (r, g, b, self.current_color[3])
        self._update_display()
        self.color_changed.emit(self.current_color)

    def _pick_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = (color.red(), color.green(), color.blue(), self.current_color[3])
            self._update_display()
            self.color_changed.emit(self.current_color)

    def _pick_background_color(self):
        """Open color picker dialog for background color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = (color.red(), color.green(), color.blue(), self.current_color[3])
            self.foreground_swatch.set_color(self.current_color)
            self.background_swatch.set_color(self.background_color)

    def set_color(self, color: Tuple[int, int, int, int]):
        """Set the current color

        Args:
            color: (R, G, B, A) tuple
        """
        if len(color) == 3:
            color = (*color, 255)  # Add alpha if not provided

        self.current_color = color
        self._update_display()

    def get_color(self) -> Tuple[int, int, int, int]:
        """Get the current color

        Returns:
            (R, G, B, A) tuple
        """
        return self.current_color


class ColorSwatch(QPushButton):
    """A clickable color swatch widget"""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = (0, 0, 0, 255)
        self.setFixedSize(60, 60)
        self.clicked.connect(self._on_clicked)

    def set_color(self, color: Tuple[int, int, int, int]):
        """Set the swatch color"""
        self.color = color
        self.update()

    def paintEvent(self, event):
        """Paint the color swatch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw color
        qcolor = QColor(*self.color)
        painter.fillRect(self.rect(), qcolor)

        # Draw border
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def _on_clicked(self):
        """Handle swatch click"""
        self.clicked.emit()


class PresetColorButton(QPushButton):
    """A button that represents a preset color"""

    color_selected = pyqtSignal(int, int, int)

    def __init__(self, r: int, g: int, b: int, parent=None):
        super().__init__(parent)
        self.color = (r, g, b)
        self.setFixedSize(25, 25)
        self.clicked.connect(self._on_clicked)

    def paintEvent(self, event):
        """Paint the preset color button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw color
        qcolor = QColor(*self.color)
        painter.fillRect(self.rect(), qcolor)

        # Draw border
        painter.setPen(QColor(150, 150, 150))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def _on_clicked(self):
        """Handle button click"""
        r, g, b = self.color
        self.color_selected.emit(r, g, b)