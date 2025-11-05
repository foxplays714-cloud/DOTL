"""
Layers panel for Paint+ UI
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QCheckBox, QLabel, QSlider, QSpinBox, QHeaderView,
    QComboBox, QFrame, QMenu, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ...layers.base_layer import BaseLayer
from ...layers.layer_stack import LayerStack


class LayerPanel(QWidget):
    """Layers panel for layer management"""

    # Signals
    layer_selected = pyqtSignal(int)  # Layer index
    layer_visibility_changed = pyqtSignal(int, bool)  # Layer index and visibility
    layer_opacity_changed = pyqtSignal(int, float)  # Layer index and opacity
    layer_blend_mode_changed = pyqtSignal(int, str)  # Layer index and blend mode

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.layer_stack: Optional[LayerStack] = None
        self.updating_ui = False

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the layers panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Layer controls at top
        controls_layout = QHBoxLayout()

        # New layer button
        self.new_layer_btn = QPushButton("+")
        self.new_layer_btn.setToolTip("New Layer")
        self.new_layer_btn.setFixedSize(24, 24)
        controls_layout.addWidget(self.new_layer_btn)

        # Delete layer button
        self.delete_layer_btn = QPushButton("-")
        self.delete_layer_btn.setToolTip("Delete Layer")
        self.delete_layer_btn.setFixedSize(24, 24)
        controls_layout.addWidget(self.delete_layer_btn)

        # Duplicate layer button
        self.duplicate_layer_btn = QPushButton("⧉")
        self.duplicate_layer_btn.setToolTip("Duplicate Layer")
        self.duplicate_layer_btn.setFixedSize(24, 24)
        controls_layout.addWidget(self.duplicate_layer_btn)

        # Layer group button
        self.group_btn = QPushButton("🗁")
        self.group_btn.setToolTip("Group Layers")
        self.group_btn.setFixedSize(24, 24)
        controls_layout.addWidget(self.group_btn)

        controls_layout.addStretch()

        # Blend mode dropdown
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([
            "Normal", "Multiply", "Screen", "Overlay", "Soft Light",
            "Hard Light", "Color Dodge", "Color Burn", "Darken", "Lighten",
            "Difference", "Exclusion", "Hue", "Saturation", "Color", "Luminosity"
        ])
        self.blend_mode_combo.setMaximumWidth(100)
        controls_layout.addWidget(QLabel("Blend:"))
        controls_layout.addWidget(self.blend_mode_combo)

        layout.addLayout(controls_layout)

        # Layer properties row
        props_layout = QHBoxLayout()

        # Opacity control
        props_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setMaximumWidth(80)
        props_layout.addWidget(self.opacity_slider)

        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setValue(100)
        self.opacity_spinbox.setSuffix("%")
        self.opacity_spinbox.setMaximumWidth(60)
        props_layout.addWidget(self.opacity_spinbox)

        props_layout.addStretch()
        layout.addLayout(props_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Layer tree widget
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabels(["Layer", "Opacity", "Visibility"])
        self.layer_tree.setRootIsDecorated(True)
        self.layer_tree.setAlternatingRowColors(True)

        # Setup columns
        header = self.layer_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 80)
        header.resizeSection(2, 60)

        layout.addWidget(self.layer_tree)

        # Layer list controls at bottom
        bottom_layout = QHBoxLayout()

        # Move layer up button
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setToolTip("Move Layer Up")
        self.move_up_btn.setFixedSize(24, 24)
        bottom_layout.addWidget(self.move_up_btn)

        # Move layer down button
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setToolTip("Move Layer Down")
        self.move_down_btn.setFixedSize(24, 24)
        bottom_layout.addWidget(self.move_down_btn)

        bottom_layout.addStretch()

        # Lock layer checkbox
        self.lock_checkbox = QCheckBox("Lock")
        bottom_layout.addWidget(self.lock_checkbox)

        layout.addLayout(bottom_layout)

    def _setup_connections(self):
        """Setup signal connections"""
        # Layer tree
        self.layer_tree.itemSelectionChanged.connect(self._on_layer_selection_changed)
        self.layer_tree.itemChanged.connect(self._on_layer_item_changed)
        self.layer_tree.itemClicked.connect(self._on_layer_item_clicked)

        # Control buttons
        self.new_layer_btn.clicked.connect(self._add_new_layer)
        self.delete_layer_btn.clicked.connect(self._delete_selected_layer)
        self.duplicate_layer_btn.clicked.connect(self._duplicate_selected_layer)
        self.group_btn.clicked.connect(self._group_selected_layers)
        self.move_up_btn.clicked.connect(self._move_layer_up)
        self.move_down_btn.clicked.connect(self._move_layer_down)

        # Layer properties
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        self.opacity_spinbox.valueChanged.connect(self._on_opacity_spinbox_changed)
        self.blend_mode_combo.currentTextChanged.connect(self._on_blend_mode_changed)
        self.lock_checkbox.toggled.connect(self._on_lock_toggled)

        # Context menu
        self.layer_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.layer_tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_layer_stack(self, layer_stack: LayerStack):
        """Set the layer stack to display

        Args:
            layer_stack: Layer stack to manage
        """
        # Disconnect from previous layer stack
        if self.layer_stack:
            try:
                self.layer_stack.layer_added.disconnect(self._on_layer_added)
                self.layer_stack.layer_removed.disconnect(self._on_layer_removed)
                self.layer_stack.layer_moved.disconnect(self._on_layer_moved)
                self.layer_stack.active_layer_changed.disconnect(self._on_active_layer_changed)
                self.layer_stack.stack_changed.disconnect(self._on_stack_changed)
            except:
                pass

        # Set new layer stack
        self.layer_stack = layer_stack

        # Connect to new layer stack
        if self.layer_stack:
            self.layer_stack.layer_added.connect(self._on_layer_added)
            self.layer_stack.layer_removed.connect(self._on_layer_removed)
            self.layer_stack.layer_moved.connect(self._on_layer_moved)
            self.layer_stack.active_layer_changed.connect(self._on_active_layer_changed)
            self.layer_stack.stack_changed.connect(self._on_stack_changed)

        # Refresh display
        self._refresh_layer_list()

    def _refresh_layer_list(self):
        """Refresh the layer tree widget"""
        if self.updating_ui:
            return

        self.updating_ui = True

        # Save current selection
        current_index = self.layer_tree.currentIndex().row() if self.layer_tree.currentItem() else -1

        # Clear existing items
        self.layer_tree.clear()

        if not self.layer_stack:
            self.updating_ui = False
            return

        # Add layers (from bottom to top)
        layer_count = self.layer_stack.get_layer_count()
        for i in range(layer_count):
            layer = self.layer_stack.get_layer(i)
            if layer:
                item = self._create_layer_item(layer, i)
                self.layer_tree.addTopLevelItem(item)

        # Restore selection
        if 0 <= current_index < self.layer_tree.topLevelItemCount():
            item = self.layer_tree.topLevelItem(current_index)
            self.layer_tree.setCurrentItem(item)

        self.updating_ui = False

    def _create_layer_item(self, layer: BaseLayer, index: int) -> QTreeWidgetItem:
        """Create a tree widget item for a layer

        Args:
            layer: Layer to create item for
            index: Layer index

        Returns:
            Created tree widget item
        """
        item = QTreeWidgetItem()

        # Layer name and thumbnail
        item.setText(0, layer.name)
        item.setData(0, Qt.ItemDataRole.UserRole, index)

        # Opacity
        item.setText(1, f"{int(layer.opacity * 100)}%")

        # Visibility checkbox
        item.setCheckState(2, Qt.CheckState.Checked if layer.visible else Qt.CheckState.Unchecked)

        # Set item properties
        item.setToolTip(0, f"Layer {index}: {layer.name}")
        if layer.is_locked():
            item.setIcon(0, QIcon.fromTheme("document-encrypted"))  # Locked icon

        return item

    def _get_selected_layer_index(self) -> int:
        """Get the index of the currently selected layer

        Returns:
            Selected layer index or -1 if no selection
        """
        current_item = self.layer_tree.currentItem()
        if current_item:
            return current_item.data(0, Qt.ItemDataRole.UserRole)
        return -1

    def _on_layer_selection_changed(self):
        """Handle layer selection change"""
        if self.updating_ui or not self.layer_stack:
            return

        index = self._get_selected_layer_index()
        if index >= 0:
            self.layer_stack.set_active_layer(index)
            self._update_layer_properties(index)

    def _on_layer_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle layer item changes"""
        if self.updating_ui or not self.layer_stack:
            return

        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index < 0:
            return

        layer = self.layer_stack.get_layer(index)
        if not layer:
            return

        if column == 0:  # Name changed
            layer.name = item.text(0)
        elif column == 2:  # Visibility changed
            visible = item.checkState(2) == Qt.CheckState.Checked
            layer.set_visibility(visible)
            self.layer_visibility_changed.emit(index, visible)

    def _on_layer_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle layer item clicks"""
        if column == 2:  # Visibility column
            # The checkbox will handle this via itemChanged
            pass

    def _on_opacity_slider_changed(self, value: int):
        """Handle opacity slider change"""
        if self.updating_ui:
            return

        index = self._get_selected_layer_index()
        if index >= 0 and self.layer_stack:
            layer = self.layer_stack.get_layer(index)
            if layer:
                opacity = value / 100.0
                layer.set_opacity(opacity)
                self.layer_opacity_changed.emit(index, opacity)
                self.updating_ui = True
                self.opacity_spinbox.setValue(value)
                self.updating_ui = False

                # Update tree item
                item = self.layer_tree.currentItem()
                if item:
                    item.setText(1, f"{value}%")

    def _on_opacity_spinbox_changed(self, value: int):
        """Handle opacity spinbox change"""
        if self.updating_ui:
            return

        self.updating_ui = True
        self.opacity_slider.setValue(value)
        self.updating_ui = False

        self._on_opacity_slider_changed(value)

    def _on_blend_mode_changed(self, blend_mode: str):
        """Handle blend mode change"""
        if self.updating_ui:
            return

        index = self._get_selected_layer_index()
        if index >= 0 and self.layer_stack:
            layer = self.layer_stack.get_layer(index)
            if layer:
                layer.set_blend_mode(blend_mode.lower())
                self.layer_blend_mode_changed.emit(index, blend_mode.lower())

    def _on_lock_toggled(self, checked: bool):
        """Handle lock checkbox toggle"""
        if self.updating_ui:
            return

        index = self._get_selected_layer_index()
        if index >= 0 and self.layer_stack:
            layer = self.layer_stack.get_layer(index)
            if layer:
                layer.set_locked(checked)
                self._refresh_layer_list()

    def _add_new_layer(self):
        """Add a new layer"""
        if not self.layer_stack:
            return

        name, ok = QInputDialog.getText(self, "New Layer", "Layer name:")
        if ok and name:
            index = self.layer_stack.add_new_raster_layer(name)
            self.layer_stack.set_active_layer(index)

    def _delete_selected_layer(self):
        """Delete the selected layer"""
        if not self.layer_stack:
            return

        index = self._get_selected_layer_index()
        if index >= 0:
            self.layer_stack.remove_layer(index)

    def _duplicate_selected_layer(self):
        """Duplicate the selected layer"""
        if not self.layer_stack:
            return

        index = self._get_selected_layer_index()
        if index >= 0:
            self.layer_stack.duplicate_layer(index)

    def _group_selected_layers(self):
        """Group selected layers (placeholder)"""
        # TODO: Implement layer grouping
        pass

    def _move_layer_up(self):
        """Move selected layer up"""
        if not self.layer_stack:
            return

        index = self._get_selected_layer_index()
        if index > 0:
            self.layer_stack.move_layer(index, index - 1)

    def _move_layer_down(self):
        """Move selected layer down"""
        if not self.layer_stack:
            return

        index = self._get_selected_layer_index()
        if index >= 0 and index < self.layer_stack.get_layer_count() - 1:
            self.layer_stack.move_layer(index, index + 1)

    def _update_layer_properties(self, index: int):
        """Update the layer properties panel

        Args:
            index: Layer index
        """
        if not self.layer_stack:
            return

        layer = self.layer_stack.get_layer(index)
        if not layer:
            return

        self.updating_ui = True

        # Update opacity controls
        opacity_percent = int(layer.opacity * 100)
        self.opacity_slider.setValue(opacity_percent)
        self.opacity_spinbox.setValue(opacity_percent)

        # Update blend mode
        blend_mode = layer.blend_mode.capitalize()
        index = self.blend_mode_combo.findText(blend_mode)
        if index >= 0:
            self.blend_mode_combo.setCurrentIndex(index)

        # Update lock checkbox
        self.lock_checkbox.setChecked(layer.is_locked())

        self.updating_ui = False

    def _show_context_menu(self, position):
        """Show context menu for layers"""
        if not self.layer_tree.itemAt(position):
            return

        menu = QMenu(self)

        # Add actions
        duplicate_action = QAction("Duplicate Layer", self)
        duplicate_action.triggered.connect(self._duplicate_selected_layer)
        menu.addAction(duplicate_action)

        delete_action = QAction("Delete Layer", self)
        delete_action.triggered.connect(self._delete_selected_layer)
        menu.addAction(delete_action)

        menu.addSeparator()

        merge_down_action = QAction("Merge Down", self)
        merge_down_action.triggered.connect(self._merge_down)
        menu.addAction(merge_down_action)

        flatten_action = QAction("Flatten Image", self)
        flatten_action.triggered.connect(self._flatten_image)
        menu.addAction(flatten_action)

        menu.exec(self.layer_tree.mapToGlobal(position))

    def _merge_down(self):
        """Merge selected layer down"""
        if self.layer_stack:
            self.layer_stack.merge_down()

    def _flatten_image(self):
        """Flatten all layers"""
        if self.layer_stack:
            self.layer_stack.flatten()

    # Layer stack signal handlers
    def _on_layer_added(self, index: int, layer: BaseLayer):
        self._refresh_layer_list()

    def _on_layer_removed(self, index: int):
        self._refresh_layer_list()

    def _on_layer_moved(self, from_index: int, to_index: int):
        self._refresh_layer_list()

    def _on_active_layer_changed(self, index: int, layer: BaseLayer):
        if not self.updating_ui:
            # Select the layer in the tree
            for i in range(self.layer_tree.topLevelItemCount()):
                item = self.layer_tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == index:
                    self.layer_tree.setCurrentItem(item)
                    self._update_layer_properties(index)
                    break

    def _on_stack_changed(self):
        if not self.updating_ui:
            self._refresh_layer_list()