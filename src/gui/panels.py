from src.scripts.imports import *
from src.gui.custom_widgets import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class PropertiesPanel(QWidget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.properties_tab_layout = QVBoxLayout()
        self.setLayout(self.properties_tab_layout)

        self.canvas = canvas
        self.parent = parent

        self.create_ui()

    def create_ui(self):
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
        self.width_scale_spin.setSuffix(' pt')
        self.width_scale_spin.setToolTip('Change the width')
        self.height_scale_spin = QDoubleSpinBox(self)
        self.height_scale_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.height_scale_spin.setFixedWidth(75)
        self.height_scale_spin.setValue(0.0)
        self.height_scale_spin.setDecimals(2)
        self.height_scale_spin.setRange(-10000.00, 10000.00)
        self.height_scale_spin.setSingleStep(1.0)
        self.height_scale_spin.setSuffix(' pt')
        self.height_scale_spin.setToolTip('Change the height')
        self.rotate_item_spin = QSpinBox(self)
        self.rotate_item_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.rotate_item_spin.setFixedWidth(70)
        self.rotate_item_spin.setRange(-360, 360)
        self.rotate_item_spin.setSuffix('°')
        self.rotate_item_spin.setToolTip('Change the rotation')
        self.flip_horizontal_btn = QPushButton(QIcon('ui/Tool Icons/flip_horizontal_icon.png'), '')
        self.flip_horizontal_btn.setToolTip('Flip horizontal')
        self.flip_horizontal_btn.setStyleSheet('border: none;')
        self.flip_horizontal_btn.clicked.connect(self.parent.use_flip_horizontal)
        self.flip_vertical_btn = QPushButton(QIcon('ui/Tool Icons/flip_vertical_icon.png'), '')
        self.flip_vertical_btn.setToolTip('Flip vertical')
        self.flip_vertical_btn.setStyleSheet('border: none;')
        self.flip_vertical_btn.clicked.connect(self.parent.use_flip_vertical)
        widget7 = ToolbarHorizontalLayout()
        widget7.layout.addWidget(self.x_pos_label)
        widget7.layout.addWidget(self.x_pos_spin)
        widget7.layout.addWidget(self.width_transform_label)
        widget7.layout.addWidget(self.width_scale_spin)
        widget7.layout.addSpacing(25)
        widget7.layout.addWidget(self.flip_horizontal_btn)
        widget8 = ToolbarHorizontalLayout()
        widget8.layout.addWidget(self.y_pos_label)
        widget8.layout.addWidget(self.y_pos_spin)
        widget8.layout.addWidget(self.height_transform_label)
        widget8.layout.addWidget(self.height_scale_spin)
        widget8.layout.addSpacing(25)
        widget8.layout.addWidget(self.flip_vertical_btn)
        widget9 = ToolbarHorizontalLayout()
        widget9.layout.addWidget(self.rotation_label)
        widget9.layout.addWidget(self.rotate_item_spin)
        widget9.layout.addStretch()

        fill_label = QLabel('Fill')
        fill_label.setStyleSheet('color: white;')
        self.fill_color_btn = CustomColorDisplayButton(self)
        self.fill_color_btn.setButtonColor(self.parent.fill_color.get())
        self.fill_color_btn.setFixedWidth(28)
        self.fill_color_btn.setFixedHeight(26)
        self.fill_color_btn.setToolTip('Change the fill color')
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+2'))
        self.fill_color_btn.clicked.connect(self.parent.fill_color_chooser)
        self.fill_color_btn.clicked.connect(self.parent.update_item_fill)
        widget5 = ToolbarHorizontalLayout()
        widget5.layout.addWidget(self.fill_color_btn)
        widget5.layout.addWidget(fill_label)
        widget5.layout.setContentsMargins(0, 14, 0, 0)

        self.stroke_color_btn = CustomColorDisplayButton(self)
        self.stroke_color_btn.setButtonColor(self.parent.outline_color.get())
        self.stroke_color_btn.setFixedWidth(28)
        self.stroke_color_btn.setFixedHeight(26)
        self.stroke_color_btn.setToolTip('Change the stroke color')
        self.stroke_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.stroke_color_btn.clicked.connect(self.parent.stroke_color_chooser)
        self.stroke_color_btn.clicked.connect(self.parent.update_item_pen)
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
        self.opacity_btn.setIcon(QIcon('ui/UI Icons/Major/opacity_icon.png'))
        self.opacity_btn.setIconSize(QSize(24, 24))
        self.opacity_btn.setStyleSheet('QPushButton:hover { background: none }')
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix('%')
        self.opacity_spin.setToolTip('Change the opacity')
        self.opacity_spin.valueChanged.connect(self.parent.use_change_opacity)
        opacity_hlayout = ToolbarHorizontalLayout()
        opacity_hlayout.layout.addWidget(self.opacity_btn)
        opacity_hlayout.layout.addWidget(opacity_label)
        opacity_hlayout.layout.addWidget(self.opacity_spin)
        opacity_hlayout.layout.addSpacing(100)
        opacity_hlayout.layout.setContentsMargins(0, 14, 0, 0)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.parent.update_item_pen)
        self.stroke_style_combo.currentIndexChanged.connect(self.parent.update_item_pen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.parent.update_item_pen)
        self.join_style_combo.currentIndexChanged.connect(self.parent.update_item_pen)
        self.x_pos_spin.valueChanged.connect(self.parent.use_set_item_pos)
        self.y_pos_spin.valueChanged.connect(self.parent.use_set_item_pos)
        self.width_scale_spin.valueChanged.connect(self.parent.use_scale_x)
        self.height_scale_spin.valueChanged.connect(self.parent.use_scale_y)
        self.rotate_item_spin.valueChanged.connect(self.parent.use_rotate)

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


class LibrariesPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.current_folder_path = ""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.canvas = canvas

        # List widget for the library
        self.library_list_widget = CustomListWidget()
        self.library_list_widget.setStyleSheet('border: none')
        self.library_list_widget.setIconSize(QSize(80, 80))

        # Library button
        self.open_library_button = QPushButton("Open Library")
        self.open_library_button.setToolTip('Open library from local directory')
        self.reload_library_button = QPushButton("")
        self.reload_library_button.setFixedWidth(28)
        self.reload_library_button.setStyleSheet('border: none')
        self.reload_library_button.setIcon(QIcon('ui/UI Icons/Minor/refresh_icon.svg'))
        self.reload_library_button.setToolTip('Reload the current library')

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setToolTip('Search for files in the current library')
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setObjectName('modernLineEdit')
        self.search_bar.textChanged.connect(self.filter_library)

        library_btn_hlayout = QHBoxLayout()
        library_btn_hlayout.addWidget(self.open_library_button)
        library_btn_hlayout.addWidget(self.reload_library_button)

        search_hlayout = QHBoxLayout()
        search_hlayout.addWidget(self.open_library_button)
        search_hlayout.addWidget(self.search_bar)

        self.layout.addLayout(library_btn_hlayout)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.library_list_widget)

        # Connect button to the method
        self.open_library_button.clicked.connect(self.open_library)
        self.reload_library_button.clicked.connect(self.reload_library)

        self.load_library(os.path.abspath('course elements'))

    def open_library(self):
        # Open file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Library Folder")

        if folder_path:
            self.current_folder_path = folder_path
            self.load_library(folder_path)

    def reload_library(self):
        if self.current_folder_path:
            self.load_library(self.current_folder_path)

    def load_library(self, folder_path):
        # Clear existing items in the list widget
        self.library_list_widget.clear()
        self.library_list_widget.all_items = []
        self.current_folder_path = folder_path

        # List all SVG files in the selected folder (now supports pixmap as well)
        svg_files = [f for f in os.listdir(folder_path) if f.endswith(('.svg', '.png', '.jpg', '.jpeg'))]

        # Check if no SVG files are found
        if not svg_files:
            self.library_list_widget.setDragEnabled(False)
            list_item = QListWidgetItem('No files found')
            list_item.setIcon(QIcon('ui/UI Icons/folder_failed_icon.svg'))
            self.library_list_widget.setIconSize(QSize(40, 40))
            self.library_list_widget.addItem(list_item)

        else:
            self.library_list_widget.setDragEnabled(True)
            # Add each SVG file to the list widget
            for svg_file in svg_files:
                list_item = QListWidgetItem(svg_file)
                list_item.setData(Qt.UserRole, os.path.join(folder_path, svg_file))
                list_item.setIcon(QIcon(os.path.join(folder_path, svg_file)))
                self.library_list_widget.setIconSize(QSize(80, 80))
                self.library_list_widget.addItem(list_item)
                self.library_list_widget.all_items.append(list_item)

    def filter_library(self, text):
        try:
            self.library_list_widget.filter_items(text)

        except Exception as e:
            print(e)

    def items(self):
        l = []

        for row in range(self.library_list_widget.count()):
            item = self.library_list_widget.item(row)
            l.append(item.text())

        return l if l else ''


class CharactersPanel(QWidget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.characters_tab_layout = QVBoxLayout()
        self.setLayout(self.characters_tab_layout)

        self.canvas = canvas
        self.parent = parent

        self.create_ui()

    def create_ui(self):
        # _____ Characters tab widgets _____
        self.font_choice_combo = QFontComboBox(self)
        self.font_choice_combo.setToolTip('Change the font style')
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setValue(20)
        self.font_size_spin.setMaximum(1000)
        self.font_size_spin.setMinimum(1)
        self.font_size_spin.setFixedWidth(105)
        self.font_size_spin.setSuffix(' pt')
        self.font_size_spin.setToolTip('Change the font size')
        self.font_letter_spacing_spin = QSpinBox(self)
        self.font_letter_spacing_spin.setValue(1)
        self.font_letter_spacing_spin.setMaximum(1000)
        self.font_letter_spacing_spin.setMinimum(-100)
        self.font_letter_spacing_spin.setFixedWidth(105)
        self.font_letter_spacing_spin.setSuffix(' pt')
        self.font_letter_spacing_spin.setToolTip('Change the font letter spacing')
        self.font_color_btn = CustomColorDisplayButton(self)
        self.font_color_btn.setFixedWidth(90)
        self.font_color_btn.setToolTip('Change the font color')
        self.font_color_btn.setButtonColor(self.parent.font_color.get())
        self.font_color_btn.clicked.connect(self.parent.font_color_chooser)
        self.font_color_btn.clicked.connect(self.parent.update_item_font)
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
        self.bold_btn.clicked.connect(self.parent.update_item_font)
        self.italic_btn.clicked.connect(self.parent.update_item_font)
        self.underline_btn.clicked.connect(self.parent.update_item_font)
        font_size_and_spacing_hlayout = ToolbarHorizontalLayout()
        font_size_and_spacing_hlayout.layout.addWidget(
            CustomIconWidget('', 'ui/UI Icons/Major/font_size_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout.addWidget(self.font_size_spin)
        font_size_and_spacing_hlayout.layout.addWidget(
            CustomIconWidget('', 'ui/UI Icons/Major/font_spacing_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout.addWidget(self.font_letter_spacing_spin)
        font_size_and_spacing_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_style_hlayout = ToolbarHorizontalLayout()
        font_style_hlayout.layout.addWidget(self.bold_btn)
        font_style_hlayout.layout.addWidget(self.italic_btn)
        font_style_hlayout.layout.addWidget(self.underline_btn)
        font_style_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_color_hlayout = ToolbarHorizontalLayout()
        font_color_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_color_hlayout.layout.addStretch()
        font_color_hlayout.layout.addWidget(QLabel('Color:'))
        font_color_hlayout.layout.addWidget(self.font_color_btn)

        self.font_size_spin.valueChanged.connect(self.parent.update_item_font)
        self.font_letter_spacing_spin.valueChanged.connect(self.parent.update_item_font)
        self.font_choice_combo.currentFontChanged.connect(self.parent.update_item_font)
        self.font_choice_combo.currentTextChanged.connect(self.parent.update_item_font)

        self.characters_tab_layout.addWidget(self.font_choice_combo)
        self.characters_tab_layout.addWidget(font_size_and_spacing_hlayout)
        self.characters_tab_layout.addWidget(font_style_hlayout)
        self.characters_tab_layout.addWidget(font_color_hlayout)


class ImageTracingPanel(QWidget):
    def __init__(self, canvas, parent):
        super().__init__()
        self.image_trace_layout = QVBoxLayout()
        self.setLayout(self.image_trace_layout)

        self.canvas = canvas
        self.parent = parent

        self.create_ui()

    def create_ui(self):
        # _____ Image Trace tab widgets _____
        colormode_label = QLabel('Preset:')
        mode_label = QLabel('Mode:')
        color_precision_label = QLabel('Color Precision (More Accurate):', self)
        corner_threshold_label = QLabel('Corner Threshold (Smoother):', self)
        path_precision_label = QLabel('Path Precision (More Accurate):', self)

        self.colormode_combo = QComboBox(self)
        self.colormode_combo.setToolTip('Change the color mode')
        self.colormode_combo.addItem('Color', 'color')
        self.colormode_combo.addItem('Black and White', 'binary')
        self.mode_combo = QComboBox(self)
        self.mode_combo.setToolTip('Change the geometry mode')
        self.mode_combo.addItem('Spline', 'spline')
        self.mode_combo.addItem('Polygon', 'polygon')
        self.mode_combo.addItem('None', 'none')
        self.mode_combo.setMinimumWidth(200)

        self.color_precision_spin = QSpinBox(self)
        self.color_precision_spin.setMaximum(8)
        self.color_precision_spin.setMinimum(1)
        self.color_precision_spin.setValue(6)
        self.color_precision_spin.setToolTip('Change the color precision')
        self.corner_threshold_spin = QSpinBox(self)
        self.corner_threshold_spin.setMaximum(180)
        self.corner_threshold_spin.setMinimum(1)
        self.corner_threshold_spin.setValue(60)
        self.corner_threshold_spin.setToolTip('Change the corner threshold')
        self.path_precision_spin = QSlider(self)
        self.path_precision_spin.setOrientation(Qt.Horizontal)
        self.path_precision_spin.setMaximum(10)
        self.path_precision_spin.setMinimum(1)
        self.path_precision_spin.setSliderPosition(3)
        self.path_precision_spin.setToolTip('Change the path precision')

        image_tracehlayout1 = ToolbarHorizontalLayout()
        image_tracehlayout1.layout.addStretch()
        image_tracehlayout1.layout.addWidget(colormode_label)
        image_tracehlayout1.layout.addWidget(self.colormode_combo)
        image_tracehlayout1.layout.setContentsMargins(0, 0, 0, 0)
        image_tracehlayout2 = ToolbarHorizontalLayout()
        image_tracehlayout2.layout.addStretch()
        image_tracehlayout2.layout.addWidget(mode_label)
        image_tracehlayout2.layout.addWidget(self.mode_combo)
        image_tracehlayout2.layout.setContentsMargins(0, 0, 0, 0)

        # Vectorize Tab Widgets
        self.image_trace_layout.addWidget(image_tracehlayout1)
        self.image_trace_layout.addWidget(image_tracehlayout2)
        self.image_trace_layout.addWidget(path_precision_label)
        self.image_trace_layout.addWidget(self.path_precision_spin)
        self.image_trace_layout.addWidget(CustomMoreOrLessLabel(self))
        self.image_trace_layout.addWidget(color_precision_label)
        self.image_trace_layout.addWidget(self.color_precision_spin)
        self.image_trace_layout.addWidget(corner_threshold_label)
        self.image_trace_layout.addWidget(self.corner_threshold_spin)


class CanvasEditorPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.setFixedHeight(185)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.canvas = canvas
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
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
        self.canvas_preset_dropdown.setFixedWidth(205)
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.update_canvas_preset)

        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setFixedWidth(205)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
        self.canvas_name_entry.setToolTip('Change the name of the canvas')
        self.canvas_name_entry.editingFinished.connect(self.update_canvas_name)

        widget1 = ToolbarHorizontalLayout()
        widget1.layout.addSpacing(25)
        widget1.layout.addWidget(canvas_x_size_label)
        widget1.layout.addWidget(self.canvas_x_entry)
        widget1.layout.addWidget(canvas_y_size_label)
        widget1.layout.addWidget(self.canvas_y_entry)

        widget2 = ToolbarHorizontalLayout()
        widget2.layout.addWidget(canvas_preset_label)
        widget2.layout.addWidget(self.canvas_preset_dropdown)

        widget3 = ToolbarHorizontalLayout()
        widget3.layout.addWidget(canvas_name_label)
        widget3.layout.addWidget(self.canvas_name_entry)

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


class QuickActionsPanel(QWidget):
    def __init__(self, canvas, parent):
        super().__init__(parent)
        self.setFixedHeight(115)

        self.canvas = canvas
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createUI()

    def createUI(self):
        self.gsnap_check_btn = QCheckBox(self)
        self.gsnap_check_btn.setText('Grid Enabled')
        self.gsnap_check_btn.setToolTip('Enable snap to grid')
        self.gsnap_check_btn.setShortcut(QKeySequence('Z'))
        self.gsnap_check_btn.clicked.connect(self.use_enable_grid)
        self.gsnap_grid_spin = QSpinBox(self)
        self.gsnap_grid_spin.setFixedWidth(80)
        self.gsnap_grid_spin.setSuffix(' pt')
        grid_size_label = QLabel('Grid Size:', self)
        self.gsnap_grid_spin.setValue(10)
        self.gsnap_grid_spin.setMinimum(1)
        self.gsnap_grid_spin.setMaximum(1000)
        self.gsnap_grid_spin.setToolTip('Change the grid size')
        horizontal_widget = ToolbarHorizontalLayout()
        horizontal_widget.layout.addWidget(self.gsnap_check_btn)
        gsnap_hlayout = ToolbarHorizontalLayout()
        gsnap_hlayout.layout.addWidget(grid_size_label)
        gsnap_hlayout.layout.addWidget(self.gsnap_grid_spin)
        gsnap_hlayout.layout.addStretch()

        self.layout.addWidget(horizontal_widget)
        self.layout.addWidget(gsnap_hlayout)

        # Update
        self.gsnap_grid_spin.valueChanged.connect(self.update_grid)

    def use_exit_grid(self):
        if self.gsnap_check_btn.isChecked():
            self.gsnap_check_btn.click()

    def use_enable_grid(self):
        if self.gsnap_check_btn.isChecked():
            self.canvas.setGridEnabled(True)
            self.canvas.update()

            for item in self.canvas.items():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.gridEnabled = True

        else:
            self.canvas.setGridEnabled(False)
            self.canvas.update()

            for item in self.canvas.items():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.gridEnabled = False

    def update_grid(self):
        # Update grid
        self.canvas.setGridSize(self.gsnap_grid_spin.value())

    def update_sculpt_radius(self, value):
        self.parent.use_set_sculpt_radius(value)
