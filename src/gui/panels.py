import mprun.gui
import mprun.types
import re
from src.scripts.imports import *
from src.framework.items import *
from src.gui.custom_widgets import StrokeLabel

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class PropertiesPanel(mprun.gui.base_widget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.setMinimumHeight(400)
        self.properties_tab_layout = QVBoxLayout()
        self.setLayout(self.properties_tab_layout)

        self.canvas = canvas
        self.parent = parent
        self.pen_color = mprun.types.item_stack()
        self.brush_color = mprun.types.item_stack()

        self.createUI()

    def createUI(self):
        self.selection_label = QLabel('No Selection')
        self.selection_label.setStyleSheet("QLabel { font-size: 12px; }")
        self.transform_separator = mprun.gui.horizontal_splitter()
        self.transform_label = QLabel('Transform', self)
        self.transform_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        self.transform_label.setAlignment(Qt.AlignLeft)
        appearence_label = QLabel('Appearance', self)
        appearence_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        appearence_label.setAlignment(Qt.AlignLeft)

        self.rotation_label = mprun.gui.icon_label('', 'mprun_assets/assets/tools/rotate_icon.png', 15, 15)
        self.rotation_label.setStyleSheet('font-size: 10px;')
        self.rotation_label.setContentsMargins(0, 0, 0, 0)

        self.scale_label = mprun.gui.icon_label('', 'mprun_assets/assets/tools/scale_icon.png', 20, 20)
        self.scale_label.setStyleSheet('font-size: 10px;')
        self.scale_label.setContentsMargins(0, 0, 0, 0)

        self.x_pos_label = QLabel('X:')
        self.y_pos_label = QLabel('Y:')
        self.width_transform_label = QLabel('W:')
        self.height_transform_label = QLabel('H:')
        self.x_pos_spin = QSpinBox(self)
        self.x_pos_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.x_pos_spin.setMaximum(10000)
        self.x_pos_spin.setMinimum(-10000)
        self.x_pos_spin.setSuffix(' pt')
        self.x_pos_spin.setToolTip('Change the x position')
        self.y_pos_spin = QSpinBox(self)
        self.y_pos_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.y_pos_spin.setMaximum(10000)
        self.y_pos_spin.setMinimum(-10000)
        self.y_pos_spin.setSuffix(' pt')
        self.y_pos_spin.setToolTip('Change the y position')
        self.rotate_item_spin = QSpinBox(self)
        self.rotate_item_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.rotate_item_spin.setRange(-360, 360)
        self.rotate_item_spin.setSuffix('°')
        self.rotate_item_spin.setToolTip('Change the rotation')
        self.rotate_item_spin.setMinimumWidth(90)
        self.scale_item_spin = QSpinBox(self)
        self.scale_item_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.scale_item_spin.setRange(-10000, 10000)
        self.scale_item_spin.setSuffix('%')
        self.scale_item_spin.setToolTip('Change the scale')
        self.scale_item_spin.setMinimumWidth(90)
        self.transform_grid_layout = QGridLayout()
        self.transform_grid_layout.setVerticalSpacing(20)
        self.transform_grid_layout.addWidget(self.x_pos_label, 0, 0)
        self.transform_grid_layout.addWidget(self.x_pos_spin, 0, 1)
        self.transform_grid_layout.addWidget(self.y_pos_label, 0, 2)
        self.transform_grid_layout.addWidget(self.y_pos_spin, 0, 3)
        self.transform_grid_layout.addWidget(self.rotation_label, 1, 0)
        self.transform_grid_layout.addWidget(self.rotate_item_spin, 1, 1)
        self.transform_grid_layout.addWidget(self.scale_label, 1, 2)
        self.transform_grid_layout.addWidget(self.scale_item_spin, 1, 3)

        fill_label = QLabel('Fill')
        fill_label.setStyleSheet('color: white;')
        self.fill_color_btn = mprun.gui.color_picking_button(self)
        self.fill_color_btn.setFixedWidth(28)
        self.fill_color_btn.setFixedHeight(26)
        self.fill_color_btn.setToolTip('Change the fill color')
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+2'))
        self.fill_color_btn.clicked.connect(self.fillColorChooser)
        widget5 = mprun.gui.horizontal_layout()
        widget5.layout().addWidget(self.fill_color_btn)
        widget5.layout().addWidget(fill_label)
        widget5.layout().setContentsMargins(0, 14, 0, 0)

        self.stroke_color_btn = mprun.gui.color_picking_button(self)
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
        widget6 = mprun.gui.horizontal_layout()
        widget6.layout().addWidget(self.stroke_color_btn)
        widget6.layout().addWidget(stroke_label)
        widget6.layout().addWidget(self.stroke_size_spin)
        widget6.layout().addSpacing(100)
        widget6.layout().setContentsMargins(0, 14, 0, 0)

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
        opacity_hlayout = mprun.gui.horizontal_layout()
        opacity_hlayout.layout().addWidget(self.opacity_btn)
        opacity_hlayout.layout().addWidget(opacity_label)
        opacity_hlayout.layout().addWidget(self.opacity_spin)
        opacity_hlayout.layout().addSpacing(100)
        opacity_hlayout.layout().setContentsMargins(0, 14, 0, 0)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.updateItemPen)
        self.stroke_style_combo.currentIndexChanged.connect(self.updateItemPen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.updateItemPen)
        self.join_style_combo.currentIndexChanged.connect(self.updateItemPen)
        self.x_pos_spin.valueChanged.connect(self.useSetItemPos)
        self.y_pos_spin.valueChanged.connect(self.useSetItemPos)
        self.rotate_item_spin.valueChanged.connect(self.useRotate)
        self.scale_item_spin.valueChanged.connect(self.useScale)

        self.properties_tab_layout.addWidget(self.selection_label)
        self.properties_tab_layout.addWidget(self.transform_separator)
        self.properties_tab_layout.addWidget(self.transform_label)
        self.properties_tab_layout.addSpacing(20)
        self.properties_tab_layout.addLayout(self.transform_grid_layout)
        self.properties_tab_layout.addSpacing(20)
        self.properties_tab_layout.addWidget(mprun.gui.horizontal_splitter())
        self.properties_tab_layout.addWidget(appearence_label)
        self.properties_tab_layout.addWidget(widget5)
        self.properties_tab_layout.addWidget(widget6)
        self.properties_tab_layout.addWidget(opacity_hlayout)
        self.properties_tab_layout.addStretch()

    def strokeColorChooser(self):
        color_dialog = mprun.gui.color_picker(self.parent)
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
        color_dialog = mprun.gui.color_picker(self.parent)
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

        selected_items = self.canvas.selectedItems()
        if selected_items:
            items = []
            old_pens = []
            for item in selected_items:
                if isinstance(item, (CustomPathItem, LeaderLineItem)):
                    items.append(item)
                    old_pens.append(item.pen())

            if items:
                try:
                    command = PenChangeCommand(items, old_pens, pen)
                    self.canvas.addCommand(command)
                except Exception as e:
                    print(f'Exception: {e}')

        self.parent.canvas_view.update()

    def updateItemFill(self):
        brush = self.getBrush()

        selected_items = self.canvas.selectedItems()
        if selected_items:
            items = []
            old_brushes = []
            for item in selected_items:
                if isinstance(item, (CustomPathItem, LeaderLineItem)):
                    items.append(item)
                    old_brushes.append(item.brush())

            if items:
                try:
                    command = BrushChangeCommand(items, old_brushes, brush)
                    self.canvas.addCommand(command)
                except Exception as e:
                    # Handle the exception (e.g., logging)
                    print(f'Exception: {e}')

        self.parent.canvas_view.update()

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

    def useRotate(self, value):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        old_rotations = []

        # Rotate each item around the center
        for item in items:
            if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                if item.parentItem().isSelected():
                    items.remove(item)

            item.setTransformOriginPoint(item.boundingRect().center())
            old_rotations.append(item.rotation())

        if items:
            command = RotateCommand(self, items, old_rotations, value)
            self.canvas.addCommand(command)

    def useScale(self, value):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        old_scales = []

        # Rotate each item around the center
        for item in items:
            if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                if item.parentItem().isSelected():
                    items.remove(item)

            item.setTransformOriginPoint(item.boundingRect().center())
            old_scales.append(item.scale())

        if items:
            self.canvas.addCommand(ScaleMultipleCommand(items, old_scales, value / 100))

    def useSetItemPos(self):
        self.canvas.blockSignals(True)
        try:
            # Get target position from spin boxes
            target_x = self.x_pos_spin.value()
            target_y = self.y_pos_spin.value()

            # Get the bounding rect of selected items
            items = [item for item in self.canvas.selectedItems()]
            old_positions = []
            new_positions = []

            bounding_rect = self.canvas.selectedItemsSceneBoundingRect()

            # Calculate the offset
            offset_x = target_x - bounding_rect.x()
            offset_y = target_y - bounding_rect.y()

            # Move each selected item by the offset and collect positions
            for item in items:
                if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                    if item.parentItem().isSelected():
                        items.remove(item)

                old_pos = item.pos()
                new_pos = QPointF(item.x() + offset_x, item.y() + offset_y)
                old_positions.append(old_pos)
                new_positions.append(new_pos)

            # Create and execute the command with all items
            command = MultiItemPositionChangeCommand(self, items, old_positions, new_positions)
            self.canvas.addCommand(command)

        finally:
            self.canvas.blockSignals(False)

    def useChangeOpacity(self, value):
        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.opacity_spin.maximum()

        items = self.canvas.selectedItems()
        if not items:
            return

        canvas_items = []
        old_opacities = []

        # Apply the effect to selected items
        for item in items:
            if not isinstance(item, CanvasItem):
                canvas_items.append(item)
                old_opacities.append(item.opacity())

        if canvas_items:
            try:
                command = OpacityCommand(canvas_items, old_opacities, opacity)
                self.canvas.addCommand(command)
            except Exception as e:
                # Handle the exception (e.g., logging)
                print(f'Exception: {e}')

    def updateTransformUi(self):
        # Block signals for all spinboxes at once
        spinboxes = [self.x_pos_spin, self.y_pos_spin,
                     self.rotate_item_spin, self.opacity_spin, self.scale_item_spin]
        for spinbox in spinboxes:
            spinbox.blockSignals(True)

        selected_items = self.canvas.selectedItems()

        if selected_items:
            self.setPropertiesTabEnabled(False)
            first_item = selected_items[0]

            # Update based on first item only
            self.x_pos_spin.setValue(int(first_item.sceneBoundingRect().x()))
            self.y_pos_spin.setValue(int(first_item.sceneBoundingRect().y()))
            self.rotate_item_spin.setValue(int(first_item.rotation()))
            self.scale_item_spin.setValue(int(first_item.scale() * 100))
            self.opacity_spin.setValue(int(first_item.opacity() * 100))

            # Update label based on selection count
            if len(selected_items) > 1:
                self.selection_label.setText(f'Combined Selection ({len(selected_items)} Items)')
                bounding_rect = self.canvas.selectedItemsSceneBoundingRect()
                self.x_pos_spin.setValue(int(bounding_rect.x()))
                self.y_pos_spin.setValue(int(bounding_rect.y()))
            else:
                self.selection_label.setText(first_item.toolTip())

        else:
            self.setPropertiesTabEnabled(True)

        # Unblock signals for all spinboxes at once
        for spinbox in spinboxes:
            spinbox.blockSignals(False)

    def setPropertiesTabEnabled(self, enabled: bool):
        self.transform_separator.setHidden(enabled)
        self.transform_label.setHidden(enabled)
        self.x_pos_label.setHidden(enabled)
        self.x_pos_spin.setHidden(enabled)
        self.y_pos_label.setHidden(enabled)
        self.y_pos_spin.setHidden(enabled)
        self.rotation_label.setHidden(enabled)
        self.rotate_item_spin.setHidden(enabled)
        self.scale_label.setHidden(enabled)
        self.scale_item_spin.setHidden(enabled)

        if enabled is True:
            self.selection_label.setText('No Selection')
            self.x_pos_spin.setValue(0)
            self.y_pos_spin.setValue(0)
            self.rotate_item_spin.setValue(0)
            self.scale_item_spin.setValue(100)
            self.opacity_spin.setValue(100)

    def default(self):
        self.stroke_color_btn.setButtonColor(self.pen_color.get())
        self.fill_color_btn.setButtonColor(self.brush_color.get())


class LibrariesPanel(mprun.gui.base_widget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName('customScrollArea')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self)

        self.current_folder_path = ""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.canvas = canvas

        self.createUI()

    def createUI(self):
        # List widget for the library
        self.library_list_widget = mprun.gui.library_list(self.canvas)
        self.library_list_widget.setStyleSheet('border: none')
        self.library_list_widget.setIconSize(QSize(80, 80))

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setToolTip('Search for specific features')
        self.search_bar.setPlaceholderText('Search Features...')
        self.search_bar.setObjectName('modernLineEdit')
        self.search_bar.textChanged.connect(self.filterLibrary)

        library_btn_hlayout = QHBoxLayout()

        search_hlayout = QHBoxLayout()
        search_hlayout.addWidget(self.search_bar)

        self.layout.addLayout(library_btn_hlayout)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.library_list_widget)

        self.loadLibrary(os.path.abspath('course elements'))

    def reloadLibrary(self):
        if self.current_folder_path:
            self.loadLibrary(self.current_folder_path)

    def loadLibrary(self, folder_path):
        # Clear existing items in the list widget
        self.library_list_widget.clear()
        self.library_list_widget.all_items = []
        self.current_folder_path = folder_path

        # List all SVG files in the selected folder (now supports pixmap as well)
        svg_files = [f for f in os.listdir(folder_path) if f.endswith(('.svg', '.png', '.jpg', '.jpeg'))]

        # Check if no files are found
        if not svg_files:
            self.library_list_widget.setDragEnabled(False)
            list_item = QListWidgetItem('No files found')
            self.library_list_widget.addItem(list_item)

        else:
            self.library_list_widget.setDragEnabled(True)

            for svg_file in svg_files:
                display_name = re.sub(r'\.svg|\.png|\.jpg|\.jpeg', '', svg_file)
                list_item = QListWidgetItem(display_name)
                list_item.setData(Qt.UserRole, os.path.join(folder_path, svg_file))
                list_item.setIcon(QIcon(os.path.join(folder_path, svg_file)))
                list_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
                list_item.setToolTip(f'<h2>{svg_file.split('.')[0]}</h2>'
                                     f'<i>Simply drag and drop this item to add it to the scene.</i><br><br>'
                                     f'<img src="{os.path.join(folder_path, svg_file)}">')
                self.library_list_widget.addItem(list_item)
                self.library_list_widget.all_items.append(list_item)

        self.library_list_widget.setDisplaySize(self.library_list_widget.currentDisplaySize())

    def filterLibrary(self, text):
        try:
            self.library_list_widget.filterItems(text)

        except Exception as e:
            print(e)

    def items(self):
        l = []

        for row in range(self.library_list_widget.count()):
            item = self.library_list_widget.item(row)
            l.append(item.text())

        return l if l else ''


class CharactersPanel(mprun.gui.base_widget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.characters_tab_layout = QVBoxLayout()
        self.setLayout(self.characters_tab_layout)

        self.canvas = canvas
        self.parent = parent
        self.font_color = mprun.types.item_stack()

        self.createUI()

    def createUI(self):
        # _____ Characters tab widgets _____
        self.font_choice_combo = QFontComboBox(self)
        self.font_choice_combo.setCurrentText('Arial')
        self.font_choice_combo.setToolTip('Change the font style')
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setValue(20)
        self.font_size_spin.setMaximum(1000)
        self.font_size_spin.setMinimum(1)
        self.font_size_spin.setFixedWidth(90)
        self.font_size_spin.setSuffix(' pt')
        self.font_size_spin.setToolTip('Change the font size')
        self.font_letter_spacing_spin = QSpinBox(self)
        self.font_letter_spacing_spin.setValue(1)
        self.font_letter_spacing_spin.setMaximum(1000)
        self.font_letter_spacing_spin.setMinimum(-100)
        self.font_letter_spacing_spin.setFixedWidth(105)
        self.font_letter_spacing_spin.setSuffix(' pt')
        self.font_letter_spacing_spin.setToolTip('Change the font letter spacing')

        self.font_color_btn = mprun.gui.color_picking_button(self)
        self.font_color_btn.setFixedWidth(81)
        self.font_color_btn.setToolTip('Change the font color')
        self.font_color_btn.clicked.connect(self.fontColorChooser)

        self.alignleft_btn = QPushButton('', self.parent)
        self.alignleft_btn.setIcon(QIcon('mprun_assets/assets/ui/panels/align_text_left.svg'))
        self.alignleft_btn.setToolTip('Align the text to the left')
        self.alignleft_btn.setCheckable(True)
        self.alignleft_btn.setChecked(True)
        self.alignleft_btn.stored_align = Qt.AlignmentFlag.AlignLeft

        self.alignmiddle_btn = QPushButton('', self.parent)
        self.alignmiddle_btn.setIcon(QIcon('mprun_assets/assets/ui/panels/align_text_middle.svg'))
        self.alignmiddle_btn.setToolTip('Align the text to the middle')
        self.alignmiddle_btn.setCheckable(True)
        self.alignmiddle_btn.stored_align = Qt.AlignmentFlag.AlignCenter

        self.alignright_btn = QPushButton('', self.parent)
        self.alignright_btn.setIcon(QIcon('mprun_assets/assets/ui/panels/align_text_right.svg'))
        self.alignright_btn.setToolTip('Align the text to the right')
        self.alignright_btn.setCheckable(True)
        self.alignright_btn.stored_align = Qt.AlignmentFlag.AlignRight

        self.alignleft_btn.clicked.connect(self.updateItemFont)
        self.alignmiddle_btn.clicked.connect(self.updateItemFont)
        self.alignright_btn.clicked.connect(self.updateItemFont)

        self.alignment_group = QButtonGroup(self.parent)
        self.alignment_group.addButton(self.alignleft_btn)
        self.alignment_group.addButton(self.alignmiddle_btn)
        self.alignment_group.addButton(self.alignright_btn)

        font_alignment_layout = mprun.gui.horizontal_layout()
        font_alignment_layout.layout().setContentsMargins(0, 0, 0, 0)
        font_alignment_layout.layout().addWidget(self.alignleft_btn)
        font_alignment_layout.layout().addWidget(self.alignmiddle_btn)
        font_alignment_layout.layout().addWidget(self.alignright_btn)

        self.bold_btn = QPushButton('B', self.parent)
        self.bold_btn.setToolTip('Set the font bold')
        self.bold_btn.setStyleSheet('font-weight: bold; font-size: 15px;')
        self.italic_btn = QPushButton('I', self.parent)
        self.italic_btn.setToolTip('Set the font italic')
        self.italic_btn.setStyleSheet('font-style: italic; font-size: 15px;')
        self.underline_btn = QPushButton('U', self.parent)
        self.underline_btn.setToolTip('Set the font underlined')
        self.underline_btn.setStyleSheet('text-decoration: underline; font-size: 15px;')
        self.bold_btn.setCheckable(True)
        self.italic_btn.setCheckable(True)
        self.underline_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.updateItemFont)
        self.italic_btn.clicked.connect(self.updateItemFont)
        self.underline_btn.clicked.connect(self.updateItemFont)
        font_size_and_spacing_hlayout = mprun.gui.horizontal_layout()
        font_size_and_spacing_hlayout.layout().addWidget(
            mprun.gui.icon_label('', 'mprun_assets/assets/ui/panels/font_size_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout().addWidget(self.font_size_spin)
        font_size_and_spacing_hlayout.layout().addWidget(
            mprun.gui.icon_label('', 'mprun_assets/assets/ui/panels/font_spacing_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout().addWidget(self.font_letter_spacing_spin)
        font_size_and_spacing_hlayout.layout().addStretch()
        font_size_and_spacing_hlayout.layout().setContentsMargins(0, 0, 0, 0)

        font_style_hlayout = mprun.gui.horizontal_layout()
        font_style_hlayout.layout().addWidget(self.bold_btn)
        font_style_hlayout.layout().addWidget(self.italic_btn)
        font_style_hlayout.layout().addWidget(self.underline_btn)
        font_style_hlayout.layout().setContentsMargins(0, 0, 0, 0)

        font_color_hlayout = mprun.gui.horizontal_layout()
        font_color_hlayout.layout().setContentsMargins(0, 0, 0, 0)
        font_color_hlayout.layout().addStretch()
        font_color_hlayout.layout().addWidget(QLabel('Color:'))
        font_color_hlayout.layout().addWidget(self.font_color_btn)

        self.font_size_spin.valueChanged.connect(self.updateItemFont)
        self.font_letter_spacing_spin.valueChanged.connect(self.updateItemFont)
        self.font_choice_combo.currentFontChanged.connect(self.updateItemFont)
        self.font_choice_combo.currentTextChanged.connect(self.updateItemFont)

        self.characters_tab_layout.addWidget(self.font_choice_combo)
        self.characters_tab_layout.addWidget(font_size_and_spacing_hlayout)
        self.characters_tab_layout.addWidget(font_alignment_layout)
        self.characters_tab_layout.addWidget(font_style_hlayout)
        self.characters_tab_layout.addSpacing(20)
        self.characters_tab_layout.addWidget(font_color_hlayout)

    def fontColorChooser(self):
        color_dialog = mprun.gui.color_picker(self.parent)
        color_dialog.setWindowTitle('Font Color')

        color_dialog.hex_spin.setText(QColor(self.font_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.font_color_btn.setButtonColor(color.name())

            else:
                self.font_color_btn.setTransparent(True)

            self.font_color.set(color.name() if color.alpha() != 0 else Qt.transparent)
            self.updateItemFont()

    def updateItemFont(self):
        # Update font
        font = self.getFont()
        new_color = QColor(self.font_color.get())
        alignment_option = self.getFontAlignment()

        selected_items = self.canvas.selectedItems()
        if selected_items:
            items = []
            old_fonts = []
            old_colors = []
            old_alignment_options = []
            for item in selected_items:
                if isinstance(item, CustomTextItem):
                    items.append(item)
                    old_fonts.append(item.font())
                    old_colors.append(item.defaultTextColor())
                    old_alignment_options.append(item.textAlignment())

            if items:
                command = FontChangeCommand(items, old_fonts, font, old_colors, new_color,
                                            old_alignment_options, alignment_option)
                self.canvas.addCommand(command)
                for item in items:
                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

    def getFont(self):
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.font_letter_spacing_spin.value())
        font.setBold(True if self.bold_btn.isChecked() else False)
        font.setItalic(True if self.italic_btn.isChecked() else False)
        font.setUnderline(True if self.underline_btn.isChecked() else False)
        return font

    def getFontColor(self):
        return QColor(self.font_color.get())

    def getFontAlignment(self):
        for button in self.alignment_group.buttons():
            if button.isChecked():
                return button.stored_align

    def default(self):
        self.font_color_btn.setButtonColor(self.font_color.get())


class CanvasEditorPanel(mprun.gui.base_widget):
    def __init__(self, canvas):
        super().__init__()
        self.setFixedHeight(185)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.canvas = canvas
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.createUI()

    def createUI(self):
        canvas_x_size_label = QLabel('W:')
        canvas_y_size_label = QLabel('H:')
        canvas_preset_label = QLabel('Preset:')
        canvas_name_label = QLabel('Name:')
        self.canvas_x_entry = QSpinBox(self)
        self.canvas_x_entry.setMaximum(5000)
        self.canvas_x_entry.setFixedWidth(85)
        self.canvas_x_entry.setAlignment(Qt.AlignLeft)
        self.canvas_x_entry.setToolTip('Change the width of the canvas')
        self.canvas_x_entry.valueChanged.connect(self.update_canvas_size)
        self.canvas_y_entry = QSpinBox(self)
        self.canvas_y_entry.setMaximum(5000)
        self.canvas_y_entry.setFixedWidth(85)
        self.canvas_y_entry.setAlignment(Qt.AlignLeft)
        self.canvas_y_entry.setToolTip('Change the height of the canvas')
        self.canvas_y_entry.valueChanged.connect(self.update_canvas_size)

        self.canvas_preset_dropdown = QComboBox(self)
        self.canvas_preset_dropdown.setFixedWidth(200)
        self.canvas_preset_dropdown.setToolTip('Change the preset of the canvas')
        self.canvas_presets = {
            'MPRUN Standard (1000 x 700)': (1000, 700),
            'Web (1920 x 1080)': (1920, 1080),
            'Letter (797 x 612)': (797, 612),
            'Legal (1008 x 612)': (1008, 612),
            'A4 (595 x 842)': (595, 842),
            'A6 (828 x 1169)': (828, 1169),
            'Phone (1080 x 1920)': (1080, 1920),
            'Custom': 'c',

        }
        for canvas, key in self.canvas_presets.items():
            self.canvas_preset_dropdown.addItem(canvas, key)
        self.canvas_preset_dropdown.setCurrentText('Custom')
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.update_canvas_preset)

        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setFixedWidth(200)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
        self.canvas_name_entry.setToolTip('Change the name of the canvas')
        self.canvas_name_entry.editingFinished.connect(self.update_canvas_name)

        widget1 = mprun.gui.horizontal_layout()
        widget1.layout().addStretch()
        widget1.layout().addWidget(canvas_x_size_label)
        widget1.layout().addWidget(self.canvas_x_entry)
        widget1.layout().addWidget(canvas_y_size_label)
        widget1.layout().addWidget(self.canvas_y_entry)

        widget2 = mprun.gui.horizontal_layout()
        widget2.layout().addStretch()
        widget2.layout().addWidget(canvas_preset_label)
        widget2.layout().addWidget(self.canvas_preset_dropdown)

        widget3 = mprun.gui.horizontal_layout()
        widget3.layout().addStretch()
        widget3.layout().addWidget(canvas_name_label)
        widget3.layout().addWidget(self.canvas_name_entry)

        self.layout.addWidget(widget1)
        self.layout.addWidget(widget2)
        self.layout.addWidget(widget3)

    def update_canvas_size(self):
        items = [item for item in self.canvas.selectedItems() if isinstance(item, CanvasItem)]
        if not items:
            return

        old_sizes = [(item.rect().width(), item.rect().height()) for item in items]
        new_width = self.canvas_x_entry.value()
        new_height = self.canvas_y_entry.value()

        command = CanvasSizeEditCommand(items, old_sizes, new_width, new_height)
        self.canvas.addCommand(command)

        for item in items:
            if isinstance(item, CanvasItem):
                item.text.setPos(item.boundingRect().x(), item.boundingRect().y())

    def update_canvas_preset(self):
        choice = self.canvas_preset_dropdown.itemData(self.canvas_preset_dropdown.currentIndex())

        if choice != 'c':
            self.canvas_x_entry.setValue(choice[0])
            self.canvas_y_entry.setValue(choice[1])

    def update_canvas_name(self):
        items = [item for item in self.canvas.selectedItems() if isinstance(item, CanvasItem)]
        if not items:
            return

        old_names = [item.name() for item in items]
        new_name = self.canvas_name_entry.text()

        command = CanvasNameEditCommand(items, old_names, new_name)
        self.canvas.addCommand(command)


class ScenePanel(mprun.gui.base_widget):
    def __init__(self, canvas, parent):
        super().__init__(parent)
        self.setMinimumHeight(200)

        self.canvas = canvas
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createUI()

    def createUI(self):
        self.zoom_widget = mprun.gui.spinbox(self)
        self.zoom_widget.label().setText('Zoom:     ')
        self.zoom_widget.spinBox().setRange(1, 80779)
        self.zoom_widget.spinBox().setSuffix('%')
        self.zoom_widget.spinBox().setToolTip('Change the zoom level')
        self.zoom_widget.spinBox().setFixedWidth(80)
        self.zoom_widget.spinBox().setValue(100)
        self.rotate_widget = mprun.gui.spinbox(self)
        self.rotate_widget.label().setText('Rotation:')
        self.rotate_widget.spinBox().setRange(-360, 360)
        self.rotate_widget.spinBox().setSuffix('°')
        self.rotate_widget.spinBox().setToolTip('Change the rotation of the scene')
        self.rotate_widget.spinBox().setFixedWidth(80)
        self.rotate_widget.spinBox().setValue(0)
        self.zoom_widget.spinBox().valueChanged.connect(self.zoomAndRotateView)
        self.rotate_widget.spinBox().valueChanged.connect(self.zoomAndRotateView)

        self.reset_btn = QPushButton('↺ Reset')
        self.reset_btn.setFixedWidth(150)
        self.reset_btn.setHidden(True)
        self.reset_btn.clicked.connect(self.resetView)

        sculpt_label = QLabel('Sculpt Radius:')
        self.sculpt_radius_spin = QSpinBox(self)
        self.sculpt_radius_spin.setSuffix(' pt')
        self.sculpt_radius_spin.setFixedWidth(75)
        self.sculpt_radius_spin.setRange(10, 500)
        self.sculpt_radius_spin.setToolTip('Change the sculpt radius')
        self.sculpt_radius_spin.setValue(100)
        self.sculpt_radius_spin.valueChanged.connect(self.parent.use_set_sculpt_radius)
        sculpt_hlayout = mprun.gui.horizontal_layout()
        sculpt_hlayout.layout().addWidget(sculpt_label)
        sculpt_hlayout.layout().addWidget(self.sculpt_radius_spin)
        sculpt_hlayout.layout().addStretch()

        self.layout.addWidget(self.zoom_widget)
        self.layout.addWidget(self.rotate_widget)
        self.layout.addWidget(self.reset_btn)
        self.layout.addWidget(sculpt_hlayout)
        self.layout.addStretch()

    def zoomAndRotateView(self):
        if self.zoom_widget.spinBox().value() != 100:
            self.reset_btn.setHidden(False)

        elif self.rotate_widget.spinBox().value() != 0:
            self.reset_btn.setHidden(False)

        else:
            self.reset_btn.setHidden(True)

        zoom = self.zoom_widget.spinBox().value() / 100
        rotation = self.rotate_widget.spinBox().value()
        self.parent.canvas_view.resetTransform()
        self.parent.canvas_view.scale(zoom, zoom)
        self.parent.canvas_view.rotate(rotation)

    def resetView(self):
        self.zoom_widget.spinBox().setValue(100)
        self.rotate_widget.spinBox().setValue(0)
        self.reset_btn.setHidden(True)
