import sys
import math
import time

import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from graphics_framework import *
from custom_classes import *
from custom_widgets import *
from course_elements import *
from canvas_creation_dialog import *
from pixels2svg import *

class MPRUN(QMainWindow):
    def __init__(self):
        super().__init__()
        # Creating the main window
        self.setWindowTitle('MPRUN - Vectorspace')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setGeometry(0, 0, 1500, 800)
        self.setAcceptDrops(True)
        # Possible cursor??
        # self.setCursor(QCursor(QPixmap('logos and icons/Tool Icons/selection_icon.png').scaled(QSize(30, 30))))

        # Drawing undoing, redoing
        self.last_drawing = []
        self.drawing_history = []

        # File
        self.file_name = None
        self.last_paper = None

        # Drawing stroke methods
        self.outline_color = item_stack()
        self.fill_color = item_stack()
        self.outline_color.set('black')
        self.fill_color.set('white')
        self.font_color = item_stack()
        self.font_color.set('black')

        # Grid Size and rotating screens
        self.gsnap_grid_size = 10
        self.screen_rotate_size = 0

        # Create GUI
        self.create_initial_canvas()
        self.create_menu()
        self.init_toolbars()
        self.create_toolbar1()
        self.create_toolbar2()
        self.create_toolbar3()
        self.create_canvas()

    def create_initial_canvas(self):
        # Canvas, canvas color
        self.canvas = QGraphicsScene()
        width = 64000
        height = 64000
        self.canvas.setSceneRect(-width // 2, -height // 2, width, height)
        brush1 = QBrush(QColor('#545454'))
        self.canvas.setBackgroundBrush(brush1)

    def create_menu(self):
        # Create menus
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('&File')
        self.tool_menu = self.menu_bar.addMenu('&Tools')
        self.edit_menu = self.menu_bar.addMenu('&Edit')
        self.item_menu = self.menu_bar.addMenu('&Item')

        # Create file actions
        insert_action = QAction('Insert', self)
        insert_action.triggered.connect(self.insert_image)

        add_canvas_action = QAction('Add Canvas', self)
        add_canvas_action.triggered.connect(self.use_add_canvas)

        export_action = QAction('Export', self)
        export_action.triggered.connect(self.choose_export)

        close_action = QAction('Close', self)
        close_action.triggered.connect(lambda: self.close())

        # Create tools actions
        path_action = QAction('Path', self)
        path_action.triggered.connect(self.use_path)
        path_action.triggered.connect(self.update_pen)

        erase_action = QAction('Erase', self)
        erase_action.triggered.connect(self.use_erase)
        erase_action.triggered.connect(self.update_pen)

        linelabel_action = QAction('Line and Label', self)
        linelabel_action.triggered.connect(self.use_label)
        linelabel_action.triggered.connect(self.update_pen)

        text_action = QAction('Text', self)
        text_action.triggered.connect(self.use_text)
        text_action.triggered.connect(self.update_font)

        smooth_action = QAction('Smooth Path', self)
        smooth_action.triggered.connect(self.use_smooth_path)

        # Create edit actions
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.triggered.connect(self.use_duplicate)

        group_action = QAction('Group Selected', self)
        group_action.triggered.connect(self.create_group)

        ungroup_action = QAction('Ungroup Selected', self)
        ungroup_action.triggered.connect(self.ungroup_group)

        vectorize_action = QAction('Vectorize', self)
        vectorize_action.triggered.connect(self.use_vectorize)

        # Create item actions
        raise_layer_action = QAction('Raise Layer', self)
        raise_layer_action.triggered.connect(self.use_raise_layer)

        lower_layer_action = QAction('Lower Layer', self)
        lower_layer_action.triggered.connect(self.use_lower_layer)

        bring_to_front_action = QAction('Bring to Front', self)
        bring_to_front_action.triggered.connect(self.use_bring_to_front)

        lock_action = QAction('Lock Position', self)
        lock_action.triggered.connect(self.lock_item)

        unlock_action = QAction('Unlock Position', self)
        unlock_action.triggered.connect(self.unlock_item)

        permanent_lock_action = QAction('Permanent Lock Position', self)
        permanent_lock_action.triggered.connect(self.permanent_lock_item)

        center_action = QAction('Center', self)
        center_action.triggered.connect(self.use_center_item)

        hide_action = QAction('Hide Selected', self)
        hide_action.triggered.connect(self.use_hide_item)

        unhide_action = QAction('Unhide All', self)
        unhide_action.triggered.connect(self.use_unhide_all)

        # Add actions
        self.file_menu.addAction(insert_action)
        self.file_menu.addAction(add_canvas_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_action)

        self.tool_menu.addAction(path_action)
        self.tool_menu.addAction(erase_action)
        self.tool_menu.addSeparator()
        self.tool_menu.addAction(linelabel_action)
        self.tool_menu.addAction(text_action)
        self.tool_menu.addSeparator()
        self.tool_menu.addAction(smooth_action)

        self.edit_menu.addAction(duplicate_action)
        self.edit_menu.addAction(group_action)
        self.edit_menu.addAction(ungroup_action)
        self.edit_menu.addAction(vectorize_action)

        self.item_menu.addAction(raise_layer_action)
        self.item_menu.addAction(lower_layer_action)
        self.item_menu.addAction(bring_to_front_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(lock_action)
        self.item_menu.addAction(unlock_action)
        self.item_menu.addAction(permanent_lock_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(center_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(hide_action)
        self.item_menu.addAction(unhide_action)

    def init_toolbars(self):
        # Toolbar
        self.toolbar = QToolBar('MPRUN Toolset')
        self.toolbar.setStyleSheet('QToolBar{spacing: 5px;}')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Action toolbar
        self.action_toolbar = QToolBar('MPRUN Action Bar')
        self.action_toolbar.setStyleSheet('QToolBar{spacing: 8px; padding: 1px;}')
        self.action_toolbar.setFixedWidth(300)
        self.action_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.action_toolbar)

    def create_toolbar1(self):
        #----action toolbar widgets----#

        # Tabview
        self.tab_view = QTabWidget(self)
        self.tab_view.setTabPosition(QTabWidget.TabPosition.West)
        self.tab_view.setTabShape(QTabWidget.TabShape.Rounded)

        # Properties Tab
        self.properties_tab = QWidget()
        self.properties_tab_layout = QVBoxLayout()
        self.properties_tab.setLayout(self.properties_tab_layout)
        self.tab_view.addTab(self.properties_tab, 'Properties')

        # Elements Tab
        self.elements_tab = QWidget()
        self.elements_tab_layout = QVBoxLayout()
        self.elements_tab.setLayout(self.elements_tab_layout)
        self.tab_view.addTab(self.elements_tab, 'Elements')

        # Vectorize Tab
        self.vectorize_tab = QWidget()
        self.vectorize_tab_layout = QVBoxLayout()
        self.vectorize_tab.setLayout(self.vectorize_tab_layout)
        self.tab_view.addTab(self.vectorize_tab, 'Vectorizing')

        # Libraries Tab
        self.libraries_tab = QWidget()
        self.libraries_tab_layout = QVBoxLayout()
        self.libraries_tab.setLayout(self.libraries_tab_layout)
        self.tab_view.addTab(self.libraries_tab, 'Libraries')

        # All labels
        properties_label = QLabel('Transform', self)
        properties_label.setStyleSheet("QLabel { color: gray; font-size: 20px; alignment: center; }")
        properties_label.setAlignment(Qt.AlignLeft)

        appearence_label = QLabel('Appearance', self)
        appearence_label.setStyleSheet("QLabel { color: gray; font-size: 20px; alignment: center; }")
        appearence_label.setAlignment(Qt.AlignLeft)

        quick_actions_label = QLabel('Quick Actions', self)
        quick_actions_label.setStyleSheet("QLabel { color: gray; font-size: 20px; alignment: center; }")
        quick_actions_label.setAlignment(Qt.AlignLeft)

        layers_label = QLabel('Layers', self)
        layers_label.setStyleSheet("QLabel { color: gray; font-size: 20px;}")
        layers_label.setAlignment(Qt.AlignLeft)



        text_options_label = QLabel('Text', self)
        text_options_label.setStyleSheet("QLabel { color: gray; font-size: 20px;}")
        text_options_label.setAlignment(Qt.AlignLeft)

        vector_options_label = QLabel('Vectorize', self)
        vector_options_label.setStyleSheet("QLabel { color: gray; font-size: 20px;}")
        vector_options_label.setAlignment(Qt.AlignLeft)

        color_tolerance_label = QLabel('Vectorize Color Tolerance:')
        color_tolerance_label.setStyleSheet('font-size: 10px;')

        # Labels
        rotation_label = QLabel('Rotating:')
        rotation_label.setStyleSheet('font-size: 10px;')
        scale_label = QLabel('Scaling:')
        scale_label.setStyleSheet('font-size: 10px;')
        opacity_label = QLabel('Opacity:')
        opacity_label.setStyleSheet('font-size: 10px;')

        # Entries
        self.rotate_slider = QSlider()
        self.rotate_slider.setRange(-360, 360)
        self.rotate_slider.setSliderPosition(0)
        self.rotate_slider.setOrientation(Qt.Horizontal)
        self.rotate_slider.valueChanged.connect(self.use_rotate)

        self.scale_slider = QSlider()
        self.scale_slider.setRange(1, 100)
        self.scale_slider.setOrientation(Qt.Horizontal)
        self.scale_slider.setSliderPosition(10)
        self.scale_slider.valueChanged.connect(self.use_scale_all)

        self.opacity_slider = QSlider()
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setOrientation(Qt.Horizontal)
        self.opacity_slider.setSliderPosition(100)
        self.opacity_slider.valueChanged.connect(self.use_change_opacity)

        self.entry1 = QLineEdit()
        self.entry1.textChanged.connect(self.use_scale_all)
        self.entry1.setPlaceholderText("Overall scale factor")

        self.entry2 = QLineEdit()
        self.entry2.textChanged.connect(self.use_scale_x)
        self.entry2.setPlaceholderText("Horizontal scale factor")

        self.entry3 = QLineEdit()
        self.entry3.textChanged.connect(self.use_scale_y)
        self.entry3.setPlaceholderText("Vertical scale factor")

        # Fill Color Button
        self.fill_color_btn = QPushButton('', self)
        self.fill_color_btn.setStyleSheet(f'background-color: black; border: None')
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+4'))
        self.fill_color.set('black')
        self.fill_color_btn.clicked.connect(self.fill_color_chooser)
        self.fill_color_btn.clicked.connect(self.update_pen)

        # Vector convert tolerance spinbox
        self.color_tolerance_spin = QSpinBox(self)
        self.color_tolerance_spin.setMaximum(1028)
        self.color_tolerance_spin.setMinimum(128)
        self.color_tolerance_spin.setValue(256)

        # Layer Combobox
        self.layer_options = {'Layer 0 (Default)': 0, 'Layer 1 (Course Elements)': 1, 'Layer 2 (Lines/Paths)': 2,
                              'Layer 3 (Text/Labels)': 3}
        self.layer_combo = QComboBox(self)
        for layer, value in self.layer_options.items():
            self.layer_combo.addItem(layer, value)

        # Vector convert background widgets
        self.background_remove_check_btn = QCheckBox(self)
        self.background_remove_check_btn.setText('Remove Background')

        # Layer Associated Widgets
        raise_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/raise_layer_icon.png'), '', self)
        raise_layer_btn.setToolTip('''Raise Layer Tool:
        Key-1''')
        raise_layer_btn.setShortcut(QKeySequence('1'))
        raise_layer_btn.clicked.connect(self.use_raise_layer)
        lower_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/lower_layer_icon.png'), '', self)
        lower_layer_btn.setToolTip('''Lower Layer Tool:
        Key-2''')
        lower_layer_btn.setShortcut(QKeySequence('2'))
        lower_layer_btn.clicked.connect(self.use_lower_layer)
        bring_to_front_btn = QPushButton(QIcon('logos and icons/Tool Icons/set_always_on_top_icon.png'), '', self)
        bring_to_front_btn.setToolTip('''Bring To Front Tool:
        Key-B''')
        bring_to_front_btn.setShortcut(QKeySequence('B'))
        bring_to_front_btn.clicked.connect(self.use_bring_to_front)
        horizontal_widget_for_layer_buttons = ToolbarHorizontalLayout()
        horizontal_widget_for_layer_buttons.layout.addWidget(raise_layer_btn)
        horizontal_widget_for_layer_buttons.layout.addWidget(lower_layer_btn)
        horizontal_widget_for_layer_buttons.layout.addWidget(bring_to_front_btn)

        # Stroke fill related widgets
        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine,
                                     'Dotted Stroke': Qt.DotLine,
                                     'Dashed Stroke': Qt.DashLine,
                                     'Dashed Dot Stroke': Qt.DashDotLine,
                                     'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox(self)
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)
        self.stroke_pencap_options = {'Square Cap': Qt.SquareCap, 'Flat Cap': Qt.FlatCap, 'Round Cap': Qt.RoundCap}
        self.stroke_pencap_combo = QComboBox(self)
        for pencap, value in self.stroke_pencap_options.items():
            self.stroke_pencap_combo.addItem(pencap, value)
        self.outline_color_btn = QPushButton('', self)
        self.outline_color_btn.setStyleSheet(f'background-color: {self.outline_color.get()}; border: None')
        self.outline_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.outline_color_btn.clicked.connect(self.stroke_color_chooser)
        self.outline_color_btn.clicked.connect(self.update_pen)
        self.stroke_size_spin = QSpinBox(self)
        self.stroke_size_spin.setValue(3)
        self.stroke_size_spin.setMaximum(1000)
        self.stroke_size_spin.setMinimum(1)
        stroke_size_label = QLabel('Stroke Size:', self)
        stroke_attributes_label = QLabel('Stroke Attributes:', self)
        fill_attributes_label = QLabel('Fill Attributes:', self)

        # Font related widgets
        self.font_choice_combo = QFontComboBox(self)
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setValue(20)
        self.font_size_spin.setMaximum(1000)
        self.font_size_spin.setMinimum(1)
        self.font_color_btn = QPushButton('', self)
        self.font_color_btn.setStyleSheet(f'background-color: black; border: None')
        self.font_color_btn.clicked.connect(self.font_color_chooser)
        self.font_color_btn.clicked.connect(self.update_font)
        self.bold_btn = QPushButton('', self)
        self.bold_btn.setIcon(QIcon('logos and icons/Tool Icons/bold_icon.png'))
        self.italic_btn = QPushButton('', self)
        self.italic_btn.setIcon(QIcon('logos and icons/Tool Icons/italic_icon.png'))
        self.underline_btn = QPushButton('', self)
        self.underline_btn.setIcon(QIcon('logos and icons/Tool Icons/underline_icon.png'))
        self.bold_btn.setCheckable(True)
        self.italic_btn.setCheckable(True)
        self.underline_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.update_font)
        self.italic_btn.clicked.connect(self.update_font)
        self.underline_btn.clicked.connect(self.update_font)
        widget4 = ToolbarHorizontalLayout()
        widget4.layout.addWidget(self.bold_btn)
        widget4.layout.addWidget(self.italic_btn)
        widget4.layout.addWidget(self.underline_btn)
        font_choice_label = QLabel('Font:', self)
        font_size_label = QLabel('Font Size:', self)

        # Quick action related widgets
        self.stroke_fill_check_btn = QCheckBox(self)
        self.stroke_fill_check_btn.setText('Fill Enabled')
        self.gsnap_check_btn = QCheckBox(self)
        self.gsnap_check_btn.setText('GSNAP Enabled')
        self.gsnap_grid_spin = QSpinBox(self)
        grid_size_label = QLabel('GSNAP Grid Size:', self)
        self.gsnap_grid_spin.setValue(10)
        self.gsnap_grid_spin.setMinimum(1)
        self.gsnap_grid_spin.setMaximum(1000)
        self.drop_shadow_check_btn = QCheckBox(self)
        self.drop_shadow_check_btn.setText('Drop Shadow')
        self.drop_shadow_check_btn.clicked.connect(self.use_drop_shadow)
        horizontal_widget_for_stroke_fill = ToolbarHorizontalLayout()
        horizontal_widget_for_stroke_fill.layout.addWidget(self.gsnap_check_btn)
        horizontal_widget_for_stroke_fill.layout.addWidget(self.stroke_fill_check_btn)
        widget3 = ToolbarHorizontalLayout()
        widget3.layout.addWidget(self.drop_shadow_check_btn)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.update_pen)
        self.stroke_style_combo.currentIndexChanged.connect(self.update_pen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.update_pen)
        self.stroke_fill_check_btn.clicked.connect(self.update_pen)
        self.font_size_spin.valueChanged.connect(self.update_font)
        self.font_choice_combo.currentFontChanged.connect(self.update_font)
        self.layer_combo.currentIndexChanged.connect(self.use_set_layer)
        self.gsnap_grid_spin.valueChanged.connect(self.update_grid_size)

        # Add action toolbar actions
        self.action_toolbar.addWidget(self.tab_view)

        # Properties Tab Widgets
        self.properties_tab_layout.addWidget(properties_label)
        self.properties_tab_layout.addWidget(rotation_label)
        self.properties_tab_layout.addWidget(self.rotate_slider)
        self.properties_tab_layout.addWidget(scale_label)
        self.properties_tab_layout.addWidget(self.scale_slider)
        self.properties_tab_layout.addWidget(self.entry1)
        self.properties_tab_layout.addWidget(self.entry2)
        self.properties_tab_layout.addWidget(self.entry3)
        self.properties_tab_layout.addSpacerItem(QSpacerItem(10, 15))
        self.properties_tab_layout.addWidget(appearence_label)
        self.properties_tab_layout.addWidget(stroke_size_label)
        self.properties_tab_layout.addWidget(self.stroke_size_spin)
        self.properties_tab_layout.addWidget(stroke_attributes_label)
        self.properties_tab_layout.addWidget(self.outline_color_btn)
        self.properties_tab_layout.addWidget(self.stroke_style_combo)
        self.properties_tab_layout.addWidget(self.stroke_pencap_combo)
        self.properties_tab_layout.addWidget(fill_attributes_label)
        self.properties_tab_layout.addWidget(self.fill_color_btn)
        self.properties_tab_layout.addWidget(opacity_label)
        self.properties_tab_layout.addWidget(self.opacity_slider)
        self.properties_tab_layout.addSpacerItem(QSpacerItem(10, 15))
        self.properties_tab_layout.addWidget(quick_actions_label)
        self.properties_tab_layout.addWidget(horizontal_widget_for_stroke_fill)
        self.properties_tab_layout.addWidget(widget3)
        self.properties_tab_layout.addWidget(grid_size_label)
        self.properties_tab_layout.addWidget(self.gsnap_grid_spin)
        self.properties_tab_layout.addSpacerItem(QSpacerItem(10, 130))

        # Elements Tab Widgets
        self.elements_tab_layout.addWidget(layers_label)
        self.elements_tab_layout.addWidget(self.layer_combo)
        self.elements_tab_layout.addWidget(horizontal_widget_for_layer_buttons)
        self.elements_tab_layout.addSpacerItem(QSpacerItem(10, 15))
        self.elements_tab_layout.addWidget(text_options_label)
        self.elements_tab_layout.addWidget(font_choice_label)
        self.elements_tab_layout.addWidget(self.font_choice_combo)
        self.elements_tab_layout.addWidget(font_size_label)
        self.elements_tab_layout.addWidget(self.font_size_spin)
        self.elements_tab_layout.addWidget(self.font_color_btn)
        self.elements_tab_layout.addWidget(widget4)
        self.elements_tab_layout.addSpacerItem(QSpacerItem(10, 500))

        # Vectorize Tab Widgets
        self.vectorize_tab_layout.addWidget(vector_options_label)
        self.vectorize_tab_layout.addWidget(color_tolerance_label)
        self.vectorize_tab_layout.addWidget(self.color_tolerance_spin)
        self.vectorize_tab_layout.addWidget(self.background_remove_check_btn)
        self.vectorize_tab_layout.addSpacerItem(QSpacerItem(10, 700))

        # Libraries Tab Widgets
        self.libraries_tab_layout.addWidget(CourseElementsWin(self.canvas))
        self.libraries_tab_layout.addSpacerItem(QSpacerItem(10, 200))

    def create_toolbar2(self):
        #----toolbar buttons----#

        # Rotate Screen Button
        icon = QAction(QIcon('logos and icons/Tool Icons/rotate_screen_icon.png'), '', self)
        icon.setToolTip('''Rotate View:
        Command+R (MacOS) or Control+R (Windows)''')
        icon.setShortcut(QKeySequence('Ctrl+R'))
        icon.triggered.connect(self.use_rotate_screen)

        # Select Button
        select_btn = QAction(QIcon('logos and icons/Tool Icons/selection_icon.png'), '', self)
        select_btn.setToolTip('''Select Tool:
        Key-Spacebar''')
        select_btn.setShortcut(QKeySequence(Qt.Key_Space))
        select_btn.triggered.connect(self.use_select)

        # Pan Button
        pan_btn = QAction(QIcon('logos and icons/Tool Icons/pan_icon.png'), '', self)
        pan_btn.setToolTip('''Pan Tool:
        Key-P''')
        pan_btn.setShortcut(QKeySequence("P"))
        pan_btn.triggered.connect(self.use_pan)

        # Refit Button
        refit_btn = QAction(QIcon('logos and icons/Tool Icons/refit_view_icon.png'), '', self)
        refit_btn.setToolTip('''Refit View Tool:
        Key-W''')
        refit_btn.setShortcut(QKeySequence("W"))
        refit_btn.triggered.connect(self.use_refit_screen)

        # Path draw button
        self.path_btn = QAction(QIcon('logos and icons/Tool Icons/path_draw_icon.png'), '', self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip('''Path Draw Tool:
        Key-L''')
        self.path_btn.setShortcut(QKeySequence('L'))
        self.path_btn.triggered.connect(self.use_path)  # Connect to method to toggle path drawing

        # Label draw button
        self.label_btn = QAction(QIcon('logos and icons/Tool Icons/line_and_label_icon.png'), "", self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip('''Line and Label Tool:
        Key-T''')
        self.label_btn.setShortcut(QKeySequence('T'))
        self.label_btn.triggered.connect(self.use_label)  # Connect to method to toggle path drawing

        # Add Text Button
        self.add_text_btn = QAction(QIcon('logos and icons/Tool Icons/text_icon.png'), '', self)
        self.add_text_btn.setToolTip('''Text Tool:
        Command+T (MacOS) or Control+T (Windows)''')
        self.add_text_btn.setShortcut(QKeySequence('Ctrl+T'))
        self.add_text_btn.setCheckable(True)
        self.add_text_btn.triggered.connect(self.use_text)

        # Erase Button
        erase_btn = QAction(QIcon('logos and icons/Tool Icons/erase_icon.png'), '', self)
        erase_btn.setToolTip('''Erase Tool:
        Key-E''')
        erase_btn.setShortcut(QKeySequence('E'))
        erase_btn.triggered.connect(self.use_erase)

        # Duplicate Button
        duplicate_btn = QAction(QIcon('logos and icons/Tool Icons/duplicate_icon.png'), '', self)
        duplicate_btn.setToolTip('''Duplicate Tool:
        Key-D''')
        duplicate_btn.setShortcut(QKeySequence("D"))
        duplicate_btn.triggered.connect(self.use_duplicate)

        # Lock Item Button
        lock_btn = QAction(QIcon('logos and icons/Tool Icons/lock_icon.png'), '', self)
        lock_btn.setToolTip('''Lock Position Tool: 
        Command+L (MacOS) or Control+L (Windows)''')
        lock_btn.setShortcut(QKeySequence('Ctrl+L'))
        lock_btn.triggered.connect(self.lock_item)

        # Unlock Item Button
        unlock_btn = QAction(QIcon('logos and icons/Tool Icons/unlock_icon.png'), '', self)
        unlock_btn.setToolTip('''Unlock Position Tool: 
        Command+U (MacOS) or Control+U (Windows)''')
        unlock_btn.setShortcut(QKeySequence('Ctrl+U'))
        unlock_btn.triggered.connect(self.unlock_item)

        # Permanent Lock Button
        permanent_lock_btn = QAction(QIcon('logos and icons/Tool Icons/permanent_lock_icon.png'), '', self)
        permanent_lock_btn.setToolTip('''Permanent Lock Tool: 
        Command+Shift+L (MacOS) or Control+Shift+L (Windows)''')
        permanent_lock_btn.setShortcut(QKeySequence('Ctrl+Shift+L'))
        permanent_lock_btn.triggered.connect(self.permanent_lock_item)

        # Hide Button
        hide_btn = QAction(QIcon('logos and icons/Tool Icons/hide_icon.png'), '', self)
        hide_btn.setToolTip('''Hide Element Tool: 
        Key-H''')
        hide_btn.setShortcut(QKeySequence('H'))
        hide_btn.triggered.connect(self.use_hide_item)

        # Unhide Button
        unhide_btn = QAction(QIcon('logos and icons/Tool Icons/unhide_icon.png'), '', self)
        unhide_btn.setToolTip('''Unhide All Tool: 
        Command+H (MacOS) or Control+H (Windows)''')
        unhide_btn.setShortcut(QKeySequence('Ctrl+H'))
        unhide_btn.triggered.connect(self.use_unhide_all)

        # Center Item Button
        center_item_btn = QAction(QIcon('logos and icons/Tool Icons/center_item_icon.png'), '', self)
        center_item_btn.setToolTip('''Center Element Tool:
        Shift+C (MacOS) or Shift+C (Windows)''')
        center_item_btn.setShortcut(QKeySequence("Shift+C"))
        center_item_btn.triggered.connect(self.use_center_item)

        # Create Group Button
        group_create_btn = QAction(QIcon('logos and icons/Tool Icons/group_icon.png'), '', self)
        group_create_btn.setToolTip('''Group Create Tool: 
        Key-G''')
        group_create_btn.setShortcut(QKeySequence('G'))
        group_create_btn.triggered.connect(self.create_group)

        # Smooth Button
        smooth_btn = QAction(QIcon('logos and icons/Tool Icons/simplify_icon.png'), '', self)
        smooth_btn.setToolTip('''Smooth Path Tool: 
        Key-S''')
        smooth_btn.setShortcut(QKeySequence('S'))
        smooth_btn.triggered.connect(self.use_smooth_path)

        # Vectorize Button
        vectorize_btn = QAction(QIcon('logos and icons/Tool Icons/vectorize_icon.png'), '', self)
        vectorize_btn.setToolTip('''Vectorize Tool: 
        Key-V''')
        vectorize_btn.setShortcut(QKeySequence('V'))
        vectorize_btn.triggered.connect(self.use_vectorize)

        # Add Canvas Button
        add_canvas_btn = QAction(QIcon('logos and icons/Tool Icons/add_canvas_icon.png'), '', self)
        add_canvas_btn.setToolTip('''Add Canvas Tool: 
        Key-A''')
        add_canvas_btn.setShortcut(QKeySequence('A'))
        add_canvas_btn.triggered.connect(self.use_add_canvas)

        # Insert Button
        insert_btn = QAction(QIcon('logos and icons/Tool Icons/insert_icon.png'), '', self)
        insert_btn.setToolTip('''Insert Tool:
        Key-I''')
        insert_btn.setShortcut(QKeySequence('I'))
        insert_btn.triggered.connect(self.insert_image)

        # Export Button
        export_btn = QAction(QIcon('logos and icons/Tool Icons/export_icon.png'), '', self)
        export_btn.setToolTip('''Export Tool:
        Command+E (MacOS) or Control+E (Windows)''')
        export_btn.setShortcut(QKeySequence('Ctrl+E'))
        export_btn.triggered.connect(self.choose_export)

        # ----add actions----#

        # Add toolbar actions
        self.toolbar.addAction(icon)
        self.toolbar.addSeparator()
        self.toolbar.addAction(select_btn)
        self.toolbar.addAction(pan_btn)
        self.toolbar.addAction(refit_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.path_btn)
        self.toolbar.addAction(erase_btn)
        self.toolbar.addAction(self.label_btn)
        self.toolbar.addAction(self.add_text_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(duplicate_btn)
        self.toolbar.addAction(lock_btn)
        self.toolbar.addAction(unlock_btn)
        self.toolbar.addAction(permanent_lock_btn)
        self.toolbar.addAction(hide_btn)
        self.toolbar.addAction(unhide_btn)
        self.toolbar.addAction(center_item_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(group_create_btn)
        self.toolbar.addAction(smooth_btn)
        self.toolbar.addAction(vectorize_btn)
        self.toolbar.addAction(add_canvas_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(insert_btn)
        self.toolbar.addAction(export_btn)
        self.toolbar.addSeparator()

    def create_toolbar3(self):
        pass

    def create_canvas(self):
        # QGraphicsView Logic, set the main widget
        self.canvas_view = CustomGraphicsView(self.canvas,
                                              self.path_btn,
                                              self.label_btn,
                                              self.stroke_fill_check_btn,
                                              self.add_text_btn)
        self.canvas_view.setRenderHint(QPainter.Antialiasing)
        self.canvas_view.setRenderHint(QPainter.TextAntialiasing)
        self.canvas_view.setScene(self.canvas)
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setBold(True if self.bold_btn.isChecked() else False)
        font.setItalic(True if self.italic_btn.isChecked() else False)
        font.setUnderline(True if self.underline_btn.isChecked() else False)
        self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2, Qt.PenJoinStyle.RoundJoin))
        self.canvas_view.update_font(font, QColor(self.font_color.get()))
        self.canvas_view.update_stroke_fill_color(self.fill_color.get())

        # Use default tools, set central widget
        self.use_select()
        self.setCentralWidget(self.canvas_view)

        # Drawing paper
        self.paper = CanvasItem(0, 0, 1000, 700)
        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, Qt.SolidLine)
        self.paper.setBrush(brush)
        self.paper.setPen(pen)
        self.paper.setZValue(-1)
        self.paper.setToolTip('Canvas 1')
        self.canvas.addItem(self.paper)
        self.last_paper = self.paper

        # Text on paper
        self.paper_text = EditableTextBlock("""Run #:   
Page #:   
Competition:    
Athlete:    
Date:   """)
        self.paper_text.setPos(2, 2)
        self.paper_text.setDefaultTextColor(QColor('black'))
        self.paper_text.setFont(QFont("Helvetica", 9))
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.paper_text.setZValue(-1)
        self.paper_text.setToolTip(f"Editable Text Block")
        self.paper_text.setParentItem(self.paper)
        self.canvas.addItem(self.paper_text)

        self.text_item = EditableTextBlock('Canvas 1')
        self.text_item.setZValue(-1)
        self.text_item.setParentItem(self.paper)
        self.text_item.setDefaultTextColor(QColor('black'))
        self.text_item.setScale(1.5)
        self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
        self.text_item.set_locked()

        # If the Path Button is checked, update!!
        if self.path_btn.isChecked():
            self.update_pen()

        if self.label_btn.isChecked():
            self.update_font()

        # Refit view after everything
        self.use_refit_screen()

    def keyPressEvent(self, event):
        if event.key() == QKeySequence('Backspace'):
            for item in self.canvas.selectedItems():
                self.canvas.removeItem(item)

        elif event.key() == QKeySequence('Escape'):
            self.canvas.clearSelection()
            if self.path_btn.isChecked():
                self.path_btn.setChecked(False)

            elif self.label_btn.isChecked():
                self.label_btn.setChecked(False)

            elif self.add_text_btn.isChecked():
                self.add_text_btn.setChecked(False)

            self.use_select()

        elif event.key() == QKeySequence('Z'):
            self.gsnap_check_btn.setChecked(False) if self.gsnap_check_btn.isChecked() else self.gsnap_check_btn.setChecked(True)

        super().keyPressEvent(event)

    def closeEvent(self, event):
        if len(self.canvas.items()) > 3:
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox()
            confirmation_dialog.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
            confirmation_dialog.setWindowTitle('Close Project')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("Are you sure you want to close the open project? (This will destroy any progress!)")
            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirmation_dialog.setDefaultButton(QMessageBox.No)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            # If the user clicked Yes, close the window
            if result == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

        else:
            event.accept()

    def update_pen(self):
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2, Qt.PenJoinStyle.RoundJoin))
        self.canvas_view.update_stroke_fill_color(self.fill_color.get())

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                if isinstance(item, CustomPathItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)
                    item.setPen(pen)

                    # Check if widget is pressed
                    if self.stroke_fill_check_btn.isChecked():
                        item.setBrush(QColor(self.fill_color.get()))

                    else:
                        item.setBrush(QBrush(QColor(Qt.transparent)))

                elif isinstance(item, EditableTextBlock):
                    font = QFont()
                    font.setFamily(self.font_choice_combo.currentText())
                    font.setPixelSize(self.font_size_spin.value())
                    font.setBold(True if self.bold_btn.isChecked() else False)
                    font.setItalic(True if self.italic_btn.isChecked() else False)
                    font.setUnderline(True if self.underline_btn.isChecked() else False)

                    item.setFont(font)
                    item.setDefaultTextColor(QColor(self.font_color.get()))

                elif isinstance(item, CustomCircleItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)
                    item.setPen(pen)

                    # Check if widget is pressed
                    if self.stroke_fill_check_btn.isChecked():
                        item.setBrush(QColor(self.fill_color.get()))

                    else:
                        item.setBrush(QBrush(QColor(Qt.transparent)))

                    if item.childItems():
                        for child in item.childItems():
                            if isinstance(child, CustomPathItem):
                                index1 = self.stroke_style_combo.currentIndex()
                                data1 = self.stroke_style_combo.itemData(index1)
                                index2 = self.stroke_pencap_combo.currentIndex()
                                data2 = self.stroke_pencap_combo.itemData(index2)

                                pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1,
                                           data2)
                                child.setPen(pen)

                                # Check if widget is pressed
                                if self.stroke_fill_check_btn.isChecked():
                                    child.setBrush(QColor(self.fill_color.get()))

                                else:
                                    child.setBrush(QBrush(QColor(Qt.transparent)))

                            elif isinstance(child, CustomRectangleItem):
                                index1 = self.stroke_style_combo.currentIndex()
                                data1 = self.stroke_style_combo.itemData(index1)
                                index2 = self.stroke_pencap_combo.currentIndex()
                                data2 = self.stroke_pencap_combo.itemData(index2)

                                pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1,
                                           data2)
                                child.setPen(pen)

                                # Check if widget is pressed
                                if self.stroke_fill_check_btn.isChecked():
                                    child.setBrush(QColor(self.fill_color.get()))

                                else:
                                    child.setBrush(QBrush(QColor(Qt.transparent)))

                elif isinstance(item, CustomRectangleItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)
                    item.setPen(pen)

                    # Check if widget is pressed
                    if self.stroke_fill_check_btn.isChecked():
                        item.setBrush(QColor(self.fill_color.get()))

                    else:
                        item.setBrush(QBrush(QColor(Qt.transparent)))

    def update_font(self):
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setBold(True if self.bold_btn.isChecked() else False)
        font.setItalic(True if self.italic_btn.isChecked() else False)
        font.setUnderline(True if self.underline_btn.isChecked() else False)

        self.canvas_view.update_font(font, QColor(self.font_color.get()))

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                if isinstance(item, EditableTextBlock):
                    item.setFont(font)
                    item.setDefaultTextColor(QColor(self.font_color.get()))

    def update_grid_size(self, value):
        for item in self.canvas.items():
            if isinstance(item, CustomGraphicsItemGroup):
                item.set_grid_size(value)
                self.gsnap_grid_size = value

            else:
                self.gsnap_grid_size = value

    def stroke_color_chooser(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Stroke Color')

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.outline_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.outline_color.set(color.name())

    def fill_color_chooser(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Fill Color')

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.fill_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.fill_color.set(color.name())

    def font_color_chooser(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Font Color')

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.font_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.font_color.set(color.name())

    def use_select(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        self.canvas_view.setDragMode(QGraphicsView.RubberBandDrag)

    def use_pan(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        self.canvas_view.setDragMode(QGraphicsView.ScrollHandDrag)

    def use_refit_screen(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                self.canvas_view.fitInView(item.sceneBoundingRect(), Qt.KeepAspectRatio)

    def use_path(self):
        self.label_btn.setChecked(False)
        self.add_text_btn.setChecked(False)

        self.path_btn.setChecked(True)

    def use_erase(self):
        self.label_btn.setChecked(False)
        self.add_text_btn.setChecked(False)

        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        self.canvas_view.update_pen(QPen(QColor('white'), self.stroke_size_spin.value(), data1, data2))
        self.canvas_view.update_stroke_fill_color('white')

        self.outline_color_btn.setStyleSheet(f'background-color: white; border: None')
        self.fill_color_btn.setStyleSheet('background-color: white; border: None')
        self.fill_color.set('white')
        self.outline_color.set('white')

        self.path_btn.setChecked(True)

    def use_label(self):
        self.path_btn.setChecked(False)
        self.add_text_btn.setChecked(False)

        self.label_btn.setChecked(True)

    def use_text(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        self.add_text_btn.setChecked(True)

    def use_rotate_screen(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)
        self.screen_rotate_size += 90
        transform = QTransform()
        transform.rotate(self.screen_rotate_size)

        self.canvas_view.setTransform(transform)

    def use_set_layer(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)
        index = self.layer_combo.currentIndex()
        data = self.layer_combo.itemData(index)

        if self.canvas.selectedItems():
            for items in self.canvas.selectedItems():
                items.setZValue(data)

    def use_bring_to_front(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        selected_items = self.canvas.selectedItems()
        max_z_value = max(item.zValue() for item in self.canvas.items())
        for item in selected_items:
            item.setZValue(max_z_value + 1)

    def use_vectorize(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPixmapItem):
                # Convert the pixmap to SVG
                try:
                    # Get the vector name
                    entry, ok = QInputDialog.getText(self, 'Vectorize', 'Enter a name for the output Vector:')

                    if ok:
                        # Set app loading
                        self.setCursor(Qt.WaitCursor)

                        # Create vector
                        pixels2svg(input_path=item.return_filename(),
                                   output_path=f'V-C STOR/{entry}.svg',
                                   color_tolerance=self.color_tolerance_spin.value(),
                                   remove_background=True if self.background_remove_check_btn.isChecked() else False)

                        # Set cursor back
                        self.setCursor(Qt.ArrowCursor)

                        # Display information
                        QMessageBox.information(self, "Convert Finished", "Vector converted successfully.")

                        # Add the item to the scene
                        item = CustomSvgItem(f'V-C STOR/{entry}.svg')
                        item.store_filename(f'V-C STOR/{entry}.svg')
                        self.canvas.addItem(item)
                        self.create_item_attributes(item)
                        item.setToolTip('Converted Vector (MPRUN Element)')

                except Exception as e:
                    # Set cursor back
                    self.setCursor(Qt.ArrowCursor)

                    QMessageBox.critical(self, "Convert Error", f"Failed to convert bitmap to vector: {e}")

            else:
                pass

    def use_duplicate(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Get selected items and create a copy
        selected_items = self.canvas.selectedItems()

        for item in selected_items:
            if isinstance(item, EditableTextBlock):
                item.duplicate()

            elif isinstance(item, CustomPathItem):
                item.duplicate()

            elif isinstance(item, CustomRectangleItem):
                item.duplicate()

            elif isinstance(item, CustomCircleItem):
                item.duplicate()

            elif isinstance(item, CustomPixmapItem):
                item.duplicate()

            elif isinstance(item, CustomSvgItem):
                item.duplicate()

            elif isinstance(item, CustomGraphicsItemGroup):
                item.duplicate()

    def use_raise_layer(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            item.setZValue(item.zValue() + 1.0)

    def use_lower_layer(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            if item.zValue() <= 0:
                QMessageBox.critical(self, 'Lower Layer', "You cannot lower this Element any lower.")

            else:
                item.setZValue(item.zValue() - 1.0)

    def use_scale_all(self, value):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                # Calculate value
                scale_factor = value / 100.0
                scale = 0.1 + (scale_factor * 9.9)

                # Calculate the center point of the item
                center = item.boundingRect().center()

                # Set the transformation origin to the center point
                item.setTransformOriginPoint(center)

                # Scale item
                item.setScale(scale)

        except ValueError:
            pass

    def use_scale_x(self, value):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                # Calculate the center point of the item
                center = item.boundingRect().center()

                # Set the transformation origin to the center point
                item.setTransformOriginPoint(center)

                transform = QTransform()
                transform.scale(value, 1.0)
                item.setTransform(transform)

        except ValueError:
            pass

    def use_scale_y(self, value):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                # Calculate the center point of the item
                center = item.boundingRect().center()

                # Set the transformation origin to the center point
                item.setTransformOriginPoint(center)

                transform = QTransform()
                transform.scale(1.0, value)
                item.setTransform(transform)
        except ValueError:
            pass

    def use_rotate(self, value):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        items = self.canvas.selectedItems()
        for item in items:
            if isinstance(item, CanvasItem):
                pass

            else:
                # Calculate the center point of the item
                center = item.boundingRect().center()

                # Set the transformation origin to the center point
                item.setTransformOriginPoint(center)

                # Rotate the item
                item.setRotation(value)

    def use_change_opacity(self, value):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.opacity_slider.maximum()

        # Create effect
        effect = QGraphicsOpacityEffect()

        # Set opacity value
        effect.setOpacity(opacity)

        # Apply the effect to selected items
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                pass

            else:
                item.setGraphicsEffect(effect)

    def use_drop_shadow(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Create effect
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)

        # Apply the effect to selected items
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                pass

            else:
                if self.drop_shadow_check_btn.isChecked():
                    item.setGraphicsEffect(effect)

                else:
                    if item.graphicsEffect() and QGraphicsDropShadowEffect():
                        item.setGraphicsEffect(None)

    def use_center_item(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                rect = self.paper.boundingRect()
                center = rect.center()

                item_rect = item.boundingRect()
                item_center = item_rect.center()
                new_pos = center - item_center
                item.setPos(new_pos)

    def use_add_canvas(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        self.window = AddCanvasDialog(self.canvas, self.last_paper)
        self.window.show()

    def use_smooth_path(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                smoothed_path = item.smooth_path(item.path())

                item.setPath(smoothed_path)
                item.setToolTip('Smoothed MPRUN Path Element')

    def use_hide_item(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            item.setVisible(False)

    def use_unhide_all(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        for item in self.canvas.items():
            item.setVisible(True)

    def use_insert(self):
        self.path_btn.setChecked(False)
        self.label_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            if isinstance(item, EditableTextBlock):
                if item.flags() == Qt.TextInteractionFlag.TextEditorInteraction:
                    pass

    def lock_item(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        item = self.canvas.selectedItems()

        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable, False)
            items.setToolTip('Locked MPRUN Element')

            if isinstance(items, CustomGraphicsItemGroup):
                items.set_locked()

    def unlock_item(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)
        item = self.canvas.selectedItems()

        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable)
            items.setToolTip('Free MPRUN Element')

            if isinstance(items, CustomGraphicsItemGroup):
                items.set_unlocked()

    def permanent_lock_item(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        if self.canvas.selectedItems():
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox()
            confirmation_dialog.setWindowTitle('Permanently Lock Item')
            confirmation_dialog.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("Are you sure you want to permanently lock the selected Element? (The Element will no longer be editable!)")
            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirmation_dialog.setDefaultButton(QMessageBox.No)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            # If the user clicked Yes, close the window
            if result == QMessageBox.Yes:
                item = self.canvas.selectedItems()

                for items in item:
                    items.setFlag(QGraphicsItem.ItemIsMovable, False)
                    items.setFlag(QGraphicsItem.ItemIsSelectable, False)

                    if isinstance(items, EditableTextBlock):
                        items.set_locked()
                        items.setToolTip('Permanently Locked MPRUN Element')

                    if isinstance(items, CustomGraphicsItemGroup):
                        items.set_locked()
                        items.setToolTip('Permanently Locked MPRUN Element')

                    if isinstance(items, CanvasItem):
                        pass

                    else:
                        items.setToolTip('Permanently Locked MPRUN Element')

            else:
                pass

    def insert_image(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Create Options
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # File Dialog, file path
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("SVG files (*.svg);;PNG files (*.png);;JPG files (*.jpg);;JPEG files (*.jpeg);;TIFF files (*.tiff);;BMP files (*.bmp);;ICO files (*.ico);;(Beta) Python files (*.py)")

        file_path, _ = file_dialog.getOpenFileName(self, "Insert Element", "", "SVG files (*.svg);;PNG files (*.png);;JPG files (*.jpg);;JPEG files (*.jpeg);;TIFF files (*.tiff);;BMP files (*.bmp);;ICO files (*.ico);;(Beta) Python files (*.py)",
                                                   options=options)

        if file_path:
            if file_path.endswith('.svg'):
                svg_item = CustomSvgItem(file_path)
                svg_item.store_filename(file_path)

                self.canvas.addItem(svg_item)
                svg_item.setToolTip('Imported SVG Item (Not an MPRUN Element)')

                self.create_item_attributes(svg_item)

            elif file_path.endswith('.py'):
                with open(file_path, 'r') as f:
                    contents = f.read()
                    exec(contents)

            else:
                image1 = QPixmap(file_path)
                image2 = CustomPixmapItem(image1)
                image2.store_filename(file_path)

                self.canvas.addItem(image2)
                image2.setToolTip('Imported Bitmap Item (Not an MPRUN Element)')

                self.create_item_attributes(image2)

    def export_canvas(self, filename, selected_item):
        # Turn tools off
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Create a QImage with the size of the selected item (QGraphicsRectItem)
        rect = selected_item.sceneBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        print(rect)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        try:
            # Save the image to file
            success = image.save(filename)

            if success:
                # If saving was successful, show a notification
                QMessageBox.information(self, "Export Finished", "Export completed successfully.")

                # Open the image with the default image viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

        except Exception as e:
            # If saving failed, show an error notification
            QMessageBox.critical(self, "Export Error", f"Failed to export canvas to file: {e}")

    def choose_export(self):
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        # Create a custom dialog to with a dropdown to select which canvas to export
        selector = CanvasItemSelector(self)
        selector.show()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                # Add the canvas items to the selector
                selector.add_canvas_item(itemName=item.toolTip(), itemKey=item)

        # Create a function to choose the selected item
        def export():
            index = selector.comboBox.currentIndex()
            data = selector.comboBox.itemData(index)
            selected_item = selector.comboBox.itemData(index)

            if selected_item:
                self.export_selected_canvas(selected_item)

        selector.exportButton.clicked.connect(export)

    def export_selected_canvas(self, selected_item):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # File dialog, filepath
        file_dialog = QFileDialog()

        file_path, selected_filter = file_dialog.getSaveFileName(self, 'Export Canvas', 'C:/Users/kelle/Downloads',
                                                                 'SVG files (*.svg);;PNG files (*.png);;JPG files (*.jpg);;JPEG files (*.jpeg);;TIFF files (*.tiff);;PDF files (*.pdf);;WEBP files (*.webp);;HEIC files (*.heic);;ICO files (*.ico)',
                                                                 options=options)

        if file_path:
            # Get the selected filter's extension
            filter_extensions = {
                'SVG files (*.svg)': '.svg',
                'PNG files (*.png)': '.png',
                'JPG files (*.jpg)': '.jpg',
                'JPEG files (*.jpeg)': '.jpeg',
                'TIFF files (*.tiff)': '.tiff',
                'PDF files (*.pdf)': '.pdf',
                'WEBP files (*.webp)': '.webp',
                'ICO files (*.ico)': '.ico',
                'HEIC files (*.heic)': '.heic'
            }
            selected_extension = filter_extensions.get(selected_filter, '.png')

            # Ensure the file_path has the selected extension
            if not file_path.endswith(selected_extension):
                file_path += selected_extension

            if selected_extension == '.svg':
                try:
                    # Get the bounding rect
                    rect = selected_item.sceneBoundingRect()

                    # Export as SVG
                    svg_generator = QSvgGenerator()
                    svg_generator.setFileName(file_path)
                    svg_generator.setSize(rect.size().toSize())
                    svg_generator.setViewBox(rect)

                    # Get input for title
                    title, ok1 = QInputDialog.getText(self, 'SVG Document Title', 'Enter a title for the SVG')

                    if ok1:
                        svg_generator.setTitle(title)
                    else:
                        svg_generator.setTitle('MPRUN SVG Document (Powered by QSvgGenerator)')

                    # Clear selection
                    self.canvas.clearSelection()

                    # Create a QPainter to paint onto the QSvgGenerator
                    painter = QPainter()
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                    painter.begin(svg_generator)

                    # Render the scene onto the QPainter
                    self.canvas.render(painter, target=rect, source=rect)

                    # End painting
                    painter.end()

                    # Show export finished notification
                    QMessageBox.information(self, 'Export Finished', 'Export completed successfully.',
                                            QMessageBox.Ok)

                    # Open the image with the default image viewer
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

                except Exception as e:
                    # Show export error notification
                    QMessageBox.information(self, 'Export Failed', f'Export failed: {e}',
                                            QMessageBox.Ok)

            elif selected_extension == '.pdf':
                # Export as PDF
                printer = QPdfWriter(file_path)
                printer.setPageSize(QPdfWriter.Letter)
                printer.setResolution(300)  # Set the resolution (in DPI)

                # Clear selection
                self.canvas.clearSelection()

                # Create painter, save file
                painter = QPainter(printer)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

                # Render the scene onto the QPainter
                self.canvas.render(painter, target=selected_item.sceneBoundingRect(), source=selected_item.sceneBoundingRect())

                # End painting
                painter.end()

                # Show export finished notification
                QMessageBox.information(self, 'Export Finished', 'Export completed successfully.',
                                        QMessageBox.Ok)

                # Open the image with the default image viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

            else:
                try:
                    self.canvas.clearSelection()
                    self.export_canvas(file_path, selected_item)

                except Exception as e:
                    print(e)

    def create_group(self):
        # Set tools off
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                if item.childItems():
                    pass

                else:
                    pass

            else:
                group = CustomGraphicsItemGroup(self.gsnap_check_btn)
                group.set_grid_size(self.gsnap_grid_size)

                item = self.canvas.selectedItems()

                # Set flags for group
                group.setFlag(QGraphicsItem.ItemIsMovable)
                group.setFlag(QGraphicsItem.ItemIsSelectable)

                # Add group
                self.canvas.addItem(group)
                self.canvas.update()

                for items in item:
                    # Set flag
                    items.setFlag(QGraphicsItem.ItemIsSelectable, False)

                    # Check if the item is an instance
                    if isinstance(items, QGraphicsTextItem):
                        items.setTextInteractionFlags(Qt.NoTextInteraction)

                        # Set an object name
                        items.setToolTip(f"Grouped Text Block (This item's text is not editable)")

                    elif isinstance(items, EditableTextBlock):
                        items.setTextInteractionFlags(Qt.NoTextInteraction)

                        # Set an object name
                        items.setToolTip(f"Grouped Text Block (This item's text is not editable)")

                    elif isinstance(items, CustomPathItem):
                        # Set an object name
                        items.setToolTip(f"Grouped Path")

                    # Add items to group
                    group.addToGroup(items)
                    group.setToolTip('Grouped Object')

    def ungroup_group(self):
        # Set tools off
        self.label_btn.setChecked(False)
        self.path_btn.setChecked(False)

        for group in self.canvas.selectedItems():
            if isinstance(group, CustomGraphicsItemGroup):
                if group.childItems():
                    for child in group.childItems():
                        child.setFlag(QGraphicsItem.ItemIsSelectable)
                        child.setToolTip('Free MPRUN Element')

                self.canvas.destroyItemGroup(group)

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)

    def set_template(self, template_choice):
        if template_choice == 1:
            pass

        elif template_choice == 2:
            self.paper.setRect(-100, -100, 728, 521)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        elif template_choice == 3:
            self.paper.setRect(-100, -100, 1625, 1193)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        elif template_choice == 4:
            self.paper.setRect(-100, -100, 980, 1820)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        elif template_choice == 5:
            self.paper.setRect(-100, -100, 491, 299)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        elif template_choice == 6:
            self.paper.setRect(-100, -100, 1747, 1147)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        elif template_choice == 7:
            self.paper.setRect(-100, -100, 1266, 924)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()
            
        elif template_choice == 8:
            self.paper.setRect(-100, -100, 1820, 980)
            self.paper_text.setPos(-98, -98)
            self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)
            self.use_center_item()

        else:
            pass

        # Refit screen
        self.use_refit_screen()

    def custom_template(self, x, y, default_text, grid_size):
        self.paper.setRect(-100, -100, x-100, y-100)
        self.paper_text.setPlainText(default_text)
        self.paper_text.setPos(-98, -98)
        self.text_item.setPos(self.paper.boundingRect().x(), self.paper.boundingRect().y() - 30)

        # Refit screen
        self.use_refit_screen()

        for item in self.canvas.items():
            if isinstance(item, CustomGraphicsItemGroup):
                item.set_grid_size(grid_size)
                self.gsnap_grid_spin.setValue(grid_size)
                self.gsnap_grid_size = grid_size


if __name__ == '__main__':
    app = QApplication([])
    window = MPRUN()
    window.show()
    app.exec_()
