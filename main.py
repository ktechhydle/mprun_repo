import sys
import math
import time
import webbrowser
import vtracer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from PyQt5.Qt import *
from graphics_framework import *
from custom_classes import *
from custom_widgets import *
from custom_tab_widget import *
from course_elements import *
from canvas_creation_dialog import *
from version_dialog import *

class MPRUN(QMainWindow):
    def __init__(self):
        super().__init__()
        # Creating the main window
        self.setWindowTitle('MPRUN - Workspace')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setGeometry(0, 0, 1500, 800)
        self.setAcceptDrops(True)

        # File
        self.file_name = None
        self.last_paper = None
        self.stored_center_item = None

        # Drawing stroke methods
        self.outline_color = item_stack()
        self.fill_color = item_stack()
        self.outline_color.set('red')
        self.fill_color.set('white')
        self.font_color = item_stack()
        self.font_color.set('black')

        # Grid Size and rotating screens
        self.gsnap_grid_size = 10
        self.screen_rotate_size = 0

        # Undo, redo
        self.undo_stack = QUndoStack()

        # Create GUI
        self.create_initial_canvas()
        self.create_menu()
        self.init_toolbars()
        self.create_toolbar1()
        self.create_toolbar2()
        self.create_toolbar3()
        self.create_view()
        self.create_default_objects()

    def create_initial_canvas(self):
        # Canvas, canvas color
        self.canvas = CustomGraphicsScene(self.undo_stack)
        self.canvas.selectionChanged.connect(self.update_appearance_ui)

    def create_menu(self):
        # Create menus
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.mprun_menu = self.menu_bar.addMenu('&MPRUN')
        self.file_menu = self.menu_bar.addMenu('&File')
        self.tool_menu = self.menu_bar.addMenu('&Tools')
        self.edit_menu = self.menu_bar.addMenu('&Edit')
        self.item_menu = self.menu_bar.addMenu('&Item')
        self.window_menu = self.menu_bar.addMenu('&Window')

        # Create MPRUN actions
        about_action = QAction('About', self)
        about_action.triggered.connect(lambda: webbrowser.open('https://github.com/ktechhydle/mprun_repo/blob/main/README.md#introducing-mprun-the-ultimate-snowboard-and-ski-competion-run-planning-software'))

        show_version_action = QAction('Version', self)
        show_version_action.triggered.connect(self.show_version)

        # Create file actions
        insert_action = QAction('Insert', self)
        insert_action.triggered.connect(self.insert_image)

        add_canvas_action = QAction('Add Canvas', self)
        add_canvas_action.triggered.connect(self.use_add_canvas)

        export_action = QAction('Export', self)
        export_action.setShortcut(QKeySequence('Ctrl+E'))
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

        trick_table_action = QAction('Trick Table', self)
        trick_table_action.setShortcut(QKeySequence('Ctrl+Shift+T'))
        trick_table_action.triggered.connect(self.use_trick_table)

        smooth_action = QAction('Smooth Path', self)
        smooth_action.triggered.connect(self.use_smooth_path)

        close_subpath_action = QAction('Close Path', self)
        close_subpath_action.triggered.connect(self.use_close_path)

        # Create edit actions
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.canvas.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Shift+Z'))
        redo_action.triggered.connect(self.canvas.redo)

        name_action = QAction('Name', self)
        name_action.setShortcut(QKeySequence('N'))
        name_action.triggered.connect(self.use_name_item)

        scale_action = QAction('Scale', self)
        scale_action.triggered.connect(self.use_scale_tool)

        duplicate_action = QAction('Duplicate', self)
        duplicate_action.setShortcut(QKeySequence("D"))
        duplicate_action.triggered.connect(self.use_duplicate)

        group_action = QAction('Group Selected', self)
        group_action.setShortcut(QKeySequence('G'))
        group_action.triggered.connect(self.create_group)

        ungroup_action = QAction('Ungroup Selected', self)
        ungroup_action.setShortcut(QKeySequence('Ctrl+G'))
        ungroup_action.triggered.connect(self.ungroup_group)

        image_trace_action = QAction('Trace Image', self)
        image_trace_action.triggered.connect(self.use_vectorize)

        # Create item actions
        raise_layer_action = QAction('Raise Layer', self)
        raise_layer_action.triggered.connect(self.use_raise_layer)

        lower_layer_action = QAction('Lower Layer', self)
        lower_layer_action.triggered.connect(self.use_lower_layer)

        bring_to_front_action = QAction('Bring to Front', self)
        bring_to_front_action.triggered.connect(self.use_bring_to_front)

        lock_action = QAction('Lock Position', self)
        lock_action.setShortcut(QKeySequence('Ctrl+L'))
        lock_action.triggered.connect(self.lock_item)

        unlock_action = QAction('Unlock Position', self)
        unlock_action.setShortcut(QKeySequence('U'))
        unlock_action.triggered.connect(self.unlock_item)

        permanent_lock_action = QAction('Permanent Lock Position', self)
        permanent_lock_action.triggered.connect(self.permanent_lock_item)

        center_action = QAction('Center', self)
        center_action.setShortcut(QKeySequence("C"))
        center_action.triggered.connect(self.use_center_item)

        element_center_action = QAction('Set Default Center', self)
        element_center_action.triggered.connect(self.use_set_center)

        display_center_action = QAction('Display Current Center', self)
        display_center_action.triggered.connect(self.use_display_center)

        hide_action = QAction('Hide Selected', self)
        hide_action.triggered.connect(self.use_hide_item)

        unhide_action = QAction('Unhide All', self)
        unhide_action.triggered.connect(self.use_unhide_all)

        select_all_action = QAction('Select All', self)
        select_all_action.setShortcut(QKeySequence('Ctrl+A'))
        select_all_action.triggered.connect(self.use_select_all)

        # Create window menu actions
        properties_action = QAction('Properties', self)
        properties_action.triggered.connect(lambda: self.display_choosen_tab('Properties'))

        layers_action = QAction('Layers', self)
        layers_action.triggered.connect(lambda: self.display_choosen_tab('Layers'))

        libraries_action = QAction('Libraries', self)
        libraries_action.triggered.connect(lambda: self.display_choosen_tab('Libraries'))

        characters_action = QAction('Characters', self)
        characters_action.triggered.connect(lambda: self.display_choosen_tab('Characters'))

        vectorizing_action = QAction('Image Trace', self)
        vectorizing_action.triggered.connect(lambda: self.display_choosen_tab('Image Trace'))

        canvas_action = QAction('Canvas', self)
        canvas_action.triggered.connect(lambda: self.display_choosen_tab('Canvas'))

        # Add actions
        self.mprun_menu.addAction(about_action)
        self.mprun_menu.addAction(show_version_action)

        self.file_menu.addAction(add_canvas_action)
        self.file_menu.addAction(insert_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_action)

        self.tool_menu.addAction(path_action)
        self.tool_menu.addAction(erase_action)
        self.tool_menu.addSeparator()
        self.tool_menu.addAction(linelabel_action)
        self.tool_menu.addAction(text_action)
        self.tool_menu.addAction(trick_table_action)
        self.tool_menu.addSeparator()
        self.tool_menu.addAction(smooth_action)
        self.tool_menu.addAction(close_subpath_action)

        self.edit_menu.addAction(undo_action)
        self.edit_menu.addAction(redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(name_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(scale_action)
        self.edit_menu.addAction(duplicate_action)
        self.edit_menu.addAction(group_action)
        self.edit_menu.addAction(ungroup_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(image_trace_action)
        self.edit_menu.addSeparator()

        self.item_menu.addAction(raise_layer_action)
        self.item_menu.addAction(lower_layer_action)
        self.item_menu.addAction(bring_to_front_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(lock_action)
        self.item_menu.addAction(unlock_action)
        self.item_menu.addAction(permanent_lock_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(center_action)
        self.item_menu.addAction(element_center_action)
        self.item_menu.addAction(display_center_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(hide_action)
        self.item_menu.addAction(unhide_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(select_all_action)

        self.window_menu.addAction(properties_action)
        self.window_menu.addAction(layers_action)
        self.window_menu.addAction(libraries_action)
        self.window_menu.addAction(characters_action)
        self.window_menu.addAction(vectorizing_action)
        self.window_menu.addAction(canvas_action)

    def init_toolbars(self):
        # Toolbar
        self.toolbar = QToolBar('MPRUN Toolset')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.TopToolBarArea)
        self.toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Action toolbar
        self.action_toolbar = QToolBar('MPRUN Action Bar')
        self.action_toolbar.setStyleSheet('QToolBar{spacing: 8px; padding: 1px;}')
        self.action_toolbar.setFixedWidth(300)
        self.action_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.action_toolbar)

        # View Toolbar
        self.view_toolbar = QToolBar('MPRUN View Toolbar')
        self.view_toolbar.setMovable(False)
        self.view_toolbar.setFixedHeight(22)
        self.view_toolbar.setStyleSheet('padding: 1px;')
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.view_toolbar)

    def create_toolbar1(self):
        #----action toolbar widgets----#

        # Tabview
        self.tab_view = DetachableTabWidget(self)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_view.setTabShape(QTabWidget.TabShape.Rounded)

        # Properties Tab
        self.properties_tab = QWidget(self)
        self.properties_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.properties_tab.setMaximumHeight(800)
        self.properties_tab_layout = QVBoxLayout()
        self.properties_tab.setLayout(self.properties_tab_layout)
        self.tab_view.addTab(self.properties_tab, 'Properties')

        # Layers Tab
        self.layers_tab = QWidget()
        self.layers_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.layers_tab.setMaximumHeight(175)
        self.layers_tab_layout = QVBoxLayout()
        self.layers_tab.setLayout(self.layers_tab_layout)
        self.tab_view.addTab(self.layers_tab, 'Layers')

        # Characters Tab
        self.characters_tab = QWidget()
        self.characters_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.characters_tab.setMaximumHeight(325)
        self.characters_tab_layout = QVBoxLayout()
        self.characters_tab.setLayout(self.characters_tab_layout)

        # Vectorize Tab
        self.image_trace = QWidget()
        self.image_trace.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.image_trace.setMaximumHeight(375)
        self.image_trace_layout = QVBoxLayout()
        self.image_trace.setLayout(self.image_trace_layout)

        # Libraries Tab
        self.libraries_tab = QWidget()
        self.libraries_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.libraries_tab.setMaximumHeight(400)
        self.libraries_tab_layout = QVBoxLayout()
        self.libraries_tab.setLayout(self.libraries_tab_layout)
        self.tab_view.addTab(self.libraries_tab, 'Libraries')

        # Canvas Tab
        self.canvas_tab = CanvasEditorPanel(self.canvas)

        # This next section is basically all the widgets for each tab
        # Some tabs don't have many widgets as they are subclassed in other files.

        # _____ Properties tab widgets _____
        self.selection_label = QLabel('No Selection')
        self.selection_label.setStyleSheet("QLabel { font-size: 12px; }")
        properties_label = QLabel('Transform', self)
        properties_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        properties_label.setAlignment(Qt.AlignLeft)
        appearence_label = QLabel('Appearance', self)
        appearence_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        appearence_label.setAlignment(Qt.AlignLeft)
        quick_actions_label = QLabel('Quick Actions', self)
        quick_actions_label.setStyleSheet("QLabel {font-size: 12px; alignment: center; }")
        quick_actions_label.setAlignment(Qt.AlignLeft)

        rotation_label = QIconWidget('', 'logos and icons/Tool Icons/rotate_icon.png', 28, 28)
        rotation_label.setAlignment(Qt.AlignRight)
        rotation_label.setStyleSheet('font-size: 10px;')
        scale_label = QLabel('Scaling:')
        scale_label.setStyleSheet('font-size: 10px;')
        opacity_label = QLabel('Opacity:')
        opacity_label.setStyleSheet('font-size: 10px;')

        x_pos_label = QLabel('X:')
        y_pos_label = QLabel('Y:')
        width_transform_label = QLabel('W:')
        height_transform_label = QLabel('H:')
        self.x_pos_spin = QSpinBox(self)
        self.x_pos_spin.setMaximum(10000)
        self.x_pos_spin.setMinimum(-10000)
        self.x_pos_spin.setSuffix(' pt')
        self.y_pos_spin = QSpinBox(self)
        self.y_pos_spin.setMaximum(10000)
        self.y_pos_spin.setMinimum(-10000)
        self.y_pos_spin.setSuffix(' pt')
        self.width_scale_spin = QDoubleSpinBox(self)
        self.width_scale_spin.setValue(10.0)
        self.width_scale_spin.setDecimals(2)
        self.width_scale_spin.setRange(-10000.00, 10000.00)
        self.width_scale_spin.setSingleStep(0.1)
        self.width_scale_spin.setSuffix(' pt')
        self.height_scale_spin = QDoubleSpinBox(self)
        self.height_scale_spin.setValue(10.0)
        self.height_scale_spin.setDecimals(2)
        self.height_scale_spin.setRange(-10000.00, 10000.00)
        self.height_scale_spin.setSingleStep(0.1)
        self.height_scale_spin.setSuffix(' pt')
        self.rotate_item_spin = QSpinBox(self)
        self.rotate_item_spin.setRange(-360, 360)
        self.rotate_item_spin.setSuffix('°')
        flip_horizontal_btn = QPushButton(QIcon('logos and icons/Tool Icons/flip_horizontal_icon.png'), '')
        flip_horizontal_btn.setToolTip('Flip Horizontal')
        flip_horizontal_btn.setStyleSheet('border: none;')
        flip_horizontal_btn.clicked.connect(lambda: self.width_scale_spin.setValue(-self.width_scale_spin.value()))
        flip_vertical_btn = QPushButton(QIcon('logos and icons/Tool Icons/flip_vertical_icon.png'), '')
        flip_vertical_btn.setToolTip('Flip Vertical')
        flip_vertical_btn.setStyleSheet('border: none;')
        flip_vertical_btn.clicked.connect(lambda: self.height_scale_spin.setValue(-self.height_scale_spin.value()))
        widget7 = ToolbarHorizontalLayout()
        widget7.layout.addWidget(x_pos_label)
        widget7.layout.addWidget(self.x_pos_spin)
        widget7.layout.addWidget(width_transform_label)
        widget7.layout.addWidget(self.width_scale_spin)
        widget7.layout.addWidget(flip_horizontal_btn)
        widget8 = ToolbarHorizontalLayout()
        widget8.layout.addWidget(y_pos_label)
        widget8.layout.addWidget(self.y_pos_spin)
        widget8.layout.addWidget(height_transform_label)
        widget8.layout.addWidget(self.height_scale_spin)
        widget8.layout.addWidget(flip_vertical_btn)
        widget9 = ToolbarHorizontalLayout()
        widget9.layout.addWidget(rotation_label)
        widget9.layout.addWidget(self.rotate_item_spin)

        self.outline_color_btn = QPushButton('', self)
        self.outline_color_btn.setStyleSheet(f'background-color: {self.outline_color.get()};')
        self.outline_color_btn.setFixedWidth(28)
        self.outline_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.outline_color_btn.clicked.connect(self.stroke_color_chooser)
        self.outline_color_btn.clicked.connect(self.update_pen)
        self.stroke_size_spin = QSpinBox(self)
        self.stroke_size_spin.setValue(3)
        self.stroke_size_spin.setMaximum(1000)
        self.stroke_size_spin.setMinimum(1)
        self.stroke_size_spin.setSuffix(' pt')
        stroke_label = StrokeLabel('Stroke', self)
        self.stroke_style_combo = stroke_label.stroke_combo
        self.stroke_style_options = stroke_label.stroke_options
        self.stroke_pencap_combo = stroke_label.pencap_combo
        self.stroke_pencap_options = stroke_label.pencap_options
        widget6 = ToolbarHorizontalLayout()
        widget6.layout.addWidget(self.outline_color_btn)
        widget6.layout.addWidget(stroke_label)
        widget6.layout.addWidget(self.stroke_size_spin)

        fill_label = QLabel('Fill')
        fill_label.setStyleSheet('color: white;')
        self.fill_color_btn = QPushButton('', self)
        self.fill_color_btn.setStyleSheet(f'background-color: #00ff00;')
        self.fill_color_btn.setFixedWidth(28)
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+4'))
        self.fill_color.set('#00ff00')
        self.fill_color_btn.clicked.connect(self.fill_color_chooser)
        self.fill_color_btn.clicked.connect(self.update_pen)
        self.fill_transparent_btn = QPushButton('Fill Transparent', self)
        self.fill_transparent_btn.clicked.connect(self.use_fill_transparent)
        widget5 = ToolbarHorizontalLayout()
        widget5.layout.addWidget(self.fill_color_btn)
        widget5.layout.addWidget(fill_label)
        widget5.layout.addWidget(self.fill_transparent_btn)

        self.opacity_slider = QSlider()
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setOrientation(Qt.Horizontal)
        self.opacity_slider.setSliderPosition(100)
        self.opacity_slider.valueChanged.connect(self.use_change_opacity)

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
        self.close_subpath_check_btn = QCheckBox(self)
        self.close_subpath_check_btn.setText('Close Path')
        horizontal_widget_for_stroke_fill = ToolbarHorizontalLayout()
        horizontal_widget_for_stroke_fill.layout.addWidget(self.gsnap_check_btn)
        horizontal_widget_for_stroke_fill.layout.addWidget(self.drop_shadow_check_btn)
        widget3 = ToolbarHorizontalLayout()
        widget3.layout.addWidget(self.close_subpath_check_btn)

        #_____ Layers tab widgets _____
        layers_label = QLabel('Layers', self)
        layers_label.setStyleSheet("QLabel { font-size: 12px;}")
        layers_label.setAlignment(Qt.AlignLeft)

        self.layer_spin = QSpinBox(self)
        self.layer_spin.setRange(0, 9999)
        self.layer_spin.setValue(0)
        self.layer_spin.setPrefix('Layer ')
        self.hide_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/hide_icon.png'), '', self)
        self.hide_layer_btn.setFixedWidth(28)
        self.hide_layer_btn.setToolTip('Hide Selected Layer')
        self.hide_layer_btn.clicked.connect(self.use_hide_layer)
        self.unhide_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/unhide_icon.png'), '', self)
        self.unhide_layer_btn.setFixedWidth(28)
        self.unhide_layer_btn.setToolTip('Unhide Selected Layer')
        self.unhide_layer_btn.clicked.connect(self.use_unhide_layer)
        layer_hlayout = ToolbarHorizontalLayout()
        layer_hlayout.layout.addWidget(self.hide_layer_btn)
        layer_hlayout.layout.addWidget(self.unhide_layer_btn)
        layer_hlayout.layout.addWidget(self.layer_spin)
        raise_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/raise_layer_icon.png'), '', self)
        raise_layer_btn.setToolTip('''Raise Layer:
        Key-1''')
        raise_layer_btn.setFixedWidth(28)
        raise_layer_btn.setShortcut(QKeySequence('1'))
        raise_layer_btn.clicked.connect(self.use_raise_layer)
        lower_layer_btn = QPushButton(QIcon('logos and icons/Tool Icons/lower_layer_icon.png'), '', self)
        lower_layer_btn.setToolTip('''Lower Layer:
        Key-2''')
        lower_layer_btn.setFixedWidth(28)
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

        #_____ Libraries tab widgets _____
        course_elements_label = QLabel('Course Elements', self)
        course_elements_label.setStyleSheet('font-size: 12px;')

        #_____ Characters tab widgets _____
        text_options_label = QLabel('Characters', self)
        text_options_label.setStyleSheet("QLabel { font-size: 12px;}")
        text_options_label.setAlignment(Qt.AlignLeft)

        self.font_choice_combo = QFontComboBox(self)
        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setValue(20)
        self.font_size_spin.setMaximum(1000)
        self.font_size_spin.setMinimum(1)
        self.font_size_spin.setSuffix(' pt')
        self.font_letter_spacing_spin = QSpinBox(self)
        self.font_letter_spacing_spin.setValue(1)
        self.font_letter_spacing_spin.setMaximum(1000)
        self.font_letter_spacing_spin.setMinimum(-10)
        self.font_letter_spacing_spin.setSuffix(' pt')
        self.font_color_btn = QPushButton('', self)
        self.font_color_btn.setStyleSheet(f'background-color: black; border: None')
        self.font_color_btn.clicked.connect(self.font_color_chooser)
        self.font_color_btn.clicked.connect(self.update_font)
        self.bold_btn = QPushButton('B', self)
        self.bold_btn.setStyleSheet('font-weight: bold; font-size: 15px;')
        self.italic_btn = QPushButton('I', self)
        self.italic_btn.setStyleSheet('font-style: italic; font-size: 15px;')
        self.underline_btn = QPushButton('U', self)
        self.underline_btn.setStyleSheet('text-decoration: underline; font-size: 15px;')
        self.bold_btn.setCheckable(True)
        self.italic_btn.setCheckable(True)
        self.underline_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.update_font)
        self.italic_btn.clicked.connect(self.update_font)
        self.underline_btn.clicked.connect(self.update_font)
        widget4 = ToolbarHorizontalLayout()
        widget4.layout.addWidget(self.font_size_spin)
        widget4.layout.addWidget(self.bold_btn)
        widget4.layout.addWidget(self.italic_btn)
        widget4.layout.addWidget(self.underline_btn)
        font_choice_label = QLabel('Font:', self)
        font_size_label = QLabel('Font Size:', self)
        font_spacing_label = QLabel('Font Spacing:', self)
        font_color_label = QLabel('Font Color:')

        #_____ Image Trace tab widgets _____
        vector_options_label = QLabel('Image Trace', self)
        vector_options_label.setStyleSheet("QLabel { font-size: 12px;}")

        colormode_label = QLabel('Preset:')
        mode_label = QLabel('Mode:')
        color_precision_label = QLabel('Color Precision (More Accurate):', self)
        corner_threshold_label = QLabel('Corner Threshold (Smoother):', self)
        path_precision_label = QLabel('Path Precision (More Accurate):', self)

        self.colormode_combo = QComboBox(self)
        self.colormode_combo.addItem('Color', 'color')
        self.colormode_combo.addItem('Black and White', 'binary')
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItem('Spline', 'spline')
        self.mode_combo.addItem('Polygon', 'polygon')
        self.mode_combo.addItem('None', 'none')

        self.color_precision_spin = QSpinBox(self)
        self.color_precision_spin.setMaximum(8)
        self.color_precision_spin.setMinimum(1)
        self.color_precision_spin.setValue(6)
        self.corner_threshold_spin = QSpinBox(self)
        self.corner_threshold_spin.setMaximum(180)
        self.corner_threshold_spin.setMinimum(1)
        self.corner_threshold_spin.setValue(60)
        self.path_precision_spin = QSlider(self)
        self.path_precision_spin.setOrientation(Qt.Horizontal)
        self.path_precision_spin.setMaximum(10)
        self.path_precision_spin.setMinimum(1)
        self.path_precision_spin.setSliderPosition(3)

        image_tracehlayout1 = ToolbarHorizontalLayout()
        image_tracehlayout1.layout.addWidget(colormode_label)
        image_tracehlayout1.layout.addWidget(self.colormode_combo)
        image_tracehlayout2 = ToolbarHorizontalLayout()
        image_tracehlayout2.layout.addWidget(mode_label)
        image_tracehlayout2.layout.addWidget(self.mode_combo)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.update_pen)
        self.stroke_style_combo.currentIndexChanged.connect(self.update_pen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.update_pen)
        self.font_size_spin.valueChanged.connect(self.update_font)
        self.font_letter_spacing_spin.valueChanged.connect(self.update_font)
        self.font_choice_combo.currentFontChanged.connect(self.update_font)
        self.layer_spin.valueChanged.connect(self.use_set_layer)
        self.gsnap_grid_spin.valueChanged.connect(self.update_grid_size)
        self.x_pos_spin.valueChanged.connect(self.use_set_item_x)
        self.y_pos_spin.valueChanged.connect(self.use_set_item_y)
        self.width_scale_spin.valueChanged.connect(self.use_scale_x)
        self.height_scale_spin.valueChanged.connect(self.use_scale_y)
        self.rotate_item_spin.valueChanged.connect(self.use_rotate)

        # Add action toolbar actions
        self.action_toolbar.addWidget(self.tab_view)

        # Properties Tab Widgets
        self.properties_tab_layout.addWidget(self.selection_label)
        self.properties_tab_layout.addWidget(HorizontalSeparator())
        self.properties_tab_layout.addWidget(properties_label)
        self.properties_tab_layout.addWidget(widget7)
        self.properties_tab_layout.addWidget(widget8)
        self.properties_tab_layout.addWidget(widget9)
        self.properties_tab_layout.addWidget(HorizontalSeparator())
        self.properties_tab_layout.addWidget(appearence_label)
        self.properties_tab_layout.addWidget(widget6)
        self.properties_tab_layout.addWidget(widget5)
        self.properties_tab_layout.addWidget(opacity_label)
        self.properties_tab_layout.addWidget(self.opacity_slider)
        self.properties_tab_layout.addWidget(HorizontalSeparator())
        self.properties_tab_layout.addWidget(quick_actions_label)
        self.properties_tab_layout.addWidget(horizontal_widget_for_stroke_fill)
        self.properties_tab_layout.addWidget(widget3)
        self.properties_tab_layout.addWidget(HorizontalSeparator())
        self.properties_tab_layout.addWidget(grid_size_label)
        self.properties_tab_layout.addWidget(self.gsnap_grid_spin)

        # Elements Tab Widgets
        self.characters_tab_layout.addWidget(HorizontalSeparator())
        self.characters_tab_layout.addWidget(text_options_label)
        self.characters_tab_layout.addWidget(font_choice_label)
        self.characters_tab_layout.addWidget(self.font_choice_combo)
        self.characters_tab_layout.addWidget(font_color_label)
        self.characters_tab_layout.addWidget(self.font_color_btn)
        self.characters_tab_layout.addWidget(font_size_label)
        self.characters_tab_layout.addWidget(widget4)
        self.characters_tab_layout.addWidget(font_spacing_label)
        self.characters_tab_layout.addWidget(self.font_letter_spacing_spin)

        # Layers Tab Widgets
        self.layers_tab_layout.addWidget(HorizontalSeparator())
        self.layers_tab_layout.addWidget(layers_label)
        self.layers_tab_layout.addWidget(layer_hlayout)
        self.layers_tab_layout.addWidget(horizontal_widget_for_layer_buttons)

        # Vectorize Tab Widgets
        self.image_trace_layout.addWidget(HorizontalSeparator())
        self.image_trace_layout.addWidget(vector_options_label)
        self.image_trace_layout.addWidget(image_tracehlayout1)
        self.image_trace_layout.addWidget(image_tracehlayout2)
        self.image_trace_layout.addWidget(path_precision_label)
        self.image_trace_layout.addWidget(self.path_precision_spin)
        self.image_trace_layout.addWidget(QMoreOrLessLabel(self))
        self.image_trace_layout.addWidget(color_precision_label)
        self.image_trace_layout.addWidget(self.color_precision_spin)
        self.image_trace_layout.addWidget(corner_threshold_label)
        self.image_trace_layout.addWidget(self.corner_threshold_spin)

        # Libraries Tab Widgets
        self.libraries_tab_layout.addWidget(HorizontalSeparator())
        self.libraries_tab_layout.addWidget(course_elements_label)
        self.libraries_tab_layout.addWidget(CourseElementsWin(self.canvas))

    def create_toolbar2(self):
        self.action_group = QActionGroup(self)

        #----toolbar buttons----#

        # Select Button
        self.select_btn = QAction(QIcon('logos and icons/Tool Icons/selection_icon.png'), '', self)
        self.select_btn.setToolTip('''Select Tool:
        Key-Spacebar''')
        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.setShortcut(QKeySequence(Qt.Key_Space))
        self.select_btn.triggered.connect(self.use_select)

        # Pan Button
        pan_btn = QAction(QIcon('logos and icons/Tool Icons/pan_icon.png'), '', self)
        pan_btn.setToolTip('''Pan Tool:
        Key-P''')
        pan_btn.setCheckable(True)
        pan_btn.setShortcut(QKeySequence("P"))
        pan_btn.triggered.connect(self.use_pan)

        # Path draw button
        self.path_btn = QAction(QIcon('logos and icons/Tool Icons/pen_tool_icon.png'), '', self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip('''Path Draw Tool:
        Key-L''')
        self.path_btn.setShortcut(QKeySequence('L'))
        self.path_btn.triggered.connect(self.update_pen)
        self.path_btn.triggered.connect(self.use_path)

        # Erase Button
        self.erase_btn = QAction(QIcon('logos and icons/Tool Icons/erase_icon.png'), '', self)
        self.erase_btn.setToolTip('''Erase Tool:
                        Key-E''')
        self.erase_btn.setCheckable(True)
        self.erase_btn.setShortcut(QKeySequence('E'))
        self.erase_btn.triggered.connect(self.update_pen)
        self.erase_btn.triggered.connect(self.use_erase)

        # Label draw button
        self.label_btn = QAction(QIcon('logos and icons/Tool Icons/label_icon.png'), "", self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip('''Line and Label Tool:
        Key-T''')
        self.label_btn.setShortcut(QKeySequence('T'))
        self.label_btn.triggered.connect(self.update_font)
        self.label_btn.triggered.connect(self.use_label)

        # Add Text Button
        self.add_text_btn = QAction(QIcon('logos and icons/Tool Icons/text_icon.png'), '', self)
        self.add_text_btn.setToolTip('''Text Tool:
        Command+T (MacOS) or Control+T (Windows)''')
        self.add_text_btn.setShortcut(QKeySequence('Ctrl+T'))
        self.add_text_btn.setCheckable(True)
        self.add_text_btn.triggered.connect(self.update_font)
        self.add_text_btn.triggered.connect(self.use_text)

        # Scale Button
        self.scale_btn = QAction(QIcon('logos and icons/Tool Icons/scale_icon.png'), '', self)
        self.scale_btn.setToolTip('''Scale Tool: 
        Key-Q''')
        self.scale_btn.setCheckable(True)
        self.scale_btn.setShortcut(QKeySequence('Q'))
        self.scale_btn.triggered.connect(self.use_scale_tool)

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

        # Smooth Button
        smooth_btn = QAction(QIcon('logos and icons/Tool Icons/smooth_path_icon.png'), '', self)
        smooth_btn.setToolTip('''Smooth Path Tool: 
        Key-S''')
        smooth_btn.setShortcut(QKeySequence('S'))
        smooth_btn.triggered.connect(self.use_smooth_path)

        # Add Canvas Button
        self.add_canvas_btn = QAction(QIcon('logos and icons/Tool Icons/add_canvas_icon.png'), '', self)
        self.add_canvas_btn.setToolTip('''Add Canvas Tool: 
        Key-A''')
        self.add_canvas_btn.setCheckable(True)
        self.add_canvas_btn.setShortcut(QKeySequence('A'))
        self.add_canvas_btn.triggered.connect(self.use_add_canvas)

        # Insert Image Button
        insert_btn = QAction(QIcon('logos and icons/Tool Icons/insert_image_icon2.png'), '', self)
        insert_btn.setToolTip('''Insert Image Tool: 
        Key-I''')
        insert_btn.setShortcut(QKeySequence('I'))
        insert_btn.triggered.connect(self.insert_image)

        # ----add actions----#

        # Add toolbar actions
        self.toolbar.addAction(self.select_btn)
        self.toolbar.addAction(pan_btn)
        self.toolbar.addAction(self.path_btn)
        self.toolbar.addAction(self.erase_btn)
        self.toolbar.addAction(self.label_btn)
        self.toolbar.addAction(self.add_text_btn)
        self.toolbar.addAction(self.scale_btn)
        self.toolbar.addAction(hide_btn)
        self.toolbar.addAction(unhide_btn)
        self.toolbar.addAction(smooth_btn)
        self.toolbar.addAction(self.add_canvas_btn)
        self.toolbar.addAction(insert_btn)

        # Action Group
        self.action_group.addAction(self.select_btn)
        self.action_group.addAction(pan_btn)
        self.action_group.addAction(self.path_btn)
        self.action_group.addAction(self.erase_btn)
        self.action_group.addAction(self.label_btn)
        self.action_group.addAction(self.add_text_btn)
        self.action_group.addAction(self.scale_btn)
        self.action_group.addAction(hide_btn)
        self.action_group.addAction(unhide_btn)
        self.action_group.addAction(smooth_btn)
        self.action_group.addAction(self.add_canvas_btn)

    def create_toolbar3(self):
        #----toolbar widgets----#
        self.zoom_amounts = {'25%': 0.25,
                             '50%': 0.50,
                             '75%': 0.75,
                             '100%': 1.00,
                             '125%': 1.25,
                             '150%': 1.50,
                             '175%': 1.75,
                             '200%': 2.00,
                             '500%': 5.00,
                             'Fit On Screen': 'fit'}
        self.view_zoom_combo = QComboBox(self)
        self.view_zoom_combo.setFixedHeight(20)
        for zoom, actual in self.zoom_amounts.items():
            self.view_zoom_combo.addItem(zoom, actual)
        self.view_zoom_combo.setCurrentIndex(3)
        self.view_zoom_combo.currentIndexChanged.connect(self.use_zoom_view)

        self.rotate_sceen_spin = QSpinBox(self)
        self.rotate_sceen_spin.setFixedHeight(20)
        self.rotate_sceen_spin.setMinimum(-10000)
        self.rotate_sceen_spin.setMaximum(10000)
        self.rotate_sceen_spin.valueChanged.connect(self.use_rotate_screen)

        # Add widgets
        self.view_toolbar.addWidget(self.view_zoom_combo)
        self.view_toolbar.addWidget(self.rotate_sceen_spin)

    def create_view(self):
        # QGraphicsView Logic (messy but whatever)
        self.canvas_view = CustomGraphicsView(self.canvas,
                                              self.path_btn,
                                              self.label_btn,
                                              self.close_subpath_check_btn,
                                              self.add_text_btn,
                                              self.erase_btn,
                                              self.add_canvas_btn,
                                              self.select_btn,
                                              self.scale_btn)
        self.canvas_view.setRenderHint(QPainter.Antialiasing)
        self.canvas_view.setRenderHint(QPainter.TextAntialiasing)
        self.canvas_view.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.canvas_view.setScene(self.canvas)
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.font_letter_spacing_spin.value())
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

        # Context menu for view
        name_action = QAction('Name', self)
        name_action.triggered.connect(self.use_name_item)
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.triggered.connect(self.use_duplicate)
        group_action = QAction('Group Selected', self)
        group_action.triggered.connect(self.create_group)
        ungroup_action = QAction('Ungroup Selected', self)
        ungroup_action.triggered.connect(self.ungroup_group)
        vectorize_action = QAction('Vectorize', self)
        vectorize_action.triggered.connect(self.use_vectorize)
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
        element_center_action = QAction('Set Default Center', self)
        element_center_action.triggered.connect(self.use_set_center)
        hide_action = QAction('Hide Selected', self)
        hide_action.triggered.connect(self.use_hide_item)
        unhide_action = QAction('Unhide All', self)
        unhide_action.triggered.connect(self.use_unhide_all)
        select_all_action = QAction('Select All', self)
        select_all_action.triggered.connect(self.use_select_all)
        sep1 = QAction(self)
        sep1.setSeparator(True)
        sep2 = QAction(self)
        sep2.setSeparator(True)
        sep3 = QAction(self)
        sep3.setSeparator(True)
        sep4 = QAction(self)
        sep4.setSeparator(True)

        self.canvas_view.addAction(name_action)
        self.canvas_view.addAction(sep1)
        self.canvas_view.addAction(duplicate_action)
        self.canvas_view.addAction(group_action)
        self.canvas_view.addAction(ungroup_action)
        self.canvas_view.addAction(sep3)
        self.canvas_view.addAction(raise_layer_action)
        self.canvas_view.addAction(lower_layer_action)
        self.canvas_view.addAction(lock_action)
        self.canvas_view.addAction(unlock_action)
        self.canvas_view.addAction(center_action)
        self.canvas_view.addAction(element_center_action)
        self.canvas_view.addAction(sep4)
        self.canvas_view.addAction(hide_action)
        self.canvas_view.addAction(unhide_action)
        self.canvas_view.addAction(select_all_action)

    def create_default_objects(self):
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.font_letter_spacing_spin.value())
        font.setBold(True if self.bold_btn.isChecked() else False)
        font.setItalic(True if self.italic_btn.isChecked() else False)
        font.setUnderline(True if self.underline_btn.isChecked() else False)

        # Drawing paper
        self.paper = CanvasItem(0, 0, 1000, 700)
        self.paper.setZValue(-1)
        self.paper.setToolTip('Canvas 1')
        self.canvas.addItem(self.paper)
        self.last_paper = self.paper
        self.stored_center_item = self.paper.boundingRect()

        # Text on paper
        self.paper_text = EditableTextBlock("""Run #:
Page #:
Competition:
Athlete:
Date:""")
        self.paper_text.setPos(2, 2)
        self.paper_text.setDefaultTextColor(QColor('black'))
        self.paper_text.setFont(font)
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.paper_text.setZValue(0)
        self.canvas.addItem(self.paper_text)

        self.text_item = CanvasTextItem('Canvas 1', self.paper)
        self.text_item.setVisible(False)

        self.use_refit_screen()

    def keyPressEvent(self, event):
        if event.key() == QKeySequence('Backspace'):
            for item in self.canvas.selectedItems():
                command = RemoveItemCommand(self.canvas, item)
                self.canvas.addCommand(command)

        elif event.key() == QKeySequence('Escape'):
            self.canvas.clearSelection()

            for action in self.action_group.actions():
                action.setChecked(False)

            self.select_btn.setChecked(True)
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
                try:
                    self.properties_tab.close()
                    self.libraries_tab.close()
                    self.layers_tab.close()
                    self.characters_tab.close()
                    self.image_trace.close()
                    self.canvas_tab.close()
                    self.add_canvas_dialog.close()

                except Exception:
                    pass

                event.accept()

            else:
                event.ignore()

        else:
            try:
                self.properties_tab.close()
                self.libraries_tab.close()
                self.layers_tab.close()
                self.characters_tab.close()
                self.image_trace.close()
                self.canvas_tab.close()
                self.add_canvas_dialog.close()

            except Exception:
                pass

            event.accept()

    def update_pen(self):
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2, Qt.PenJoinStyle.RoundJoin))
        self.canvas_view.update_stroke_fill_color(QBrush(QColor(self.fill_color.get())))

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                if isinstance(item, CustomPathItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    if self.close_subpath_check_btn.isChecked():
                        path = item.path()
                        if path.elementCount() > 0:
                            command = CloseSubpathCommand(item, self.canvas)
                            self.canvas.addCommand(command)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1,
                               data2)
                    item.setPen(pen)
                    item.setBrush(QColor(self.fill_color.get()))

                elif isinstance(item, CustomCircleItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)
                    item.setPen(pen)

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
                                child.setBrush(QColor(self.fill_color.get()))

                            elif isinstance(child, CustomRectangleItem):
                                index1 = self.stroke_style_combo.currentIndex()
                                data1 = self.stroke_style_combo.itemData(index1)
                                index2 = self.stroke_pencap_combo.currentIndex()
                                data2 = self.stroke_pencap_combo.itemData(index2)

                                pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1,
                                           data2)
                                child.setPen(pen)
                                child.setBrush(QColor(self.fill_color.get()))

                elif isinstance(item, CustomRectangleItem):
                    index1 = self.stroke_style_combo.currentIndex()
                    data1 = self.stroke_style_combo.itemData(index1)
                    index2 = self.stroke_pencap_combo.currentIndex()
                    data2 = self.stroke_pencap_combo.itemData(index2)

                    pen = QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)
                    item.setPen(pen)
                    item.setBrush(QColor(self.fill_color.get()))

    def update_font(self):
        font = QFont()
        font.setFamily(self.font_choice_combo.currentText())
        font.setPixelSize(self.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.font_letter_spacing_spin.value())
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

    def update_appearance_ui(self):
        self.x_pos_spin.blockSignals(True)
        self.y_pos_spin.blockSignals(True)
        self.width_scale_spin.blockSignals(True)
        self.height_scale_spin.blockSignals(True)
        self.rotate_item_spin.blockSignals(True)
        self.canvas_tab.canvas_x_entry.blockSignals(True)
        self.canvas_tab.canvas_y_entry.blockSignals(True)
        self.canvas_tab.canvas_name_entry.blockSignals(True)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(True)
        self.stroke_size_spin.blockSignals(True)
        self.stroke_style_combo.blockSignals(True)
        self.stroke_pencap_combo.blockSignals(True)
        self.fill_color_btn.blockSignals(True)
        self.outline_color_btn.blockSignals(True)
        self.font_choice_combo.blockSignals(True)
        self.font_color_btn.blockSignals(True)
        self.font_size_spin.blockSignals(True)
        self.font_letter_spacing_spin.blockSignals(True)
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)
        self.layer_spin.blockSignals(True)

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                self.selection_label.setText(item.toolTip())

        else:
            self.selection_label.setText('No Selection')
            self.x_pos_spin.setValue(0)
            self.y_pos_spin.setValue(0)
            self.rotate_item_spin.setValue(0)
            self.width_scale_spin.setValue(10.0)
            self.height_scale_spin.setValue(10.0)
            self.layer_spin.setValue(0)

        for item in self.canvas.selectedItems():
            self.x_pos_spin.setValue(int(item.x()))
            self.y_pos_spin.setValue(int(item.y()))
            self.rotate_item_spin.setValue(int(item.rotation()))
            self.width_scale_spin.setValue(float(item.transform().m11() * 10))
            self.height_scale_spin.setValue(float(item.transform().m22() * 10))
            self.layer_spin.setValue(int(item.zValue()))

            if isinstance(item, CustomPathItem):
                pen = item.pen()
                brush = item.brush()

                # Set Colors
                self.outline_color_btn.setStyleSheet(f'background-color: {pen.color().name()};')
                self.outline_color.set(pen.color().name())
                self.fill_color_btn.setStyleSheet(f'background-color: {brush.color().name() if brush.color().alpha() != 0 else Qt.transparent};')
                self.fill_color.set(brush.color().name() if brush.color().alpha() != 0 else Qt.transparent)

                # Set Values
                self.stroke_size_spin.setValue(pen.width())

                for index, (style, value) in enumerate(self.stroke_style_options.items()):
                    if pen.style() == value:
                        self.stroke_style_combo.setCurrentIndex(index)

                for i, (s, v) in enumerate(self.stroke_pencap_options.items()):
                    if pen.capStyle() == v:
                        self.stroke_pencap_combo.setCurrentIndex(i)

            elif isinstance(item, CanvasItem):
                self.canvas_tab.canvas_x_entry.setValue(int(item.boundingRect().width()))
                self.canvas_tab.canvas_y_entry.setValue(int(item.boundingRect().height()))

                for child in item.childItems():
                    if isinstance(child, CanvasTextItem):
                        self.canvas_tab.canvas_name_entry.setText(child.text())

            elif isinstance(item, CustomCircleItem):
                if item.childItems():
                    for child in item.childItems():
                        if isinstance(child, CustomRectangleItem):
                            pen = child.pen()
                            brush = child.brush()

                            # Set Colors
                            self.outline_color_btn.setStyleSheet(f'background-color: {pen.color().name()};')
                            self.outline_color.set(pen.color().name())
                            self.fill_color_btn.setStyleSheet(
                                f'background-color: {brush.color().name() if brush.color().alpha() != 0 else Qt.transparent};')
                            self.fill_color.set(brush.color().name() if brush.color().alpha() != 0 else Qt.transparent)

                        else:
                            pen = item.pen()
                            brush = item.brush()

                            # Set Colors
                            self.outline_color_btn.setStyleSheet(f'background-color: {pen.color().name()};')
                            self.outline_color.set(pen.color().name())
                            self.fill_color_btn.setStyleSheet(
                                f'background-color: {brush.color().name() if brush.color().alpha() != 0 else Qt.transparent};')
                            self.fill_color.set(brush.color().name() if brush.color().alpha() != 0 else Qt.transparent)

                            # Set Values
                            self.stroke_size_spin.setValue(pen.width())

                            for index, (style, value) in enumerate(self.stroke_style_options.items()):
                                if pen.style() == value:
                                    self.stroke_style_combo.setCurrentIndex(index)

                            for i, (s, v) in enumerate(self.stroke_pencap_options.items()):
                                if pen.capStyle() == v:
                                    self.stroke_pencap_combo.setCurrentIndex(i)

                else:
                    pen = item.pen()
                    brush = item.brush()

                    # Set Colors
                    self.outline_color_btn.setStyleSheet(f'background-color: {pen.color().name()};')
                    self.outline_color.set(pen.color().name())
                    self.fill_color_btn.setStyleSheet(
                        f'background-color: {brush.color().name() if brush.color().alpha() != 0 else Qt.transparent};')
                    self.fill_color.set(brush.color().name() if brush.color().alpha() != 0 else Qt.transparent)

                    # Set Values
                    self.stroke_size_spin.setValue(pen.width())

                    for index, (style, value) in enumerate(self.stroke_style_options.items()):
                        if pen.style() == value:
                            self.stroke_style_combo.setCurrentIndex(index)

                    for i, (s, v) in enumerate(self.stroke_pencap_options.items()):
                        if pen.capStyle() == v:
                            self.stroke_pencap_combo.setCurrentIndex(i)

            elif isinstance(item, EditableTextBlock):
                font = item.font()
                color = item.defaultTextColor().name()

                self.font_color_btn.setStyleSheet(f'background-color: {color};')
                self.font_choice_combo.setCurrentText(font.family())
                self.font_size_spin.setValue(font.pixelSize())
                self.font_letter_spacing_spin.setValue(int(font.letterSpacing()))
                self.bold_btn.setChecked(True if font.bold() else False)
                self.italic_btn.setChecked(True if font.italic() else False)
                self.underline_btn.setChecked(True if font.underline() else False)

        self.x_pos_spin.blockSignals(False)
        self.y_pos_spin.blockSignals(False)
        self.rotate_item_spin.blockSignals(False)
        self.width_scale_spin.blockSignals(False)
        self.height_scale_spin.blockSignals(False)
        self.canvas_tab.canvas_x_entry.blockSignals(False)
        self.canvas_tab.canvas_y_entry.blockSignals(False)
        self.canvas_tab.canvas_name_entry.blockSignals(False)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(False)
        self.stroke_size_spin.blockSignals(False)
        self.stroke_style_combo.blockSignals(False)
        self.stroke_pencap_combo.blockSignals(False)
        self.fill_color_btn.blockSignals(False)
        self.outline_color_btn.blockSignals(False)
        self.font_choice_combo.blockSignals(False)
        self.font_color_btn.blockSignals(False)
        self.font_size_spin.blockSignals(False)
        self.font_letter_spacing_spin.blockSignals(False)
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)
        self.layer_spin.blockSignals(False)

    def stroke_color_chooser(self):
        color_dialog = CustomColorPicker()
        color_dialog.setWindowTitle('Stroke Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.outline_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.outline_color.set(color.name())

    def fill_color_chooser(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Fill Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.fill_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.fill_color.set(color.name())

    def font_color_chooser(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Font Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.font_color_btn.setStyleSheet(f'background-color: {color.name()}; border: None')
            self.font_color.set(color.name())

    def use_select(self):
        self.canvas_view.setDragMode(QGraphicsView.RubberBandDrag)

    def use_select_all(self):
        for item in self.canvas.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)

    def use_pan(self):
        self.canvas_view.setDragMode(QGraphicsView.ScrollHandDrag)

    def use_path(self):
        self.path_btn.setChecked(True)

    def use_erase(self):
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        self.fill_color.set(Qt.transparent)
        self.outline_color.set('white')

        self.canvas_view.update_pen(QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))
        self.canvas_view.update_stroke_fill_color(QBrush(QColor(self.fill_color.get())))

        self.outline_color_btn.setStyleSheet(f'background-color: white;')
        self.fill_color_btn.setStyleSheet('background-color: transparent;')

        self.erase_btn.setChecked(True)

    def use_label(self):
        self.label_btn.setChecked(True)

    def use_text(self):
        self.add_text_btn.setChecked(True)

    def use_refit_screen(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                self.canvas_view.fitInView(item.sceneBoundingRect(), Qt.KeepAspectRatio)

    def use_zoom_view(self):
        index = self.view_zoom_combo.currentIndex()
        zoom = self.view_zoom_combo.itemData(index)

        if zoom == 'fit':
            self.use_refit_screen()

        else:
            self.canvas_view.resetTransform()
            self.canvas_view.scale(zoom, zoom)
            self.canvas_view.rotate(self.rotate_sceen_spin.value())

    def use_rotate_screen(self, value):
        index = self.view_zoom_combo.currentIndex()
        zoom = self.view_zoom_combo.itemData(index)

        if zoom == 'fit':
            self.use_refit_screen()

        else:
            self.canvas_view.resetTransform()
            self.canvas_view.scale(zoom, zoom)
            self.canvas_view.rotate(self.rotate_sceen_spin.value())

    def use_set_layer(self):
        for items in self.canvas.selectedItems():
            items.setZValue(self.layer_spin.value())

    def use_hide_layer(self):
        for item in self.canvas.items():
            if int(item.zValue()) == self.layer_spin.value():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.setVisible(False)

    def use_unhide_layer(self):
        for item in self.canvas.items():
            if int(item.zValue()) == self.layer_spin.value():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.setVisible(True)

    def use_raise_layer(self):
        for item in self.canvas.selectedItems():
            item.setZValue(item.zValue() + 1.0)

    def use_lower_layer(self):
        for item in self.canvas.selectedItems():
            if item.zValue() <= 0:
                QMessageBox.critical(self, 'Lower Layer', "You cannot lower this Element any lower.")

            else:
                item.setZValue(item.zValue() - 1.0)

    def use_bring_to_front(self):
        selected_items = self.canvas.selectedItems()
        if selected_items:
            max_z = max([item.zValue() for item in self.canvas.items()])
            for item in selected_items:
                item.setZValue(max_z + 1)

    def use_vectorize(self):
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
                        vtracer.convert_image_to_svg_py(item.return_filename(),
                                                        f'V-C STOR/{entry}.svg',
                                                        colormode=self.colormode_combo.itemData(self.colormode_combo.currentIndex()),  # ["color"] or "binary"
                                                        hierarchical='cutout',  # ["stacked"] or "cutout"
                                                        mode=self.mode_combo.itemData(self.mode_combo.currentIndex()),  # ["spline"] "polygon", or "none"
                                                        filter_speckle=4,  # default: 4
                                                        color_precision=6,  # default: 6
                                                        layer_difference=16,  # default: 16
                                                        corner_threshold=self.corner_threshold_spin.value(),  # default: 60
                                                        length_threshold=4.0,  # in [3.5, 10] default: 4.0
                                                        max_iterations=10,  # default: 10
                                                        splice_threshold=45,  # default: 45
                                                        path_precision=3  # default: 8
                                                        )

                        # Set cursor back
                        self.setCursor(Qt.ArrowCursor)

                        # Display information
                        QMessageBox.information(self, "Convert Finished", "Vector converted successfully.")

                        # Add the item to the scene
                        item = CustomSvgItem(f'V-C STOR/{entry}.svg')
                        item.store_filename(f'V-C STOR/{entry}.svg')
                        add_command = AddItemCommand(self.canvas, item)
                        self.canvas.addCommand(add_command)
                        self.create_item_attributes(item)
                        item.setToolTip('Vector Element')

                except Exception as e:
                    # Set cursor back
                    self.setCursor(Qt.ArrowCursor)

                    QMessageBox.critical(self, "Convert Error", f"Failed to convert bitmap to vector: {e}")

            else:
                pass

    def use_duplicate(self):
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

    def use_set_item_x(self, value):
        for item in self.canvas.selectedItems():
            item.setPos(value, item.y())

    def use_set_item_y(self, value):
        for item in self.canvas.selectedItems():
            item.setPos(item.x(), value)

    def use_scale_x(self, value):
        self.use_scale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def use_scale_y(self, value):
        self.use_scale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def use_scale(self, x_value, y_value):
        try:
            x_value = float(x_value / 10)
            y_value = float(y_value / 10)
            items = self.canvas.selectedItems()
            for item in items:
                if isinstance(item, CanvasItem):
                    pass

                else:
                    command = TransformScaleCommand(item, x_value, y_value, item.transform().m11(), item.transform().m22())
                    self.canvas.addCommand(command)

        except Exception as e:
            pass

    def use_scale_tool(self):
        self.scale_btn.setChecked(True)

    def use_rotate(self, value):
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
                command = RotateCommand(item, item.rotation(), value)
                self.canvas.addCommand(command)

    def use_change_opacity(self, value):
        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.opacity_slider.maximum()

        # Apply the effect to selected items
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                pass

            else:
                command = OpacityCommand(item, item.opacity(), opacity)
                self.canvas.addCommand(command)

    def use_drop_shadow(self):
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
        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                rect = self.stored_center_item
                center = rect.center()

                item.setTransformOriginPoint(item.boundingRect().center())
                new_pos = center - item.boundingRect().center()
                item.setPos(new_pos)

    def use_set_center(self):
        if not self.canvas.selectedItems():
            QMessageBox.information(self, 'Set Default Center', 'Select an item to set the default center to.')

        else:
            self.stored_center_item = self.canvas.selectedItemsBoundingRect()

    def use_display_center(self):
        # Create the ellipse item
        ellipse_item = CenterPointItem(0, 0, 30, 30)
        ellipse_item.setBrush(QBrush(QColor(Qt.blue)))  # Set brush color to blue
        ellipse_item.setToolTip('Current Center Point')

        # Calculate the center of the stored item
        center = self.stored_center_item.center()

        # Position the ellipse at the calculated center
        ellipse_item.setPos(center.x() - 15, center.y() - 15)  # Adjust for ellipse size

        # Set Z-value
        ellipse_item.setZValue(10000)

        # Add the ellipse to the scene
        command = AddItemCommand(self.canvas, ellipse_item)
        self.canvas.addCommand(command)

    def use_add_canvas(self):
        self.add_canvas_dialog = AddCanvasDialog(self.canvas, self.last_paper)
        self.add_canvas_dialog.show()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                for items in item.childItems():
                    if isinstance(items, CanvasTextItem):
                        items.setVisible(True)

                    items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                    items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def use_smooth_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                try:
                    smoothed_path = item.smooth_path(item.path())

                    add_command = SmoothPathCommand(self.canvas, item, smoothed_path, item.path())
                    self.canvas.addCommand(add_command)

                except Exception as e:
                    QMessageBox.critical(self, "Smooth Path", "Cannot smooth path anymore.")
                    self.canvas.undo()

    def use_close_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                command = CloseSubpathCommand(item, self.canvas)
                self.canvas.addCommand(command)

    def use_fill_transparent(self):
        self.fill_color_btn.setStyleSheet('background-color: transparent')
        self.fill_color.set(Qt.transparent)

        for item in self.canvas.selectedItems():
            if isinstance(item, EditableTextBlock):
                pass

            elif isinstance(item, CustomPixmapItem):
                pass

            elif isinstance(item, CustomSvgItem):
                pass

            elif isinstance(item, CustomGraphicsItemGroup):
                pass

            elif isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CustomCircleItem):
                item.setBrush(QBrush(QColor(Qt.transparent)))

                if item.childItems():
                    for child in item.childItems():
                        if isinstance(child, CustomRectangleItem):
                            child.setBrush(QBrush(QColor(Qt.transparent)))

            else:
                item.setBrush(QBrush(QColor(Qt.transparent)))

    def use_hide_item(self):
        for item in self.canvas.selectedItems():
            command = HideCommand(item, True, False)
            self.canvas.addCommand(command)

    def use_unhide_all(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasTextItem):
                pass

            else:
                if not item.isVisible():
                    command = HideCommand(item, False, True)
                    self.canvas.addCommand(command)

                else:
                    pass

    def use_trick_table(self):
        item = EditableTextBlock(' ')
        item.insert_table(11, 3)
        item.setToolTip('Trick Table')

        command = AddItemCommand(self.canvas, item)
        self.canvas.addCommand(command)
        self.create_item_attributes(item)

    def use_name_item(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                if item.childItems():
                    pass

                else:
                    pass

            else:
                entry, ok = QInputDialog.getText(self, 'Name Element', 'Enter a name for the selected elements:')

                if ok:
                    command = NameCommand(item, item.toolTip(), entry)
                    self.canvas.addCommand(command)

                    self.update_appearance_ui()

    def lock_item(self):
        item = self.canvas.selectedItems()

        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable, False)

            if isinstance(items, CustomGraphicsItemGroup):
                items.set_locked()

    def unlock_item(self):
        item = self.canvas.selectedItems()

        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable)

            if isinstance(items, CustomGraphicsItemGroup):
                items.set_unlocked()

    def permanent_lock_item(self):
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
                        items.setToolTip('Permanently Locked Element')

                    if isinstance(items, CustomGraphicsItemGroup):
                        items.set_locked()
                        items.setToolTip('Permanently Locked Element')

                    if isinstance(items, CanvasItem):
                        pass

                    else:
                        items.setToolTip('Permanently Locked MPRUN Element')

            else:
                pass

    def insert_image(self):
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

                add_command = AddItemCommand(self.canvas, svg_item)
                self.canvas.addCommand(add_command)
                svg_item.setToolTip('Imported SVG')

                self.create_item_attributes(svg_item)

            elif file_path.endswith('.py'):
                with open(file_path, 'r') as f:
                    contents = f.read()
                    exec(contents)

            else:
                image1 = QPixmap(file_path)
                image2 = CustomPixmapItem(image1)
                image2.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, image2)
                self.canvas.addCommand(add_command)
                image2.setToolTip('Imported Pixmap')

                self.create_item_attributes(image2)

    def export_canvas(self, filename, selected_item):
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

                if len(item) > 1:
                    # Set flags for group
                    group.setFlag(QGraphicsItem.ItemIsMovable)
                    group.setFlag(QGraphicsItem.ItemIsSelectable)

                    # Add group
                    self.canvas.addItem(group)

                    for items in item:
                        # Set flag
                        items.setFlag(QGraphicsItem.ItemIsSelectable, False)

                        # Add items to group
                        group.addToGroup(items)
                        group.setToolTip('Group')

                else:
                    pass

    def ungroup_group(self):
        for group in self.canvas.selectedItems():
            if isinstance(group, CustomGraphicsItemGroup):
                if group.childItems():
                    for child in group.childItems():
                        child.setFlag(QGraphicsItem.ItemIsSelectable)
                        child.setToolTip(child.toolTip())
                        child.setParentItem(child)

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
        self.last_paper = self.paper
        self.stored_center_item = self.paper.boundingRect()

        # Refit screen
        self.use_refit_screen()

        if default_text == '':
            self.canvas.removeItem(self.paper_text)

        for item in self.canvas.items():
            if isinstance(item, CustomGraphicsItemGroup):
                item.set_grid_size(grid_size)
                self.gsnap_grid_spin.setValue(grid_size)
                self.gsnap_grid_size = grid_size

    def show_version(self):
        app = VersionWin()
        app.mainloop()

    def display_choosen_tab(self, tab_name):
        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == tab_name:
                break

            else:
                if tab_name == 'Properties':
                    self.tab_view.addTab(self.properties_tab, tab_name)
                    self.tab_view.setCurrentWidget(self.properties_tab)

                elif tab_name == 'Layers':
                    self.tab_view.addTab(self.layers_tab, tab_name)
                    self.tab_view.setCurrentWidget(self.layers_tab)

                elif tab_name == 'Libraries':
                    self.tab_view.addTab(self.libraries_tab, tab_name)
                    self.tab_view.setCurrentWidget(self.libraries_tab)

                elif tab_name == 'Characters':
                    self.tab_view.addTab(self.characters_tab, tab_name)
                    self.tab_view.setCurrentWidget(self.characters_tab)

                elif tab_name == 'Image Trace':
                    self.tab_view.addTab(self.image_trace, tab_name)
                    self.tab_view.setCurrentWidget(self.image_trace)

                elif tab_name == 'Canvas':
                    self.tab_view.addTab(self.canvas_tab, tab_name)
                    self.tab_view.setCurrentWidget(self.canvas_tab)


if __name__ == '__main__':
    app = QApplication([])

    sshFile = "main_style.css"
    with open(sshFile, "r") as fh:
        app.setStyleSheet(fh.read())

    window = MPRUN()
    window.show()
    app.exec_()
