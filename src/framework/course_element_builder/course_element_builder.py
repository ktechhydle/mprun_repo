
from src.framework.course_element_builder.course_element_builder_graphics import *
from src.framework.course_element_builder.course_element_builder_items import *
from src.gui.custom_widgets import HorizontalSeparator, CustomIconWidget, ToolbarHorizontalLayout, \
    CustomColorDisplayButton, StrokeLabel, CustomColorPicker, CustomToolbar
from src.scripts.imports import *
from src.scripts.raw_functions import ItemStack


class CourseElementBuilderPanel(QWidget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.setMinimumHeight(400)
        self.properties_tab_layout = QVBoxLayout()
        self.setLayout(self.properties_tab_layout)

        self.scene = canvas
        self.parent = parent
        self.pen_color = ItemStack()
        self.brush_color = ItemStack()

        self.createUI()

    def createUI(self):
        self.selection_label = QLabel('No Selection')
        self.selection_label.setStyleSheet("QLabel { font-size: 12px; }")
        self.transform_separator = HorizontalSeparator()
        self.transform_label = QLabel('Transform', self)
        self.transform_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        self.transform_label.setAlignment(Qt.AlignLeft)
        appearence_label = QLabel('Appearance', self)
        appearence_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        appearence_label.setAlignment(Qt.AlignLeft)

        self.rotation_label = CustomIconWidget('', 'ui/Tool Icons/rotate_icon.png', 20, 20)
        self.rotation_label.setAlignment(Qt.AlignRight)
        self.rotation_label.setStyleSheet('font-size: 10px;')
        self.rotation_label.setContentsMargins(0, 0, 0, 0)

        self.x_pos_label = QLabel('X:')
        self.y_pos_label = QLabel('Y:')
        self.width_transform_label = QLabel('W:')
        self.height_transform_label = QLabel('H:')
        self.x_pos_spin = QSpinBox(self)
        self.x_pos_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.x_pos_spin.setFixedWidth(75)
        self.x_pos_spin.setMaximum(10000)
        self.x_pos_spin.setMinimum(-10000)
        self.x_pos_spin.setSuffix(' pt')
        self.x_pos_spin.setToolTip('Change the x position')
        self.y_pos_spin = QSpinBox(self)
        self.y_pos_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.y_pos_spin.setFixedWidth(75)
        self.y_pos_spin.setMaximum(10000)
        self.y_pos_spin.setMinimum(-10000)
        self.y_pos_spin.setSuffix(' pt')
        self.y_pos_spin.setToolTip('Change the y position')
        self.width_scale_spin = QDoubleSpinBox(self)
        self.width_scale_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.width_scale_spin.setFixedWidth(75)
        self.width_scale_spin.setValue(0.0)
        self.width_scale_spin.setDecimals(2)
        self.width_scale_spin.setRange(-10000.00, 10000.00)
        self.width_scale_spin.setSingleStep(1.0)
        self.width_scale_spin.setSuffix('%')
        self.width_scale_spin.setToolTip('Change the width')
        self.height_scale_spin = QDoubleSpinBox(self)
        self.height_scale_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.height_scale_spin.setFixedWidth(75)
        self.height_scale_spin.setValue(0.0)
        self.height_scale_spin.setDecimals(2)
        self.height_scale_spin.setRange(-10000.00, 10000.00)
        self.height_scale_spin.setSingleStep(1.0)
        self.height_scale_spin.setSuffix('%')
        self.height_scale_spin.setToolTip('Change the height')
        self.rotate_item_spin = QSpinBox(self)
        self.rotate_item_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.rotate_item_spin.setFixedWidth(65)
        self.rotate_item_spin.setRange(-360, 360)
        self.rotate_item_spin.setSuffix('°')
        self.rotate_item_spin.setToolTip('Change the rotation')
        self.flip_horizontal_btn = QPushButton(QIcon('ui/Tool Icons/flip_horizontal_icon.png'), '')
        self.flip_horizontal_btn.setToolTip('Flip horizontal')
        self.flip_horizontal_btn.setStyleSheet('border: none;')
        self.flip_horizontal_btn.clicked.connect(self.useFlipHorizontal)
        self.flip_vertical_btn = QPushButton(QIcon('ui/Tool Icons/flip_vertical_icon.png'), '')
        self.flip_vertical_btn.setToolTip('Flip vertical')
        self.flip_vertical_btn.setStyleSheet('border: none;')
        self.flip_vertical_btn.clicked.connect(self.useFlipVertical)
        widget7 = ToolbarHorizontalLayout()
        widget7.layout.addWidget(self.x_pos_label)
        widget7.layout.addWidget(self.x_pos_spin)
        widget7.layout.addWidget(self.width_transform_label)
        widget7.layout.addWidget(self.width_scale_spin)
        widget7.layout.addStretch()
        widget7.layout.addWidget(self.flip_horizontal_btn)
        widget8 = ToolbarHorizontalLayout()
        widget8.layout.addWidget(self.y_pos_label)
        widget8.layout.addWidget(self.y_pos_spin)
        widget8.layout.addWidget(self.height_transform_label)
        widget8.layout.addWidget(self.height_scale_spin)
        widget8.layout.addStretch()
        widget8.layout.addWidget(self.flip_vertical_btn)
        widget9 = ToolbarHorizontalLayout()
        widget9.layout.addWidget(self.rotation_label)
        widget9.layout.addWidget(self.rotate_item_spin)
        widget9.layout.addStretch()

        fill_label = QLabel('Fill')
        fill_label.setStyleSheet('color: white;')
        self.fill_color_btn = CustomColorDisplayButton(self)
        self.fill_color_btn.setFixedWidth(28)
        self.fill_color_btn.setFixedHeight(26)
        self.fill_color_btn.setToolTip('Change the fill color')
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+2'))
        self.fill_color_btn.clicked.connect(self.fillColorChooser)
        widget5 = ToolbarHorizontalLayout()
        widget5.layout.addWidget(self.fill_color_btn)
        widget5.layout.addWidget(fill_label)
        widget5.layout.setContentsMargins(0, 14, 0, 0)

        self.stroke_color_btn = CustomColorDisplayButton(self)
        self.stroke_color_btn.setFixedWidth(28)
        self.stroke_color_btn.setFixedHeight(26)
        self.stroke_color_btn.setToolTip('Change the stroke color')
        self.stroke_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.stroke_color_btn.clicked.connect(self.strokeColorChooser)
        self.stroke_size_spin = QSpinBox(self)
        self.stroke_size_spin.setValue(3)
        self.stroke_size_spin.setMaximum(1000)
        self.stroke_size_spin.setMinimum(1)
        self.stroke_size_spin.setSuffix(' pt')
        self.stroke_size_spin.setToolTip('Change the stroke width')
        stroke_label = StrokeLabel('Stroke', self)
        self.stroke_style_combo = stroke_label.stroke_combo
        self.stroke_style_options = stroke_label.stroke_options
        self.stroke_pencap_combo = stroke_label.pencap_combo
        self.stroke_pencap_options = stroke_label.pencap_options
        self.join_style_combo = stroke_label.join_style_combo
        self.join_style_options = stroke_label.join_style_options
        widget6 = ToolbarHorizontalLayout()
        widget6.layout.addWidget(self.stroke_color_btn)
        widget6.layout.addWidget(stroke_label)
        widget6.layout.addWidget(self.stroke_size_spin)
        widget6.layout.addSpacing(100)
        widget6.layout.setContentsMargins(0, 14, 0, 0)

        opacity_label = QLabel('Opacity')
        opacity_label.setStyleSheet('color: white;')
        self.opacity_btn = QPushButton('')
        self.opacity_btn.setFixedWidth(28)
        self.opacity_btn.setFixedHeight(26)
        self.opacity_btn.setIcon(QIcon('mprun_assets/assets/ui/panels/opacity_icon.png'))
        self.opacity_btn.setIconSize(QSize(24, 24))
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix('%')
        self.opacity_spin.setToolTip('Change the opacity')
        self.opacity_spin.valueChanged.connect(self.useChangeOpacity)
        opacity_hlayout = ToolbarHorizontalLayout()
        opacity_hlayout.layout.addWidget(self.opacity_btn)
        opacity_hlayout.layout.addWidget(opacity_label)
        opacity_hlayout.layout.addWidget(self.opacity_spin)
        opacity_hlayout.layout.addSpacing(100)
        opacity_hlayout.layout.setContentsMargins(0, 14, 0, 0)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.updateItemPen)
        self.stroke_style_combo.currentIndexChanged.connect(self.updateItemPen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.updateItemPen)
        self.join_style_combo.currentIndexChanged.connect(self.updateItemPen)
        self.x_pos_spin.valueChanged.connect(self.useSetItemPos)
        self.y_pos_spin.valueChanged.connect(self.useSetItemPos)
        self.width_scale_spin.valueChanged.connect(self.useScaleX)
        self.height_scale_spin.valueChanged.connect(self.useScaleY)
        self.rotate_item_spin.valueChanged.connect(self.useRotate)

        self.properties_tab_layout.addWidget(self.selection_label)
        self.properties_tab_layout.addWidget(self.transform_separator)
        self.properties_tab_layout.addWidget(self.transform_label)
        self.properties_tab_layout.addWidget(widget7)
        self.properties_tab_layout.addWidget(widget8)
        self.properties_tab_layout.addWidget(widget9)
        self.properties_tab_layout.addWidget(HorizontalSeparator())
        self.properties_tab_layout.addWidget(appearence_label)
        self.properties_tab_layout.addWidget(widget5)
        self.properties_tab_layout.addWidget(widget6)
        self.properties_tab_layout.addWidget(opacity_hlayout)
        self.properties_tab_layout.addStretch()

    def strokeColorChooser(self):
        color_dialog = CustomColorPicker(self.parent)
        color_dialog.setWindowTitle('Stroke Color')

        color_dialog.hex_spin.setText(QColor(self.pen_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.stroke_color_btn.setButtonColor(color.name())

            else:
                self.stroke_color_btn.setTransparent(True)

            self.pen_color.set(color.name() if color.alpha() != 0 else Qt.transparent)
            self.updateItemPen()

    def fillColorChooser(self):
        color_dialog = CustomColorPicker(self.parent)
        color_dialog.setWindowTitle('Fill Color')

        color_dialog.hex_spin.setText(QColor(self.brush_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.fill_color_btn.setButtonColor(color.name())

            else:
                self.fill_color_btn.setTransparent(True)

            self.brush_color.set(color.name() if color.alpha() != 0 else Qt.transparent)
            self.updateItemFill()

    def updateItemPen(self):
        pen = self.getPen()

        selected_items = self.scene.selectedItems()
        if selected_items:
            items = []
            old_pens = []
            for item in selected_items:
                items.append(item)
                old_pens.append(item.pen())

            if items:
                try:
                    command = PenChangeCommand(items, old_pens, pen)
                    self.scene.addCommand(command)
                except Exception as e:
                    print(f'Exception: {e}')

    def updateItemFill(self):
        brush = self.getBrush()

        selected_items = self.scene.selectedItems()
        if selected_items:
            items = []
            old_brushes = []
            for item in selected_items:
                items.append(item)
                old_brushes.append(item.brush())

            if items:
                try:
                    command = BrushChangeCommand(items, old_brushes, brush)
                    self.scene.addCommand(command)
                except Exception as e:
                    # Handle the exception (e.g., logging)
                    print(f'Exception: {e}')

    def getPen(self) -> QPen:
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        pen = QPen()
        pen.setColor(QColor(self.pen_color.get()))
        pen.setWidth(self.stroke_size_spin.value())
        pen.setJoinStyle(
            self.join_style_combo.itemData(self.join_style_combo.currentIndex()))
        pen.setStyle(data1)
        pen.setCapStyle(data2)

        return pen

    def getBrush(self) -> QBrush:
        return QBrush(QColor(self.brush_color.get()))
    
    def useScaleX(self, value):
        self.useScale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def useScaleY(self, value):
        self.useScale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def useScale(self, x_value, y_value):
        try:
            items = self.scene.selectedItems()

            old_transforms = []
            new_transforms = []

            for correct_item in items:
                # Get the center of the bounding box
                bounding_rect = correct_item.boundingRect()
                center_x = bounding_rect.center().x()
                center_y = bounding_rect.center().y()

                scale_x = x_value / 100
                scale_y = y_value / 100

                # Record the old transform and calculate the new one
                old_transforms.append(correct_item.transform())
                transform = QTransform()
                transform.translate(center_x, center_y)
                transform.scale(scale_x, scale_y)
                transform.translate(-center_x, -center_y)
                new_transforms.append(transform)

            # Create and add the command
            command = TransformCommand(items, old_transforms, new_transforms)
            self.scene.addCommand(command)

        except Exception as e:
            print(f'Error during scaling: {e}')
            
    def useSetItemPos(self):
        self.scene.blockSignals(True)
        try:
            # Get target position from spin boxes
            target_x = self.x_pos_spin.value()
            target_y = self.y_pos_spin.value()

            # Get the bounding rect of selected items
            items = [item for item in self.scene.selectedItems()]
            old_positions = []
            new_positions = []

            bounding_rect = self.scene.selectedItemsSceneBoundingRect()

            # Calculate the offset
            offset_x = target_x - bounding_rect.x()
            offset_y = target_y - bounding_rect.y()

            # Move each selected item by the offset and collect positions
            for item in items:
                old_pos = item.pos()
                new_pos = QPointF(item.x() + offset_x, item.y() + offset_y)
                old_positions.append(old_pos)
                new_positions.append(new_pos)

            # Create and execute the command with all items
            command = MultiItemPositionChangeCommand(None, items, old_positions, new_positions)
            self.scene.addCommand(command)

        finally:
            self.scene.blockSignals(False)

    def useRotate(self, value):
        items = self.scene.selectedItems()
        old_rotations = []

        # Rotate each item around the center
        for item in items:
            old_rotations.append(item.rotation())
            item.setTransformOriginPoint(item.boundingRect().center())

        if items:
            command = RotateCommand(None, items, old_rotations, value)
            self.scene.addCommand(command)

    def useFlipHorizontal(self):
        self.width_scale_spin.setValue(-self.width_scale_spin.value())

    def useFlipVertical(self):
        self.height_scale_spin.setValue(-self.height_scale_spin.value())

    def useChangeOpacity(self, value):
        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.opacity_spin.maximum()

        items = self.scene.selectedItems()
        if not items:
            return

        canvas_items = []
        old_opacities = []

        # Apply the effect to selected items
        for item in items:
            canvas_items.append(item)
            old_opacities.append(item.opacity())

        if canvas_items:
            command = OpacityCommand(canvas_items, old_opacities, opacity)
            self.scene.addCommand(command)

    def default(self):
        self.stroke_color_btn.setButtonColor('#000000')
        self.fill_color_btn.setButtonColor('transparent')
        self.pen_color.set('#000000')
        self.brush_color.set('transparent')
        self.updateItemPen()
        self.updateItemFill()


class CourseElementBuilder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('mprun_assets/assets/logos/mprun_icon.png'))
        self.setWindowTitle('Course Elements Builder')
        self.setLayout(QHBoxLayout())

        self.createUi()
        self.createToolBar()
        self.createToolBarActions()
        self.createActions()

    def createUi(self):
        self.scene = CourseElementBuilderScene()
        self.scene.selectionChanged.connect(self.updateTransformUI)
        self.scene.selectionChanged.connect(self.updateAppearanceUI)
        self.view = CourseElementBuilderView(self.scene, self)

        self.properties_tab = CourseElementBuilderPanel(self.scene, self)
        self.properties_tab.setFixedWidth(280)
        self.properties_tab.default()

        self.layout().addWidget(self.view)
        self.layout().addWidget(self.properties_tab)
        self.updateTransformUI()
        self.updateAppearanceUI()

    def createToolBar(self):
        self.toolbar = CustomToolbar('ToolBar')
        self.toolbar.setParent(self.view)
        self.toolbar.setObjectName('customToolBar')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.setFloatable(True)
        self.toolbar.move(11, 11)

    def createToolBarActions(self):
        self.action_group = QActionGroup(self)

        self.select_btn = QAction(QIcon('mprun_assets/assets/tools/selection_icon.png'), 'Select Tool (Spacebar)', self)
        self.select_btn.setToolTip(
            '<b>Select (Spacebar)</b><br>'
            'Select items on the scene by clicking and dragging a selection rectangle.<br>'
            '<hr>'
            '<i>Press F1 for more help.</i>'
        )
        self.select_btn.setShortcut(QKeySequence(Qt.Key.Key_Space))
        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.triggered.connect(self.useSelect)

        # Pan Button
        self.pan_btn = QAction(QIcon('mprun_assets/assets/tools/pan_icon.png'), 'Pan Tool (P)', self)
        self.pan_btn.setToolTip(
            '<b>Pan (P)</b><br>'
            'Pan around the scene by clicking and dragging.<br>'
            '<hr>'
            '<i>Press F1 for more help.</i>'
        )
        self.pan_btn.setShortcut(QKeySequence('P'))
        self.pan_btn.setCheckable(True)
        self.pan_btn.triggered.connect(self.usePan)

        self.lip_btn = QAction(QIcon('mprun_assets/assets/tools/pan_icon.png'), 'Lip Tool (L)', self)
        self.lip_btn.setToolTip(
            '<b>Lip (L)</b><br>'
            'Draw lips on to features.<br>'
            '<hr>'
            '<i>Press F1 for more help.</i>'
        )
        self.lip_btn.setShortcut(QKeySequence('L'))
        self.lip_btn.setCheckable(True)

        self.line_btn = QAction(QIcon('mprun_assets/assets/tools/pan_icon.png'), 'Line Tool (Ctrl+L)', self)
        self.line_btn.setToolTip(
            '<b>Line (Ctrl+L)</b><br>'
            'Draw line elements for features.<br>'
            '<hr>'
            '<i>Press F1 for more help.</i>'
        )
        self.line_btn.setShortcut(QKeySequence('Ctrl+L'))
        self.line_btn.setCheckable(True)

        self.arc_btn = QAction(QIcon('mprun_assets/assets/tools/pan_icon.png'), 'Arc Tool (A)', self)
        self.arc_btn.setToolTip(
            '<b>Arc (A)</b><br>'
            'Draw arc elements for features.<br>'
            '<hr>'
            '<i>Press F1 for more help.</i>'
        )
        self.arc_btn.setShortcut(QKeySequence('A'))
        self.arc_btn.setCheckable(True)

        self.toolbar.addAction(self.select_btn)
        self.toolbar.addAction(self.pan_btn)
        self.toolbar.addAction(self.lip_btn)
        self.toolbar.addAction(self.line_btn)
        self.toolbar.addAction(self.arc_btn)

        self.action_group.addAction(self.select_btn)
        self.action_group.addAction(self.pan_btn)
        self.action_group.addAction(self.lip_btn)
        self.action_group.addAction(self.line_btn)
        self.action_group.addAction(self.arc_btn)

        self.select_btn.trigger()

    def createActions(self):
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.scene.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Shift+Z'))
        redo_action.triggered.connect(self.scene.redo)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence('Ctrl+C'))
        copy_action.triggered.connect(self.scene.copy)

        cut_action = QAction('Cut', self)
        cut_action.setShortcut(QKeySequence('Ctrl+X'))
        cut_action.triggered.connect(self.scene.cut)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence('Ctrl+V'))
        paste_action.triggered.connect(self.scene.paste)

        duplicate_action = QAction('Duplicate', self)
        duplicate_action.setShortcut(QKeySequence('D'))
        duplicate_action.triggered.connect(self.scene.duplicate)

        delete_action = QAction('Delete', self)
        delete_action.setShortcut(QKeySequence('Backspace'))
        delete_action.triggered.connect(self.useDelete)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        exit_action.triggered.connect(self.view.escape)

        help_action = QAction('Help', self)
        help_action.setShortcut(Qt.Key_F1)
        help_action.triggered.connect(lambda: self.parent().show_help)

        self.addAction(undo_action)
        self.addAction(redo_action)
        self.addAction(copy_action)
        self.addAction(cut_action)
        self.addAction(paste_action)
        self.addAction(duplicate_action)
        self.addAction(delete_action)
        self.addAction(exit_action)
        self.addAction(help_action)

    def setPropertiesTabEnabled(self, enabled: bool):
        self.properties_tab.transform_separator.setHidden(enabled)
        self.properties_tab.transform_label.setHidden(enabled)
        self.properties_tab.x_pos_label.setHidden(enabled)
        self.properties_tab.x_pos_spin.setHidden(enabled)
        self.properties_tab.y_pos_label.setHidden(enabled)
        self.properties_tab.y_pos_spin.setHidden(enabled)
        self.properties_tab.width_transform_label.setHidden(enabled)
        self.properties_tab.height_transform_label.setHidden(enabled)
        self.properties_tab.width_scale_spin.setHidden(enabled)
        self.properties_tab.height_scale_spin.setHidden(enabled)
        self.properties_tab.flip_horizontal_btn.setHidden(enabled)
        self.properties_tab.flip_vertical_btn.setHidden(enabled)
        self.properties_tab.rotation_label.setHidden(enabled)
        self.properties_tab.rotate_item_spin.setHidden(enabled)

        if enabled is True:
            self.properties_tab.selection_label.setText('No Selection')
            self.properties_tab.x_pos_spin.setValue(0)
            self.properties_tab.y_pos_spin.setValue(0)
            self.properties_tab.rotate_item_spin.setValue(0)
            self.properties_tab.opacity_spin.setValue(100)
            self.properties_tab.width_scale_spin.setValue(0.0)
            self.properties_tab.height_scale_spin.setValue(0.0)

    def updateTransformUI(self):
        # Block signals for all spinboxes at once
        spinboxes = [self.properties_tab.x_pos_spin, self.properties_tab.y_pos_spin,
                     self.properties_tab.width_scale_spin, self.properties_tab.height_scale_spin,
                     self.properties_tab.rotate_item_spin, self.properties_tab.opacity_spin]
        for spinbox in spinboxes:
            spinbox.blockSignals(True)

        selected_items = self.scene.selectedItems()

        if selected_items:
            self.setPropertiesTabEnabled(False)
            first_item = selected_items[0]

            # Update based on first item only
            self.properties_tab.x_pos_spin.setValue(int(first_item.sceneBoundingRect().x()))
            self.properties_tab.y_pos_spin.setValue(int(first_item.sceneBoundingRect().y()))
            self.properties_tab.rotate_item_spin.setValue(int(first_item.rotation()))
            self.properties_tab.opacity_spin.setValue(int(first_item.opacity() * 100))
            self.properties_tab.width_scale_spin.setValue(first_item.transform().m11() * 100)
            self.properties_tab.height_scale_spin.setValue(first_item.transform().m22() * 100)

            # Update label based on selection count
            if len(selected_items) > 1:
                self.properties_tab.selection_label.setText(f'Combined Selection ({len(selected_items)} Items)')
                bounding_rect = self.scene.selectedItemsSceneBoundingRect()
                self.properties_tab.x_pos_spin.setValue(int(bounding_rect.x()))
                self.properties_tab.y_pos_spin.setValue(int(bounding_rect.y()))
            else:
                self.properties_tab.selection_label.setText(first_item.toolTip())

        else:
            self.setPropertiesTabEnabled(True)

        # Unblock signals for all spinboxes at once
        for spinbox in spinboxes:
            spinbox.blockSignals(False)

    def updateAppearanceUI(self):
        # Widgets to block/unblock signals for canvas and properties
        signal_block_widgets = [
            self.properties_tab.stroke_size_spin, self.properties_tab.stroke_style_combo,
            self.properties_tab.stroke_pencap_combo, self.properties_tab.join_style_combo,
            self.properties_tab.fill_color_btn, self.properties_tab.stroke_color_btn,
        ]

        # Block signals for all relevant widgets
        for widget in signal_block_widgets:
            widget.blockSignals(True)

        try:
            def set_color(btn, color, color_attr):
                if color.alpha() != 0:
                    btn.setButtonColor(color.name())
                    color_attr.set(color.name())
                else:
                    btn.setTransparent(True)
                    color_attr.set(Qt.transparent)

            for item in self.scene.selectedItems():
                pen, brush = item.pen(), item.brush()

                set_color(self.properties_tab.stroke_color_btn, pen.color(), self.properties_tab.pen_color)
                set_color(self.properties_tab.fill_color_btn, brush.color(), self.properties_tab.brush_color)

                # Set Values for pen-related attributes
                self.properties_tab.stroke_size_spin.setValue(pen.width())

                # Common update functions to avoid redundancy
                def update_combo(combo, options, target_value):
                    for idx, (key, value) in enumerate(options.items()):
                        if target_value == value:
                            combo.setCurrentIndex(idx)
                            break

                update_combo(self.properties_tab.stroke_style_combo, self.properties_tab.stroke_style_options,
                             pen.style())
                update_combo(self.properties_tab.stroke_pencap_combo, self.properties_tab.stroke_pencap_options,
                             pen.capStyle())
                update_combo(self.properties_tab.join_style_combo, self.properties_tab.join_style_options,
                             pen.joinStyle())

        except Exception as e:
            print(e)

        # Unblock signals for all relevant widgets
        for widget in signal_block_widgets:
            widget.blockSignals(False)

    def useSelect(self):
        self.select_btn.setChecked(True)
        self.view.enableItemFlags()
        self.view.setDragMode(QGraphicsView.RubberBandDrag)

    def usePan(self):
        self.pan_btn.setChecked(True)

    def useDelete(self):
        items = [item for item in self.scene.selectedItems()]

        if items:
            command = RemoveItemCommand(self.scene, items)
            self.scene.addCommand(command)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = CourseElementBuilder()
    window.show()

    sys.exit(app.exec_())
