"""
Properties panel for Paint+ UI - displays context-sensitive properties
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSpinBox, QSlider, QComboBox, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt

from ...tools.base_tool import BaseTool


class PropertiesPanel(QWidget):
    """Properties panel for tool and document settings"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_tool: Optional[BaseTool] = None
        self.tool_widget: Optional[QWidget] = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the properties panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Title
        title_label = QLabel("Properties")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title_label)

        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Properties container
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_container)
        self.properties_layout.setContentsMargins(0, 0, 0, 0)
        self.properties_layout.setSpacing(4)

        scroll_area.setWidget(self.properties_container)
        layout.addWidget(scroll_area)

        # Default content - no tool selected
        self._show_no_tool_selected()

    def set_tool_options(self, tool_name: str):
        """Set the current tool and display its options

        Args:
            tool_name: Name of the currently selected tool
        """
        # Clear current content
        self._clear_properties()

        if not tool_name:
            self._show_no_tool_selected()
            return

        # Create tool-specific properties
        self._create_tool_properties(tool_name)

    def _clear_properties(self):
        """Clear all current properties"""
        # Remove all widgets from the layout
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.tool_widget = None

    def _show_no_tool_selected(self):
        """Show message when no tool is selected"""
        no_tool_label = QLabel("No tool selected")
        no_tool_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_tool_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        self.properties_layout.addWidget(no_tool_label)

    def _create_tool_properties(self, tool_name: str):
        """Create properties for the specified tool

        Args:
            tool_name: Name of tool to create properties for
        """
        # Create title for current tool
        tool_title = QLabel(f"Tool: {tool_name}")
        tool_title.setStyleSheet("font-weight: bold; color: #333;")
        self.properties_layout.addWidget(tool_title)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_layout.addWidget(separator)

        # Tool-specific properties would be created here
        # For now, show common properties for all tools

        if tool_name == "Brush":
            self._create_brush_properties()
        elif tool_name == "Eraser":
            self._create_eraser_properties()
        elif tool_name == "Eyedropper":
            self._create_eyedropper_properties()
        else:
            self._create_generic_properties()

        # Add stretch at bottom
        self.properties_layout.addStretch()

    def _create_brush_properties(self):
        """Create properties specific to brush tool"""
        # Size group
        size_group = QGroupBox("Brush Size")
        size_layout = QHBoxLayout(size_group)

        size_layout.addWidget(QLabel("Size:"))
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 500)
        size_slider.setValue(10)
        size_layout.addWidget(size_slider)

        size_spinbox = QSpinBox()
        size_spinbox.setRange(1, 500)
        size_spinbox.setValue(10)
        size_layout.addWidget(size_spinbox)

        self.properties_layout.addWidget(size_group)

        # Opacity group
        opacity_group = QGroupBox("Opacity")
        opacity_layout = QHBoxLayout(opacity_group)

        opacity_layout.addWidget(QLabel("Opacity:"))
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(100)
        opacity_layout.addWidget(opacity_slider)

        opacity_spinbox = QSpinBox()
        opacity_spinbox.setRange(0, 100)
        opacity_spinbox.setValue(100)
        opacity_spinbox.setSuffix("%")
        opacity_layout.addWidget(opacity_spinbox)

        self.properties_layout.addWidget(opacity_group)

        # Hardness group
        hardness_group = QGroupBox("Hardness")
        hardness_layout = QHBoxLayout(hardness_group)

        hardness_layout.addWidget(QLabel("Hardness:"))
        hardness_slider = QSlider(Qt.Orientation.Horizontal)
        hardness_slider.setRange(0, 100)
        hardness_slider.setValue(100)
        hardness_layout.addWidget(hardness_slider)

        hardness_spinbox = QSpinBox()
        hardness_spinbox.setRange(0, 100)
        hardness_spinbox.setValue(100)
        hardness_spinbox.setSuffix("%")
        hardness_layout.addWidget(hardness_spinbox)

        self.properties_layout.addWidget(hardness_group)

        # Flow group
        flow_group = QGroupBox("Flow")
        flow_layout = QHBoxLayout(flow_group)

        flow_layout.addWidget(QLabel("Flow:"))
        flow_slider = QSlider(Qt.Orientation.Horizontal)
        flow_slider.setRange(1, 100)
        flow_slider.setValue(100)
        flow_layout.addWidget(flow_slider)

        flow_spinbox = QSpinBox()
        flow_spinbox.setRange(1, 100)
        flow_spinbox.setValue(100)
        flow_spinbox.setSuffix("%")
        flow_layout.addWidget(flow_spinbox)

        self.properties_layout.addWidget(flow_group)

    def _create_eraser_properties(self):
        """Create properties specific to eraser tool"""
        # Size group
        size_group = QGroupBox("Eraser Size")
        size_layout = QHBoxLayout(size_group)

        size_layout.addWidget(QLabel("Size:"))
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 500)
        size_slider.setValue(20)
        size_layout.addWidget(size_slider)

        size_spinbox = QSpinBox()
        size_spinbox.setRange(1, 500)
        size_spinbox.setValue(20)
        size_layout.addWidget(size_spinbox)

        self.properties_layout.addWidget(size_group)

        # Opacity group
        opacity_group = QGroupBox("Opacity")
        opacity_layout = QHBoxLayout(opacity_group)

        opacity_layout.addWidget(QLabel("Opacity:"))
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(100)
        opacity_layout.addWidget(opacity_slider)

        opacity_spinbox = QSpinBox()
        opacity_spinbox.setRange(0, 100)
        opacity_spinbox.setValue(100)
        opacity_spinbox.setSuffix("%")
        opacity_layout.addWidget(opacity_spinbox)

        self.properties_layout.addWidget(opacity_group)

        # Hardness group
        hardness_group = QGroupBox("Hardness")
        hardness_layout = QHBoxLayout(hardness_group)

        hardness_layout.addWidget(QLabel("Hardness:"))
        hardness_slider = QSlider(Qt.Orientation.Horizontal)
        hardness_slider.setRange(0, 100)
        hardness_slider.setValue(100)
        hardness_layout.addWidget(hardness_slider)

        hardness_spinbox = QSpinBox()
        hardness_spinbox.setRange(0, 100)
        hardness_spinbox.setValue(100)
        hardness_spinbox.setSuffix("%")
        hardness_layout.addWidget(hardness_spinbox)

        self.properties_layout.addWidget(hardness_group)

    def _create_eyedropper_properties(self):
        """Create properties specific to eyedropper tool"""
        info_label = QLabel("Click on canvas to sample color")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        self.properties_layout.addWidget(info_label)

        # Sample size group
        sample_group = QGroupBox("Sample Size")
        sample_layout = QVBoxLayout(sample_group)

        point_sample = QRadioButton("Point Sample")
        point_sample.setChecked(True)
        sample_layout.addWidget(point_sample)

        avg_3x3 = QRadioButton("3×3 Average")
        sample_layout.addWidget(avg_3x3)

        avg_5x5 = QRadioButton("5×5 Average")
        sample_layout.addWidget(avg_5x5)

        self.properties_layout.addWidget(sample_group)

    def _create_generic_properties(self):
        """Create generic properties for unknown tools"""
        info_label = QLabel("Properties for this tool are not yet implemented")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        self.properties_layout.addWidget(info_label)

    def set_document_properties(self, document_info: Dict[str, Any]):
        """Set document properties display

        Args:
            document_info: Dictionary containing document information
        """
        # Clear current content
        self._clear_properties()

        # Document title
        doc_title = QLabel("Document Properties")
        doc_title.setStyleSheet("font-weight: bold; color: #333;")
        self.properties_layout.addWidget(doc_title)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.properties_layout.addWidget(separator)

        # Document dimensions
        dimensions_group = QGroupBox("Dimensions")
        dimensions_layout = QVBoxLayout(dimensions_group)

        width_label = QLabel(f"Width: {document_info.get('width', 'N/A')} px")
        dimensions_layout.addWidget(width_label)

        height_label = QLabel(f"Height: {document_info.get('height', 'N/A')} px")
        dimensions_layout.addWidget(height_label)

        self.properties_layout.addWidget(dimensions_group)

        # Document resolution
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QVBoxLayout(resolution_group)

        dpi_label = QLabel(f"DPI: {document_info.get('dpi', 'N/A')}")
        resolution_layout.addWidget(dpi_label)

        self.properties_layout.addWidget(resolution_group)

        # Color mode
        color_group = QGroupBox("Color Mode")
        color_layout = QVBoxLayout(color_group)

        color_mode_label = QLabel(f"Mode: {document_info.get('color_mode', 'N/A')}")
        color_layout.addWidget(color_mode_label)

        self.properties_layout.addWidget(color_group)

        self.properties_layout.addStretch()