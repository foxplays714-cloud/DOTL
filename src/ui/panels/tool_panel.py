"""
Tool panel for Paint+ UI
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QButtonGroup,
    QScrollArea, QFrame, QLabel, QToolTip
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction

from ...tools.base_tool import BaseTool
from ...tools.brush_tools import BrushTool


class ToolPanel(QWidget):
    """Tool selection panel"""

    # Signals
    tool_selected = pyqtSignal(str)  # Tool name

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.tools: Dict[str, BaseTool] = {}
        self.tool_buttons: Dict[str, QToolButton] = {}
        self.current_tool: Optional[BaseTool] = None

        self._setup_ui()
        self._register_default_tools()
        self._layout_tools()

    def _setup_ui(self):
        """Setup the tool panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)

        # Create scroll area for tools
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Create tool container widget
        self.tool_container = QWidget()
        self.tool_layout = QVBoxLayout(self.tool_container)
        self.tool_layout.setContentsMargins(0, 0, 0, 0)
        self.tool_layout.setSpacing(1)

        scroll_area.setWidget(self.tool_container)
        layout.addWidget(scroll_area)

        # Set panel properties
        self.setMaximumWidth(80)  # Fixed width for tool panel
        self.setMinimumWidth(60)

    def _register_default_tools(self):
        """Register default tools"""
        # Basic tools
        self.register_tool(BrushTool())

        # TODO: Add more tools as they are implemented
        # self.register_tool(EraserTool())
        # self.register_tool(EyedropperTool())
        # self.register_tool(MoveTool())
        # self.register_tool(ZoomTool())
        # self.register_tool(TextTool())

    def register_tool(self, tool: BaseTool):
        """Register a new tool

        Args:
            tool: Tool to register
        """
        self.tools[tool.name] = tool

    def _layout_tools(self):
        """Layout tools in categories"""
        # Clear existing layout
        for i in reversed(range(self.tool_layout.count())):
            child = self.tool_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Group tools by category
        categories = {}
        for tool in self.tools.values():
            category = tool.category
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)

        # Create tool buttons for each category
        category_order = ["painting", "selection", "retouching", "vector", "navigation"]

        for category in category_order:
            if category in categories:
                self._add_category_section(category, categories[category])

        # Add any remaining categories
        for category, tools in categories.items():
            if category not in category_order:
                self._add_category_section(category, tools)

    def _add_category_section(self, category: str, tools: List[BaseTool]):
        """Add a category section with tools

        Args:
            category: Category name
            tools: List of tools in this category
        """
        if not tools:
            return

        # Add category separator
        if self.tool_layout.count() > 0:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setMaximumHeight(1)
            self.tool_layout.addWidget(separator)

        # Add category label
        category_label = QLabel(category.capitalize())
        category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        category_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666;
                padding: 2px;
            }
        """)
        self.tool_layout.addWidget(category_label)

        # Add tool buttons
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

        for tool in tools:
            button = self._create_tool_button(tool)
            button_group.addButton(button)
            self.tool_layout.addWidget(button)

        self.tool_layout.addStretch()

    def _create_tool_button(self, tool: BaseTool) -> QToolButton:
        """Create a tool button for the given tool

        Args:
            tool: Tool to create button for

        Returns:
            Created tool button
        """
        button = QToolButton()
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setFixedSize(48, 48)
        button.setIconSize(QSize(32, 32))
        button.setToolTip(tool.description)
        button.setStatusTip(tool.name)

        # Set tool icon or create text-based icon
        if tool.icon_path:
            button.setIcon(QIcon(tool.icon_path))
        else:
            # Create text-based icon with first letter
            text = tool.name[0].upper() if tool.name else "?"
            button.setText(text)
            button.setStyleSheet("""
                QToolButton {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f5f5f5;
                    font-size: 16px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #e0e0e0;
                    border-color: #999;
                }
                QToolButton:checked {
                    background-color: #d0d0d0;
                    border-color: #666;
                }
            """)

        # Connect button click
        button.clicked.connect(lambda: self.select_tool(tool.name))

        # Store button reference
        self.tool_buttons[tool.name] = button

        return button

    def select_tool(self, tool_name: str):
        """Select a tool by name

        Args:
            tool_name: Name of tool to select
        """
        if tool_name not in self.tools:
            return

        # Deactivate previous tool
        if self.current_tool:
            self.current_tool.deactivate()

        # Activate new tool
        self.current_tool = self.tools[tool_name]
        self.current_tool.activate()

        # Update button state
        if tool_name in self.tool_buttons:
            self.tool_buttons[tool_name].setChecked(True)

        # Emit signal
        self.tool_selected.emit(tool_name)

    def get_current_tool(self) -> Optional[BaseTool]:
        """Get the currently selected tool

        Returns:
            Current tool or None if no tool selected
        """
        return self.current_tool

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name

        Args:
            tool_name: Name of tool to get

        Returns:
            Tool or None if not found
        """
        return self.tools.get(tool_name)

    def set_tool_icon(self, tool_name: str, icon_path: str):
        """Set icon for a tool

        Args:
            tool_name: Name of tool
            icon_path: Path to icon file
        """
        if tool_name in self.tool_buttons:
            button = self.tool_buttons[tool_name]
            button.setIcon(QIcon(icon_path))
            button.setText("")  # Remove text when icon is set

    def get_tool_names(self) -> List[str]:
        """Get list of all tool names

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def select_first_tool(self):
        """Select the first available tool"""
        if self.tools:
            first_tool_name = next(iter(self.tools.keys()))
            self.select_tool(first_tool_name)