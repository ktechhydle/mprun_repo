import os.path
import time

from src.scripts.imports import *
from src.scripts.app_internal import *
from src.scripts.app_screens import *
from src.scripts.styles import *
from src.framework.custom_classes import *
from src.framework.undo_commands import *
from src.framework.graphics_framework import *
from src.gui.custom_widgets import *
from src.gui.custom_dialogs import *
from src.gui.libraries import *

class MPRUN(QMainWindow):
    def __init__(self):
        super(MPRUN, self).__init__()
        # Creating the main window
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_logoV3.png'))
        self.setGeometry(0, 0, 1500, 800)
        self.setAcceptDrops(True)

        # File
        self.file_name = None

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
        self.undo_stack.setUndoLimit(200)

        # Create GUI
        self.create_actions_dict()
        self.create_initial_canvas()
        self.create_menu()
        self.init_toolbars()
        self.create_toolbar1()
        self.create_toolbar2()
        self.create_toolbar3()
        self.create_view()
        self.create_default_objects()
        self.update()

        self.show()

    def closeEvent(self, event):
        if self.canvas.modified:
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox(self)
            confirmation_dialog.setWindowTitle('Close Document')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
            confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
            confirmation_dialog.setDefaultButton(QMessageBox.Save)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            # If the user clicked Yes, close the window
            if result == QMessageBox.Discard:
                try:
                    self.undo_stack.clear()
                    self.w.close()
                    event.accept()

                except Exception:
                    pass

            elif result == QMessageBox.Save:
                success = self.save()

                if success:
                    try:
                        self.undo_stack.clear()
                        self.w.close()
                        event.accept()

                    except Exception:
                        pass

                else:
                    event.ignore()

            else:
                event.ignore()

        else:
            try:
                self.undo_stack.clear()
                self.w.close()
                event.accept()

            except Exception:
                pass

    def create_actions_dict(self):
        self.actions = {}

    def create_initial_canvas(self):
        # Canvas, canvas color
        self.canvas = CustomGraphicsScene(self.undo_stack)
        self.canvas.setParentWindow(self)
        self.canvas.selectionChanged.connect(self.update_appearance_ui)
        self.canvas.selectionChanged.connect(self.update_transform_ui)
        self.canvas.itemsMoved.connect(self.update_transform_ui)
        self.setWindowTitle(f'{os.path.basename(self.canvas.manager.filename)} - MPRUN')

    def create_menu(self):
        # Create menus
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('&File')
        self.tool_menu = self.menu_bar.addMenu('&Tools')
        self.edit_menu = self.menu_bar.addMenu('&Edit')
        self.object_menu = self.menu_bar.addMenu('&Object')
        self.selection_menu = self.menu_bar.addMenu('&Selection')
        self.help_menu = self.menu_bar.addMenu('&Help')

        # Create file actions
        insert_action = QAction('Insert', self)
        insert_action.setShortcut(QKeySequence('I'))
        insert_action.triggered.connect(self.insert_image)

        add_canvas_action = QAction('Add Canvas', self)
        add_canvas_action.setShortcut(QKeySequence('A'))
        add_canvas_action.triggered.connect(self.use_add_canvas)

        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence('Ctrl+N'))
        new_action.triggered.connect(self.new)

        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence('Ctrl+O'))
        open_action.triggered.connect(self.open)

        self.open_recent_menu = QMenu('Open Recent')

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.save)

        saveas_action = QAction('Save As', self)
        saveas_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        saveas_action.triggered.connect(self.saveas)

        export_action = QAction('Export Canvas', self)
        export_action.setShortcut(QKeySequence('Ctrl+E'))
        export_action.triggered.connect(self.choose_export)

        export_multiple_action = QAction('Export All', self)
        export_multiple_action.setShortcut(QKeySequence('Ctrl+Shift+E'))
        export_multiple_action.triggered.connect(self.choose_multiple_export)

        close_action = QAction('Close', self)
        close_action.triggered.connect(lambda: self.close())

        # Create tools submenus and actions
        drawing_menu = self.tool_menu.addMenu('Drawing')
        path_menu = self.tool_menu.addMenu('Path')
        characters_menu = self.tool_menu.addMenu('Characters')
        image_menu = self.tool_menu.addMenu('Image')
        view_menu = self.tool_menu.addMenu('View')

        select_action = QAction('Select', self)
        select_action.setShortcut(QKeySequence(Qt.Key_Space))
        select_action.triggered.connect(self.use_select)

        pan_action = QAction('Pan', self)
        pan_action.setShortcut(QKeySequence('P'))
        pan_action.triggered.connect(self.use_pan)

        rotate_view_action = QAction('Rotate', self)
        rotate_view_action.triggered.connect(lambda: self.rotate_scene_spin.setFocus())

        zoom_view_action = QAction('Zoom', self)
        zoom_view_action.triggered.connect(lambda: self.view_zoom_spin.setFocus())

        path_action = QAction('Path Draw', self)
        path_action.setShortcut(QKeySequence('L'))
        path_action.triggered.connect(self.use_path)
        path_action.triggered.connect(self.update)

        pen_action = QAction('Pen Draw', self)
        pen_action.setShortcut(QKeySequence('Ctrl+L'))
        pen_action.triggered.connect(self.use_pen_tool)
        pen_action.triggered.connect(self.update)

        linelabel_action = QAction('Line and Label', self)
        linelabel_action.setShortcut(QKeySequence('T'))
        linelabel_action.triggered.connect(self.use_label)
        linelabel_action.triggered.connect(self.update)

        text_action = QAction('Text', self)
        text_action.setShortcut(QKeySequence('Ctrl+T'))
        text_action.triggered.connect(self.use_text)
        text_action.triggered.connect(self.update)

        smooth_action = QAction('Smooth Path', self)
        smooth_action.triggered.connect(self.use_smooth_path)

        close_subpath_action = QAction('Close Path', self)
        close_subpath_action.triggered.connect(self.use_close_path)

        sculpt_path_action = QAction('Sculpt Path', self)
        sculpt_path_action.setShortcut(QKeySequence('S'))
        sculpt_path_action.triggered.connect(self.use_sculpt_path)

        # Create edit actions
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.canvas.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Shift+Z'))
        redo_action.triggered.connect(self.canvas.redo)

        delete_action = QAction('Delete', self)
        delete_action.setShortcut(QKeySequence('Backspace'))
        delete_action.triggered.connect(self.use_delete)

        hard_delete_action = QAction('Hard Delete', self)
        hard_delete_action.setShortcut(QKeySequence('Ctrl+Shift+Backspace'))
        hard_delete_action.triggered.connect(self.use_hard_delete)

        # Create object actions
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.setShortcut(QKeySequence("D"))
        duplicate_action.triggered.connect(self.use_duplicate)

        scale_action = QAction('Scale', self)
        scale_action.setShortcut(QKeySequence('Q'))
        scale_action.triggered.connect(self.use_scale_tool)

        flip_horizontal_action = QAction('Flip Horizontal', self)
        flip_horizontal_action.setShortcut(QKeySequence(''))
        flip_horizontal_action.triggered.connect(self.use_flip_horizontal)

        flip_vertical_action = QAction('Flip Vertical', self)
        flip_vertical_action.setShortcut(QKeySequence(''))
        flip_vertical_action.triggered.connect(self.use_flip_vertical)

        mirror_horizontal_action = QAction('Mirror Horizontal', self)
        mirror_horizontal_action.setShortcut(QKeySequence('M+H'))
        mirror_horizontal_action.triggered.connect(lambda: self.use_mirror('h'))

        mirror_vertical_action = QAction('Mirror Vertical', self)
        mirror_vertical_action.setShortcut(QKeySequence('M+V'))
        mirror_vertical_action.triggered.connect(lambda: self.use_mirror('v'))

        image_trace_action = QAction('Trace Image', self)
        image_trace_action.triggered.connect(self.use_vectorize)

        raise_layer_action = QAction('Raise Layer', self)
        raise_layer_action.setShortcut(QKeySequence('Up'))
        raise_layer_action.triggered.connect(self.use_raise_layer)

        lower_layer_action = QAction('Lower Layer', self)
        lower_layer_action.setShortcut(QKeySequence('Down'))
        lower_layer_action.triggered.connect(self.use_lower_layer)

        bring_to_front_action = QAction('Bring to Front', self)
        bring_to_front_action.triggered.connect(self.use_bring_to_front)

        hide_action = QAction('Hide Selected', self)
        hide_action.setShortcut(QKeySequence('H'))
        hide_action.triggered.connect(self.use_hide_item)

        unhide_action = QAction('Unhide All', self)
        unhide_action.setShortcut(QKeySequence('Ctrl+H'))
        unhide_action.triggered.connect(self.use_unhide_all)

        reset_action = QAction('Reset Item', self)
        reset_action.triggered.connect(self.use_reset_item)

        # Create selection menu actions
        select_all_action = QAction('Select All', self)
        select_all_action.setShortcut(QKeySequence('Ctrl+A'))
        select_all_action.triggered.connect(self.use_select_all)

        clear_selection_action = QAction('Clear Selection', self)
        clear_selection_action.setShortcut(QKeySequence('Escape'))
        clear_selection_action.triggered.connect(self.use_escape)

        select_paths_action = QAction('Select Paths', self)
        select_paths_action.triggered.connect(lambda: self.use_selection_mode('path'))

        select_text_action = QAction('Select Text', self)
        select_text_action.triggered.connect(lambda: self.use_selection_mode('text'))

        select_leaderline_action = QAction('Select Leader Lines', self)
        select_leaderline_action.triggered.connect(lambda: self.use_selection_mode('leaderline'))

        select_groups_action = QAction('Select Groups', self)
        select_groups_action.triggered.connect(lambda: self.use_selection_mode('group'))

        select_pixmaps_action = QAction('Select Pixmaps', self)
        select_pixmaps_action.triggered.connect(lambda: self.use_selection_mode('pixmap'))

        select_svgs_action = QAction('Select SVGs', self)
        select_svgs_action.triggered.connect(lambda: self.use_selection_mode('svg'))

        select_canvases_action = QAction('Select Canvases', self)
        select_canvases_action.triggered.connect(lambda: self.use_selection_mode('canvas'))

        # Create help menu actions
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)

        show_version_action = QAction('Version', self)
        show_version_action.triggered.connect(self.show_version)

        find_action_action = QAction('Find Action', self)
        find_action_action.triggered.connect(self.show_find_action)

        # Add actions
        self.file_menu.addAction(add_canvas_action)
        self.file_menu.addAction(insert_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(new_action)
        self.file_menu.addAction(open_action)
        self.file_menu.addMenu(self.open_recent_menu)
        self.file_menu.addSeparator()
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_action)
        self.file_menu.addAction(export_multiple_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(close_action)

        self.edit_menu.addAction(undo_action)
        self.edit_menu.addAction(redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(delete_action)
        self.edit_menu.addAction(hard_delete_action)

        self.object_menu.addAction(raise_layer_action)
        self.object_menu.addAction(lower_layer_action)
        self.object_menu.addAction(bring_to_front_action)
        self.object_menu.addSeparator()
        self.object_menu.addAction(duplicate_action)
        self.object_menu.addAction(scale_action)
        self.object_menu.addSeparator()
        self.object_menu.addAction(flip_horizontal_action)
        self.object_menu.addAction(flip_vertical_action)
        self.object_menu.addAction(mirror_horizontal_action)
        self.object_menu.addAction(mirror_vertical_action)
        self.object_menu.addSeparator()
        self.object_menu.addAction(hide_action)
        self.object_menu.addAction(unhide_action)
        self.object_menu.addAction(reset_action)
        self.object_menu.addSeparator()

        self.selection_menu.addAction(select_all_action)
        self.selection_menu.addAction(clear_selection_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_paths_action)
        self.selection_menu.addAction(select_text_action)
        self.selection_menu.addAction(select_leaderline_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_groups_action)
        self.selection_menu.addAction(select_pixmaps_action)
        self.selection_menu.addAction(select_svgs_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_canvases_action)

        self.help_menu.addAction(about_action)
        self.help_menu.addAction(show_version_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(find_action_action)

        # Sub menu actions
        drawing_menu.addAction(path_action)
        drawing_menu.addAction(pen_action)
        drawing_menu.addAction(linelabel_action)

        path_menu.addAction(smooth_action)
        path_menu.addAction(close_subpath_action)
        path_menu.addAction(sculpt_path_action)

        characters_menu.addAction(text_action)

        image_menu.addAction(image_trace_action)

        view_menu.addAction(select_action)
        view_menu.addAction(pan_action)
        view_menu.addAction(rotate_view_action)
        view_menu.addAction(zoom_view_action)

        # Add to actions dict
        self.actions['Trace Image'] = image_trace_action
        self.actions['Select All'] = select_all_action
        self.actions['Smooth Path'] = smooth_action
        self.actions['Close Path'] = close_subpath_action
        self.actions['Sculpt Path'] = sculpt_path_action
        self.actions['Duplicate'] = duplicate_action
        self.actions['Reset Item'] = reset_action
        self.actions['Bring to Front'] = bring_to_front_action
        self.actions['Undo'] = undo_action
        self.actions['Redo'] = redo_action
        self.actions['Export Canvas'] = export_action
        self.actions['Export All'] = export_multiple_action
        self.actions['New'] = new_action
        self.actions['Save'] = save_action
        self.actions['Save As'] = saveas_action
        self.actions['Open'] = open_action

    def init_toolbars(self):
        # Toolbar
        self.toolbar = QToolBar('Toolset')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setFixedWidth(60)
        self.toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)
        self.toolbar.setFloatable(True)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Item toolbar
        self.item_toolbar = QToolBar('Control')
        self.item_toolbar.setIconSize(QSize(32, 32))
        self.item_toolbar.setMovable(False)
        self.item_toolbar.setAllowedAreas(Qt.TopToolBarArea)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.item_toolbar)

    def create_toolbar1(self):
        #----action toolbar widgets----#

        # Dock widget
        self.toolbox = CustomToolbox(self)
        self.toolbox.setFixedWidth(300)
        self.toolbox.setMinimumHeight(680)

        self.tab_view_dock = CustomDockWidget(self.toolbox, self)
        self.tab_view_dock.setWindowTitle('Actions')
        self.tab_view_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        # Properties Tab
        self.properties_tab = QWidget(self)
        self.properties_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.properties_tab.setFixedHeight(300)
        self.properties_tab.setFixedWidth(300)
        self.properties_tab_layout = QVBoxLayout()
        self.properties_tab.setLayout(self.properties_tab_layout)

        # Characters Tab
        self.characters_tab = QWidget()
        self.characters_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.characters_tab.setFixedHeight(185)
        self.characters_tab.setFixedWidth(300)
        self.characters_tab_layout = QVBoxLayout()
        self.characters_tab.setLayout(self.characters_tab_layout)

        # Vectorize Tab
        self.image_trace = QWidget()
        self.image_trace.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.image_trace.setFixedHeight(375)
        self.image_trace.setFixedWidth(300)
        self.image_trace_layout = QVBoxLayout()
        self.image_trace.setLayout(self.image_trace_layout)

        # Libraries Tab
        self.libraries_tab = LibraryWidget(self.canvas)
        self.libraries_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.libraries_tab.setFixedHeight(385)
        self.libraries_tab.setFixedWidth(300)

        # Canvas Tab
        self.canvas_tab = CanvasEditorPanel(self.canvas)
        self.canvas_tab.setFixedWidth(300)

        # Quick Actions Tab
        self.quick_actions_tab = QuickActionsPanel(self.canvas, self)
        self.quick_actions_tab.setFixedWidth(300)

        # Add tabs
        self.toolbox.addItem(self.properties_tab, 'Properties')
        self.toolbox.addItem(self.libraries_tab, 'Libraries')
        self.toolbox.addItem(self.characters_tab, 'Characters')
        self.toolbox.addItem(self.image_trace, 'Image Trace')
        self.toolbox.addItem(self.canvas_tab, 'Canvas')
        self.toolbox.addItem(self.quick_actions_tab, 'Quick Actions')

        # This next section is basically all the widgets for each tab
        # Some tabs don't have many widgets as they are subclassed in other files.

        # _____ Properties tab widgets _____
        self.selection_label = QLabel('No Selection')
        self.selection_label.setStyleSheet("QLabel { font-size: 12px; }")
        self.transform_separator = HorizontalSeparator()
        self.transform_label = QLabel('Transform', self)
        self.transform_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        self.transform_label.setAlignment(Qt.AlignLeft)
        appearence_label = QLabel('Appearance', self)
        appearence_label.setStyleSheet("QLabel { font-size: 12px; alignment: center; }")
        appearence_label.setAlignment(Qt.AlignLeft)

        self.rotation_label = QIconWidget('', 'ui/Tool Icons/rotate_icon.png', 20, 20)
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
        self.flip_horizontal_btn.clicked.connect(self.use_flip_horizontal)
        self.flip_vertical_btn = QPushButton(QIcon('ui/Tool Icons/flip_vertical_icon.png'), '')
        self.flip_vertical_btn.setToolTip('Flip vertical')
        self.flip_vertical_btn.setStyleSheet('border: none;')
        self.flip_vertical_btn.clicked.connect(self.use_flip_vertical)
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
        widget9.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))

        fill_label = QLabel('Fill')
        fill_label.setStyleSheet('color: white;')
        self.fill_color_btn = QColorButton(self)
        self.fill_color_btn.setButtonColor('#00ff00')
        self.fill_color_btn.setFixedWidth(28)
        self.fill_color_btn.setFixedHeight(26)
        self.fill_color_btn.setToolTip('Change the fill color')
        self.fill_color_btn.setShortcut(QKeySequence('Ctrl+2'))
        self.fill_color.set('#00ff00')
        self.fill_color_btn.clicked.connect(self.fill_color_chooser)
        self.fill_color_btn.clicked.connect(self.update_item_fill)
        widget5 = ToolbarHorizontalLayout()
        widget5.layout.addWidget(self.fill_color_btn)
        widget5.layout.addWidget(fill_label)
        widget5.layout.setContentsMargins(0, 14, 0, 0)

        self.stroke_color_btn = QColorButton(self)
        self.stroke_color_btn.setButtonColor(self.outline_color.get())
        self.stroke_color_btn.setFixedWidth(28)
        self.stroke_color_btn.setFixedHeight(26)
        self.stroke_color_btn.setToolTip('Change the stroke color')
        self.stroke_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.stroke_color_btn.clicked.connect(self.stroke_color_chooser)
        self.stroke_color_btn.clicked.connect(self.update_item_pen)
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
        self.opacity_btn.setIcon(QIcon('ui/UI Icons/opacity_icon.png'))
        self.opacity_btn.setIconSize(QSize(24, 24))
        self.opacity_btn.setStyleSheet('QPushButton:hover { background: none }')
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix('%')
        self.opacity_spin.setToolTip('Change the opacity')
        self.opacity_spin.valueChanged.connect(self.use_change_opacity)
        opacity_hlayout = ToolbarHorizontalLayout()
        opacity_hlayout.layout.addWidget(self.opacity_btn)
        opacity_hlayout.layout.addWidget(opacity_label)
        opacity_hlayout.layout.addWidget(self.opacity_spin)
        opacity_hlayout.layout.addSpacing(100)
        opacity_hlayout.layout.setContentsMargins(0, 14, 0, 0)

        #_____ Characters tab widgets _____
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
        self.font_color_btn = QColorButton(self)
        self.font_color_btn.setFixedWidth(90)
        self.font_color_btn.setToolTip('Change the font color')
        self.font_color_btn.setStyleSheet(f'background-color: black;')
        self.font_color_btn.clicked.connect(self.font_color_chooser)
        self.font_color_btn.clicked.connect(self.update_item_font)
        self.bold_btn = QPushButton('B', self)
        self.bold_btn.setToolTip('Set the font bold')
        self.bold_btn.setStyleSheet('font-weight: bold; font-size: 15px;')
        self.italic_btn = QPushButton('I', self)
        self.italic_btn.setToolTip('Set the font italic')
        self.italic_btn.setStyleSheet('font-style: italic; font-size: 15px;')
        self.underline_btn = QPushButton('U', self)
        self.underline_btn.setToolTip('Set the font underlined')
        self.underline_btn.setStyleSheet('text-decoration: underline; font-size: 15px;')
        self.bold_btn.setCheckable(True)
        self.italic_btn.setCheckable(True)
        self.underline_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.update_item_font)
        self.italic_btn.clicked.connect(self.update_item_font)
        self.underline_btn.clicked.connect(self.update_item_font)
        font_size_and_spacing_hlayout = ToolbarHorizontalLayout()
        font_size_and_spacing_hlayout.layout.addWidget(
            QIconWidget('', 'ui/UI Icons/Major/font_size_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout.addWidget(self.font_size_spin)
        font_size_and_spacing_hlayout.layout.addWidget(
            QIconWidget('', 'ui/UI Icons/Major/font_spacing_icon.svg', 20, 20))
        font_size_and_spacing_hlayout.layout.addWidget(self.font_letter_spacing_spin)
        font_size_and_spacing_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_style_hlayout = ToolbarHorizontalLayout()
        font_style_hlayout.layout.addWidget(self.bold_btn)
        font_style_hlayout.layout.addWidget(self.italic_btn)
        font_style_hlayout.layout.addWidget(self.underline_btn)
        font_style_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_color_hlayout = ToolbarHorizontalLayout()
        font_color_hlayout.layout.setContentsMargins(0, 0, 0, 0)
        font_color_hlayout.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        font_color_hlayout.layout.addWidget(QLabel('Color:'))
        font_color_hlayout.layout.addWidget(self.font_color_btn)

        #_____ Image Trace tab widgets _____
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
        image_tracehlayout1.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        image_tracehlayout1.layout.addWidget(colormode_label)
        image_tracehlayout1.layout.addWidget(self.colormode_combo)
        image_tracehlayout1.layout.setContentsMargins(0, 0, 0, 0)
        image_tracehlayout2 = ToolbarHorizontalLayout()
        image_tracehlayout2.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        image_tracehlayout2.layout.addWidget(mode_label)
        image_tracehlayout2.layout.addWidget(self.mode_combo)
        image_tracehlayout2.layout.setContentsMargins(0, 0, 0, 0)

        # If any changes are made, update them
        self.stroke_size_spin.valueChanged.connect(self.update_item_pen)
        self.stroke_style_combo.currentIndexChanged.connect(self.update_item_pen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.update_item_pen)
        self.join_style_combo.currentIndexChanged.connect(self.update_item_pen)
        self.font_size_spin.valueChanged.connect(self.update_item_font)
        self.font_letter_spacing_spin.valueChanged.connect(self.update_item_font)
        self.font_choice_combo.currentFontChanged.connect(self.update_item_font)
        self.font_choice_combo.currentTextChanged.connect(self.update_item_font)
        self.x_pos_spin.valueChanged.connect(self.use_set_item_pos)
        self.y_pos_spin.valueChanged.connect(self.use_set_item_pos)
        self.width_scale_spin.valueChanged.connect(self.use_scale_x)
        self.height_scale_spin.valueChanged.connect(self.use_scale_y)
        self.rotate_item_spin.valueChanged.connect(self.use_rotate)

        # Add action toolbar actions
        self.tab_view_dock.setWidget(self.toolbox)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tab_view_dock)

        # Properties Tab Widgets
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

        # Elements Tab Widgets
        self.characters_tab_layout.addWidget(self.font_choice_combo)
        self.characters_tab_layout.addWidget(font_size_and_spacing_hlayout)
        self.characters_tab_layout.addWidget(font_style_hlayout)
        self.characters_tab_layout.addWidget(font_color_hlayout)

        # Vectorize Tab Widgets
        self.image_trace_layout.addWidget(image_tracehlayout1)
        self.image_trace_layout.addWidget(image_tracehlayout2)
        self.image_trace_layout.addWidget(path_precision_label)
        self.image_trace_layout.addWidget(self.path_precision_spin)
        self.image_trace_layout.addWidget(QMoreOrLessLabel(self))
        self.image_trace_layout.addWidget(color_precision_label)
        self.image_trace_layout.addWidget(self.color_precision_spin)
        self.image_trace_layout.addWidget(corner_threshold_label)
        self.image_trace_layout.addWidget(self.corner_threshold_spin)

        # Add to actions dict
        self.actions['Change Stroke Color'] = self.stroke_color_btn
        self.actions['Change Fill Color'] = self.fill_color_btn
        self.actions['Change Font Color'] = self.font_color_btn
        self.actions['Open Library'] = self.libraries_tab.open_library_button
        self.actions['Reload Library'] = self.libraries_tab.reload_library_button
        self.actions['Enable Grid'] = self.quick_actions_tab.gsnap_check_btn

        # Default widget settings
        self.transform_separator.setHidden(True)
        self.transform_label.setHidden(True)
        self.x_pos_label.setHidden(True)
        self.x_pos_spin.setHidden(True)
        self.y_pos_label.setHidden(True)
        self.y_pos_spin.setHidden(True)
        self.width_transform_label.setHidden(True)
        self.height_transform_label.setHidden(True)
        self.width_scale_spin.setHidden(True)
        self.height_scale_spin.setHidden(True)
        self.flip_horizontal_btn.setHidden(True)
        self.flip_vertical_btn.setHidden(True)
        self.rotation_label.setHidden(True)
        self.rotate_item_spin.setHidden(True)

    def create_toolbar2(self):
        self.action_group = QActionGroup(self)

        #----toolbar buttons----#

        # Select Button
        self.select_btn = QAction(QIcon('ui/Tool Icons/selection_icon.png'), 'Select Tool (Spacebar)', self)
        self.select_btn.setToolTip('''Select Tool (Spacebar)''')
        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.triggered.connect(self.use_select)

        # Pan Button
        self.pan_btn = QAction(QIcon('ui/Tool Icons/pan_icon.png'), 'Pan Tool (P)', self)
        self.pan_btn.setToolTip('''Pan Tool (P)''')
        self.pan_btn.setCheckable(True)
        self.pan_btn.triggered.connect(self.use_pan)

        # Drawing/editing tools
        self.path_btn = QAction(QIcon('ui/Tool Icons/pen_tool_icon.png'), 'Path Draw Tool (L)', self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip('''Path Draw Tool (L)''')
        self.path_btn.triggered.connect(self.update)
        self.path_btn.triggered.connect(self.use_path)

        self.pen_btn = QAction(QIcon('ui/Tool Icons/pen_draw_icon.png'), 'Pen Draw Tool (Ctrl+L)', self)
        self.pen_btn.setCheckable(True)
        self.pen_btn.setToolTip('''Pen Draw Tool (Ctrl+L)''')
        self.pen_btn.triggered.connect(self.update)
        self.pen_btn.triggered.connect(self.use_pen_tool)

        self.sculpt_btn = QAction(QIcon('ui/Tool Icons/sculpt_icon.png'), 'Sculpt Tool (S)', self)
        self.sculpt_btn.setCheckable(True)
        self.sculpt_btn.setToolTip('''Sculpt Tool (S)''')
        self.sculpt_btn.triggered.connect(self.update)
        self.sculpt_btn.triggered.connect(self.use_sculpt_path)

        self.drawing_toolbutton = ToolButton()
        self.drawing_toolbutton.setDefaultAction(self.path_btn)
        self.drawing_toolbutton.addAction(self.path_btn)
        self.drawing_toolbutton.addAction(self.pen_btn)
        self.drawing_toolbutton.addAction(self.sculpt_btn)

        # Label draw button
        self.label_btn = QAction(QIcon('ui/Tool Icons/label_icon.png'), "Line and Label Tool (T)", self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip('''Line and Label Tool (T)''')
        self.label_btn.triggered.connect(self.update)
        self.label_btn.triggered.connect(self.use_label)

        # Add Text Button
        self.add_text_btn = QAction(QIcon('ui/Tool Icons/text_icon.png'), 'Text Tool (Ctrl+T)', self)
        self.add_text_btn.setToolTip('''Text Tool (Ctrl+T)''')
        self.add_text_btn.setCheckable(True)
        self.add_text_btn.triggered.connect(self.update)
        self.add_text_btn.triggered.connect(self.use_text)

        # Scale Button
        self.scale_btn = QAction(QIcon('ui/Tool Icons/scale_icon.png'), 'Scale Tool (Q)', self)
        self.scale_btn.setToolTip('''Scale Tool (Q)''')
        self.scale_btn.setCheckable(True)
        self.scale_btn.triggered.connect(self.use_scale_tool)

        # Hide Button
        self.hide_btn = QAction(QIcon('ui/Tool Icons/hide_icon.png'), 'Hide Element Tool (H)', self)
        self.hide_btn.setToolTip('''Hide Element Tool (H)''')
        self.hide_btn.triggered.connect(self.use_hide_item)

        # Unhide Button
        self.unhide_btn = QAction(QIcon('ui/Tool Icons/unhide_icon.png'), 'Unhide All Tool (Ctrl+H)', self)
        self.unhide_btn.setToolTip('''Unhide All Tool (Ctrl+H)''')
        self.unhide_btn.triggered.connect(self.use_unhide_all)

        # Add Canvas Button
        self.add_canvas_btn = QAction(QIcon('ui/Tool Icons/add_canvas_icon.png'), 'Add Canvas Tool (A)', self)
        self.add_canvas_btn.setToolTip('''Add Canvas Tool (A)''')
        self.add_canvas_btn.setCheckable(True)
        self.add_canvas_btn.triggered.connect(self.use_add_canvas)

        # Insert Image Button
        self.insert_btn = QAction(QIcon('ui/Tool Icons/insert_image_icon2.png'), 'Insert Element Tool (I)', self)
        self.insert_btn.setToolTip('''Insert Tool (I)''')
        self.insert_btn.triggered.connect(self.insert_image)

        # ----add actions----#

        # Add toolbar actions
        self.toolbar.addAction(self.select_btn)
        self.toolbar.addAction(self.pan_btn)
        self.toolbar.addWidget(self.drawing_toolbutton)
        self.toolbar.addAction(self.label_btn)
        self.toolbar.addAction(self.add_text_btn)
        self.toolbar.addAction(self.scale_btn)
        self.toolbar.addAction(self.hide_btn)
        self.toolbar.addAction(self.unhide_btn)
        self.toolbar.addAction(self.add_canvas_btn)
        self.toolbar.addAction(self.insert_btn)

        # Action Group
        self.action_group.addAction(self.select_btn)
        self.action_group.addAction(self.pan_btn)
        self.action_group.addAction(self.path_btn)
        self.action_group.addAction(self.pen_btn)
        self.action_group.addAction(self.sculpt_btn)
        self.action_group.addAction(self.label_btn)
        self.action_group.addAction(self.add_text_btn)
        self.action_group.addAction(self.scale_btn)
        self.action_group.addAction(self.hide_btn)
        self.action_group.addAction(self.unhide_btn)
        self.action_group.addAction(self.add_canvas_btn)

        # Add to actions dict
        self.actions['''Select'''] = self.select_btn
        self.actions['Pan'] = self.pan_btn
        self.actions['Path Draw'] = self.path_btn
        self.actions['Pen Draw'] = self.pen_btn
        self.actions['Line and Label'] = self.label_btn
        self.actions['Add Text'] = self.add_text_btn
        self.actions['Scale'] = self.scale_btn
        self.actions['Hide'] = self.hide_btn
        self.actions['Unhide'] = self.unhide_btn
        self.actions['Add Canvas'] = self.add_canvas_btn
        self.actions['Insert Image'] = self.insert_btn

    def create_toolbar3(self):
        #----item toolbar widgets----#
        align_left_btn = QAction(QIcon('ui/Tool Icons/align_left_icon.png'), '', self)
        align_left_btn.setToolTip('Align the selected elements to the left')
        align_left_btn.triggered.connect(self.use_align_left)

        align_right_btn = QAction(QIcon('ui/Tool Icons/align_right_icon.png'), '', self)
        align_right_btn.setToolTip('Align the selected elements to the right')
        align_right_btn.triggered.connect(self.use_align_right)

        align_center_btn = QAction(QIcon('ui/Tool Icons/align_center_icon.png'), '', self)
        align_center_btn.setToolTip('Align the selected elements to the center')
        align_center_btn.triggered.connect(self.use_align_center)

        align_middle_btn = QAction(QIcon('ui/Tool Icons/align_middle_icon.png'), '', self)
        align_middle_btn.setToolTip('Align the selected elements to the middle')
        align_middle_btn.triggered.connect(self.use_align_middle)

        align_top_btn = QAction(QIcon('ui/Tool Icons/align_top_icon.png'), '', self)
        align_top_btn.setToolTip('Align the selected elements to the top')
        align_top_btn.triggered.connect(self.use_align_top)

        align_bottom_btn = QAction(QIcon('ui/Tool Icons/align_bottom_icon.png'), '', self)
        align_bottom_btn.setToolTip('Align the selected elements to the center')
        align_bottom_btn.triggered.connect(self.use_align_bottom)

        rotate_ccw_action = QAction(QIcon('ui/Tool Icons/rotate_ccw_icon.png'), '', self)
        rotate_ccw_action.setToolTip('Rotate the selected elements 90° counter-clockwise')
        rotate_ccw_action.triggered.connect(lambda: self.use_rotate_direction('ccw'))

        rotate_cw_action = QAction(QIcon('ui/Tool Icons/rotate_cw_icon.png'), '', self)
        rotate_cw_action.setToolTip('Rotate the selected elements 90° clockwise')
        rotate_cw_action.triggered.connect(lambda: self.use_rotate_direction('cw'))

        raise_layer_action = QAction(QIcon('ui/Tool Icons/raise_layer_icon.png'), '', self)
        raise_layer_action.setToolTip('Raise the selected elements a layer up')
        raise_layer_action.triggered.connect(self.use_raise_layer)

        lower_layer_action = QAction(QIcon('ui/Tool Icons/lower_layer_icon.png'), '', self)
        lower_layer_action.setToolTip('Lower the selected elements a layer down')
        lower_layer_action.triggered.connect(self.use_lower_layer)

        self.view_zoom_spin = QSpinBox(self)
        self.view_zoom_spin.setToolTip('Zoom view')
        self.view_zoom_spin.setRange(1, 5000)
        self.view_zoom_spin.setFixedWidth(50)
        self.view_zoom_spin.setSuffix('%')
        self.view_zoom_spin.setValue(100)
        self.view_zoom_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.view_zoom_spin.valueChanged.connect(self.use_change_view)

        self.rotate_scene_spin = QSpinBox(self)
        self.rotate_scene_spin.setToolTip('Rotate view')
        self.rotate_scene_spin.setFixedWidth(50)
        self.rotate_scene_spin.setMinimum(-10000)
        self.rotate_scene_spin.setMaximum(10000)
        self.rotate_scene_spin.setSuffix('°')
        self.rotate_scene_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.rotate_scene_spin.valueChanged.connect(self.use_change_view)

        sculpt_label = QLabel('Sculpt Radius:')
        self.sculpt_radius_spin = QSpinBox(self)
        self.sculpt_radius_spin.setSuffix(' pt')
        self.sculpt_radius_spin.setFixedWidth(75)
        self.sculpt_radius_spin.setRange(10, 500)
        self.sculpt_radius_spin.setToolTip('Change the sculpt radius')
        self.sculpt_radius_spin.setValue(100)
        self.sculpt_radius_spin.valueChanged.connect(self.use_set_sculpt_radius)
        sculpt_hlayout = ToolbarHorizontalLayout()
        sculpt_hlayout.layout.addWidget(sculpt_label)
        sculpt_hlayout.layout.addWidget(self.sculpt_radius_spin)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add widgets
        self.item_toolbar.addAction(align_left_btn)
        self.item_toolbar.addAction(align_right_btn)
        self.item_toolbar.addAction(align_center_btn)
        self.item_toolbar.addAction(align_middle_btn)
        self.item_toolbar.addAction(align_top_btn)
        self.item_toolbar.addAction(align_bottom_btn)
        self.item_toolbar.addSeparator()
        self.item_toolbar.addAction(rotate_ccw_action)
        self.item_toolbar.addAction(rotate_cw_action)
        self.item_toolbar.addAction(raise_layer_action)
        self.item_toolbar.addAction(lower_layer_action)
        self.item_toolbar.addSeparator()
        self.item_toolbar.addWidget(sculpt_hlayout)
        self.item_toolbar.addWidget(spacer)
        self.item_toolbar.addWidget(self.rotate_scene_spin)
        self.item_toolbar.addWidget(self.view_zoom_spin)

        # Add to actions dict
        self.actions['Zoom View'] = self.view_zoom_spin
        self.actions['Rotate View'] = self.rotate_scene_spin
        self.actions['Align Left'] = align_left_btn
        self.actions['Align Right'] = align_right_btn
        self.actions['Align Middle'] = align_middle_btn
        self.actions['Align Center'] = align_center_btn
        self.actions['Align Top'] = align_top_btn
        self.actions['Align Bottom'] = align_bottom_btn
        self.actions['Rotate Counter Clockwise'] = rotate_ccw_action
        self.actions['Rotate Clockwise'] = rotate_cw_action
        self.actions['Raise Layer'] = raise_layer_action
        self.actions['Lower Layer'] = lower_layer_action

    def create_view(self):
        # QGraphicsView Logic
        self.canvas_view = CustomGraphicsView(self.canvas,
                                              self.path_btn,
                                              self.label_btn,
                                              self.pen_btn,
                                              self.add_text_btn,
                                              self.add_canvas_btn,
                                              self.select_btn,
                                              self.scale_btn,
                                              self.pan_btn,
                                              self.view_zoom_spin,
                                              self.quick_actions_tab.gsnap_check_btn,
                                              self.sculpt_btn)
        self.canvas_view.setViewport(CustomViewport())
        self.canvas_view.setScene(self.canvas)
        self.canvas.set_widget(self.scale_btn)
        self.action_group.triggered.connect(self.canvas_view.on_add_canvas_trigger)
        self.setCentralWidget(self.canvas_view)

        # Update default fonts, colors, etc.
        self.update('ui_update')
        self.update_item_pen()
        self.update_item_font()
        self.update_item_fill()

        # Context menu for view
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.triggered.connect(self.use_duplicate)
        vectorize_action = QAction('Vectorize', self)
        vectorize_action.triggered.connect(self.use_vectorize)
        raise_layer_action = QAction('Raise Layer', self)
        raise_layer_action.triggered.connect(self.use_raise_layer)
        lower_layer_action = QAction('Lower Layer', self)
        lower_layer_action.triggered.connect(self.use_lower_layer)
        bring_to_front_action = QAction('Bring to Front', self)
        bring_to_front_action.triggered.connect(self.use_bring_to_front)
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

        self.canvas_view.addAction(duplicate_action)
        self.canvas_view.addAction(sep3)
        self.canvas_view.addAction(raise_layer_action)
        self.canvas_view.addAction(lower_layer_action)
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
        self.paper = CanvasItem(QRectF(0, 0, 1000, 700), 'Canvas 1')
        self.canvas.addItem(self.paper)

        # Text on paper
        self.paper_text = CustomTextItem(default_text)
        self.paper_text.setPos(2, 2)
        self.paper_text.setDefaultTextColor(QColor('black'))
        self.paper_text.setFont(font)
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.paper_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.paper_text.setZValue(0)
        self.canvas.addItem(self.paper_text)

        self.path_btn.trigger()
        self.select_btn.trigger()

    def update(self, *args):
        super().update()

        for mode in args:
            if mode == 'ui_update':
                self.update_transform_ui()
                self.update_appearance_ui()
                self.repaint()

            elif mode == 'item_update':
                self.canvas.update()
                self.canvas_view.update()

                for item in self.canvas.items():
                    item.update()

                    if isinstance(item, LeaderLineItem):
                        item.updatePathEndPoint()

    def update_item_pen(self):
        # Update pen and brush
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        pen = QPen()
        pen.setColor(QColor(self.outline_color.get()))
        pen.setWidth(self.stroke_size_spin.value())
        pen.setJoinStyle(self.join_style_combo.itemData(self.join_style_combo.currentIndex()))
        pen.setStyle(data1)
        pen.setCapStyle(data2)

        self.canvas_view.update_pen(pen)

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                if isinstance(item, CustomPathItem):
                    try:
                        command = PenChangeCommand(item, item.pen(), pen)
                        self.canvas.addCommand(command)

                    except Exception:
                        pass

                elif isinstance(item, LeaderLineItem):
                    try:
                        command = PenChangeCommand(item, item.pen(), pen)
                        self.canvas.addCommand(command)

                    except Exception:
                        pass

    def update_item_fill(self):
        brush = QBrush(QColor(self.fill_color.get()))

        self.canvas_view.update_brush(brush)

        if self.canvas.selectedItems():
            for item in self.canvas.selectedItems():
                if isinstance(item, CustomPathItem):
                    try:
                        command = BrushChangeCommand(item, item.brush(), brush)
                        self.canvas.addCommand(command)

                    except Exception:
                        pass

                elif isinstance(item, LeaderLineItem):
                    try:
                        command = BrushChangeCommand(item, item.brush(), brush)
                        self.canvas.addCommand(command)

                    except Exception:
                        pass

    def update_item_font(self):
        # Update font
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
                if isinstance(item, CustomTextItem):
                    command = FontChangeCommand(item, item.font(), font, item.defaultTextColor(),
                                                QColor(self.font_color.get()))
                    self.canvas.addCommand(command)

                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

                elif isinstance(item, CustomPathItem):
                    if item.add_text == True:
                        item.update()
                        item.setTextAlongPathFont(font)
                        item.setTextAlongPathColor(QColor(self.font_color.get()))
                        item.update()

    def update_transform_ui(self):
        self.x_pos_spin.blockSignals(True)
        self.y_pos_spin.blockSignals(True)
        self.width_scale_spin.blockSignals(True)
        self.height_scale_spin.blockSignals(True)
        self.rotate_item_spin.blockSignals(True)
        self.opacity_spin.blockSignals(True)

        if len(self.canvas.selectedItems()) > 0:
            self.properties_tab.setFixedHeight(425)

            self.transform_separator.setHidden(False)
            self.transform_label.setHidden(False)
            self.x_pos_label.setHidden(False)
            self.x_pos_spin.setHidden(False)
            self.y_pos_label.setHidden(False)
            self.y_pos_spin.setHidden(False)
            self.width_transform_label.setHidden(False)
            self.height_transform_label.setHidden(False)
            self.width_scale_spin.setHidden(False)
            self.height_scale_spin.setHidden(False)
            self.flip_horizontal_btn.setHidden(False)
            self.flip_vertical_btn.setHidden(False)
            self.rotation_label.setHidden(False)
            self.rotate_item_spin.setHidden(False)

            for item in self.canvas.selectedItems():
                self.x_pos_spin.setValue(int(item.sceneBoundingRect().x()))
                self.y_pos_spin.setValue(int(item.sceneBoundingRect().y()))
                self.rotate_item_spin.setValue(int(item.rotation()))
                self.opacity_spin.setValue(int(item.opacity() * 100))

                if item.transform().m11() < 0:
                    self.width_scale_spin.setValue(-item.boundingRect().width())

                else:
                    self.width_scale_spin.setValue(item.boundingRect().width())

                if item.transform().m22() < 0:
                    self.height_scale_spin.setValue(-item.boundingRect().height())

                else:
                    self.height_scale_spin.setValue(item.boundingRect().height())

                self.selection_label.setText(item.toolTip())

                if len(self.canvas.selectedItems()) > 1:
                    self.selection_label.setText('Combined Selection')
                    self.x_pos_spin.setValue(int(self.canvas.selectedItemsSceneBoundingRect().x()))
                    self.y_pos_spin.setValue(int(self.canvas.selectedItemsSceneBoundingRect().y()))

        else:
            self.properties_tab.setFixedHeight(325)

            self.transform_separator.setHidden(True)
            self.transform_label.setHidden(True)
            self.x_pos_label.setHidden(True)
            self.x_pos_spin.setHidden(True)
            self.y_pos_label.setHidden(True)
            self.y_pos_spin.setHidden(True)
            self.width_transform_label.setHidden(True)
            self.height_transform_label.setHidden(True)
            self.width_scale_spin.setHidden(True)
            self.height_scale_spin.setHidden(True)
            self.flip_horizontal_btn.setHidden(True)
            self.flip_vertical_btn.setHidden(True)
            self.rotation_label.setHidden(True)
            self.rotate_item_spin.setHidden(True)

            self.selection_label.setText('No Selection')
            self.x_pos_spin.setValue(0)
            self.y_pos_spin.setValue(0)
            self.rotate_item_spin.setValue(0)
            self.opacity_spin.setValue(100)
            self.width_scale_spin.setValue(0.0)
            self.height_scale_spin.setValue(0.0)

        self.x_pos_spin.blockSignals(False)
        self.y_pos_spin.blockSignals(False)
        self.rotate_item_spin.blockSignals(False)
        self.opacity_spin.blockSignals(False)
        self.width_scale_spin.blockSignals(False)
        self.height_scale_spin.blockSignals(False)

    def update_appearance_ui(self):
        self.canvas_tab.canvas_x_entry.blockSignals(True)
        self.canvas_tab.canvas_y_entry.blockSignals(True)
        self.canvas_tab.canvas_name_entry.blockSignals(True)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(True)
        self.stroke_size_spin.blockSignals(True)
        self.stroke_style_combo.blockSignals(True)
        self.stroke_pencap_combo.blockSignals(True)
        self.join_style_combo.blockSignals(True)
        self.fill_color_btn.blockSignals(True)
        self.stroke_color_btn.blockSignals(True)
        self.font_choice_combo.blockSignals(True)
        self.font_color_btn.blockSignals(True)
        self.font_size_spin.blockSignals(True)
        self.font_letter_spacing_spin.blockSignals(True)
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)

        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                pen = item.pen()
                brush = item.brush()

                # Set Colors
                if pen.color().alpha() != 0:
                    self.stroke_color_btn.setButtonColor(pen.color().name())
                    self.outline_color.set(pen.color().name())

                else:
                    self.stroke_color_btn.setTransparent(True)
                    self.outline_color.set(Qt.transparent)

                if brush.color().alpha() != 0:
                    self.fill_color_btn.setButtonColor(brush.color().name())
                    self.fill_color.set(brush.color().name())

                else:
                    self.fill_color_btn.setTransparent(True)
                    self.fill_color.set(Qt.transparent)

                # Set Values
                self.stroke_size_spin.setValue(pen.width())

                for index, (style, value) in enumerate(self.stroke_style_options.items()):
                    if pen.style() == value:
                        self.stroke_style_combo.setCurrentIndex(index)

                for i, (s, v) in enumerate(self.stroke_pencap_options.items()):
                    if pen.capStyle() == v:
                        self.stroke_pencap_combo.setCurrentIndex(i)

                for index, (s, v) in enumerate(self.join_style_options.items()):
                    if pen.joinStyle() == v:
                        self.join_style_combo.setCurrentIndex(i)

                self.canvas_view.update_pen(item.pen())
                self.canvas_view.update_brush(item.brush())

            elif isinstance(item, CanvasItem):
                self.canvas_tab.canvas_x_entry.setValue(int(item.boundingRect().width()))
                self.canvas_tab.canvas_y_entry.setValue(int(item.boundingRect().height()))
                self.canvas_tab.canvas_name_entry.setText(item.name())

                # Update the canvas preset dropdown
                for index, (preset, size) in enumerate(self.canvas_tab.canvas_presets.items()):
                    if (item.boundingRect().width(), item.boundingRect().height()) == size:
                        self.canvas_tab.canvas_preset_dropdown.setCurrentIndex(index)
                        break  # Exit the loop once the matching preset is found
                else:
                    # If no matching preset is found, set to 'Custom'
                    custom_index = self.canvas_tab.canvas_preset_dropdown.findText('Custom')
                    self.canvas_tab.canvas_preset_dropdown.setCurrentIndex(custom_index)

            elif isinstance(item, LeaderLineItem):
                pen = item.pen()
                brush = item.brush()

                # Set Colors
                if pen.color().alpha() != 0:
                    self.stroke_color_btn.setButtonColor(pen.color().name())
                    self.outline_color.set(pen.color().name())

                else:
                    self.stroke_color_btn.setTransparent(True)
                    self.outline_color.set(Qt.transparent)

                if brush.color().alpha() != 0:
                    self.fill_color_btn.setButtonColor(brush.color().name())
                    self.fill_color.set(brush.color().name())

                else:
                    self.fill_color_btn.setTransparent(True)
                    self.fill_color.set(Qt.transparent)

                # Set Values
                self.stroke_size_spin.setValue(pen.width())

                for index, (style, value) in enumerate(self.stroke_style_options.items()):
                    if pen.style() == value:
                        self.stroke_style_combo.setCurrentIndex(index)

                for i, (s, v) in enumerate(self.stroke_pencap_options.items()):
                    if pen.capStyle() == v:
                        self.stroke_pencap_combo.setCurrentIndex(i)

                for index, (s, v) in enumerate(self.join_style_options.items()):
                    if pen.joinStyle() == v:
                        self.join_style_combo.setCurrentIndex(i)

                self.canvas_view.update_pen(item.pen())
                self.canvas_view.update_brush(item.brush())

            elif isinstance(item, CustomTextItem):
                font = item.font()
                color = item.defaultTextColor()

                if color.alpha() != 0:
                    self.font_color_btn.setButtonColor(color.name())
                    self.font_color.set(color.name())

                else:
                    self.font_color_btn.setTransparent(True)
                    self.font_color.set(Qt.transparent)

                self.font_choice_combo.setCurrentText(font.family())
                self.font_size_spin.setValue(font.pixelSize())
                self.font_letter_spacing_spin.setValue(int(font.letterSpacing()))
                self.bold_btn.setChecked(True if font.bold() else False)
                self.italic_btn.setChecked(True if font.italic() else False)
                self.underline_btn.setChecked(True if font.underline() else False)

                self.canvas_view.update_font(item.font(), item.defaultTextColor())

        self.canvas_tab.canvas_x_entry.blockSignals(False)
        self.canvas_tab.canvas_y_entry.blockSignals(False)
        self.canvas_tab.canvas_name_entry.blockSignals(False)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(False)
        self.stroke_size_spin.blockSignals(False)
        self.stroke_style_combo.blockSignals(False)
        self.stroke_pencap_combo.blockSignals(False)
        self.join_style_combo.blockSignals(False)
        self.fill_color_btn.blockSignals(False)
        self.stroke_color_btn.blockSignals(False)
        self.font_choice_combo.blockSignals(False)
        self.font_color_btn.blockSignals(False)
        self.font_size_spin.blockSignals(False)
        self.font_letter_spacing_spin.blockSignals(False)
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)

    def stroke_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Stroke Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.outline_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.stroke_color_btn.setTransparent(False)
                self.stroke_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')
            else:
                self.stroke_color_btn.setTransparent(True)

            self.outline_color.set(color.name() if color.alpha() != 0 else Qt.transparent)

    def fill_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Fill Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.fill_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.fill_color_btn.setTransparent(False)
                self.fill_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')
                self.fill_color_btn.repaint()

            else:
                self.fill_color_btn.setTransparent(True)

            self.fill_color.set(color.name() if color.alpha() != 0 else Qt.transparent)

    def font_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Font Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.font_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.font_color_btn.setTransparent(False)
                self.font_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')

            else:
                self.font_color_btn.setTransparent(True)

            self.font_color.set(color.name() if color.alpha() != 0 else Qt.transparent)

    def use_delete(self):
        selected_items = self.canvas.selectedItems()
        if selected_items:
            for item in selected_items:
                if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                    item.setSelected(False)
                    item.parentItem().setSelected(True)

            selected_items = self.canvas.selectedItems()

            command = RemoveItemCommand(self.canvas, selected_items)
            self.canvas.addCommand(command)

    def use_hard_delete(self):
        for item in self.canvas.selectedItems():
            self.canvas.removeItem(item)
            del item

    def use_select(self):
        self.select_btn.setChecked(True)
        self.canvas_view.on_add_canvas_trigger()
        self.canvas_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.canvas_view.setContextMenuPolicy(Qt.ActionsContextMenu)

    def use_select_all(self):
        self.select_btn.trigger()

        for item in self.canvas.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)

    def use_escape(self):
        self.canvas.clearSelection()

        for item in self.canvas.items():
            if isinstance(item, CustomTextItem) and item.hasFocus():
                item.clearFocus()

    def use_selection_mode(self, mode: str):
        if mode == 'canvas':
            self.use_add_canvas()

        else:
            self.select_btn.trigger()

        self.canvas.clearSelection()

        for item in self.canvas.items():
            if mode == 'path':
                if isinstance(item, CustomPathItem):
                    item.setSelected(True)

            elif mode == 'leaderline':
                if isinstance(item, LeaderLineItem):
                    item.setSelected(True)

            elif mode == 'pixmap':
                if isinstance(item, CustomPixmapItem):
                    item.setSelected(True)

            elif mode == 'svg':
                if isinstance(item, CustomSvgItem):
                    item.setSelected(True)

            elif mode == 'text':
                if isinstance(item, CustomTextItem):
                    item.setSelected(True)

            elif mode == 'svg':
                if isinstance(item, CustomSvgItem):
                    item.setSelected(True)

            elif mode == 'canvas':
                if isinstance(item, CanvasItem):
                    item.setSelected(True)

            elif mode == 'group':
                if isinstance(item, CustomGraphicsItemGroup):
                    item.setSelected(True)

    def use_pan(self):
        self.pan_btn.setChecked(True)

    def use_path(self):
        self.path_btn.setChecked(True)
        self.drawing_toolbutton.setDefaultAction(self.path_btn)
        self.canvas_view.disable_item_flags()

    def use_pen_tool(self):
        self.pen_btn.setChecked(True)
        self.drawing_toolbutton.setDefaultAction(self.pen_btn)
        self.canvas_view.disable_item_flags()

    def use_sculpt_path(self):
        self.sculpt_btn.setChecked(True)
        self.drawing_toolbutton.setDefaultAction(self.sculpt_btn)
        self.canvas_view.disable_item_flags()

    def use_set_sculpt_radius(self, value):
        self.canvas_view.sculptingTool.set_sculpt_radius(value)

    def use_label(self):
        self.label_btn.setChecked(True)
        self.canvas_view.disable_item_flags()

    def use_text(self):
        self.add_text_btn.setChecked(True)

    def use_change_view(self):
        value = self.view_zoom_spin.value() / 100

        self.canvas_view.resetTransform()
        self.canvas_view.scale(value, value)
        self.canvas_view.rotate(self.rotate_scene_spin.value())

    def use_raise_layer(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                pass

            else:
                c = LayerChangeCommand(item, item.zValue(), item.zValue() + 1)
                self.canvas.addCommand(c)

    def use_lower_layer(self):
        for item in self.canvas.selectedItems():
            if item.zValue() <= 0:
                QMessageBox.critical(self, 'Lower Layer', "You cannot lower this Element any lower.")

            else:
                if isinstance(item, CanvasItem):
                    pass

                else:
                    c = LayerChangeCommand(item, item.zValue(), item.zValue() - 1)
                    self.canvas.addCommand(c)

    def use_bring_to_front(self):
        selected_items = self.canvas.selectedItems()
        if selected_items:
            max_z = max([item.zValue() for item in self.canvas.items()])
            for item in selected_items:
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setZValue(max_z)

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
            if isinstance(item, CustomTextItem):
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

            elif isinstance(item, LeaderLineItem):
                item.duplicate()

    def use_set_item_pos(self):
        self.canvas.blockSignals(True)
        try:
            # Get target position from spin boxes
            target_x = self.x_pos_spin.value()
            target_y = self.y_pos_spin.value()

            # Get the bounding rect of selected items
            selected_items = self.canvas.selectedItems()
            if not selected_items:
                return

            bounding_rect = self.canvas.selectedItemsSceneBoundingRect()

            # Calculate the offset
            offset_x = target_x - bounding_rect.x()
            offset_y = target_y - bounding_rect.y()

            # Prepare lists for items, old positions, and new positions
            items = []
            old_positions = []
            new_positions = []

            # Move each selected item by the offset and collect positions
            for item in selected_items:
                if isinstance(item, LeaderLineItem):
                    item.childItems()[0].setSelected(False)
                    item.updatePathEndPoint()

                old_pos = item.pos()
                new_pos = QPointF(item.x() + offset_x, item.y() + offset_y)

                items.append(item)
                old_positions.append(old_pos)
                new_positions.append(new_pos)

            # Create and execute the command with all items
            command = MultiItemPositionChangeCommand(self, items, old_positions, new_positions)
            self.canvas.addCommand(command)

        finally:
            self.canvas.blockSignals(False)

    def use_scale_x(self, value):
        self.use_scale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def use_scale_y(self, value):
        self.use_scale(self.width_scale_spin.value(), self.height_scale_spin.value())

    def use_scale(self, x_value, y_value):
        try:
            items = self.canvas.selectedItems()
            for item in items:
                if isinstance(item, CanvasItem):
                    pass

                else:
                    if isinstance(item, LeaderLineItem):
                        item.childItems()[0].setSelected(False)
                        item.updatePathEndPoint()

                    elif isinstance(item, CustomTextItem):
                        if isinstance(item.parentItem(), LeaderLineItem):
                            item.parentItem().updatePathEndPoint()

                    # Calculate the center of the bounding box for the selected items
                    bounding_rect = item.boundingRect()
                    center_x = bounding_rect.center().x()
                    center_y = bounding_rect.center().y()

                    # Calculate the scaling factor for the group
                    current_width = bounding_rect.width()
                    current_height = bounding_rect.height()

                    scale_x = x_value / current_width if current_width != 0 else 1
                    scale_y = y_value / current_height if current_height != 0 else 1

                    # Create a transform centered on the bounding box's center
                    transform = QTransform()
                    transform.translate(center_x, center_y)
                    transform.scale(scale_x, scale_y)
                    transform.translate(-center_x, -center_y)

                    # Apply the transform to each item
                    command = TransformCommand(item, item.transform(), transform)
                    self.canvas.addCommand(command)

        except Exception as e:
            print(f"Error during scaling: {e}")

    def use_scale_tool(self):
        self.scale_btn.setChecked(True)
        self.canvas_view.disable_item_flags()

        self.use_exit_grid()

    def use_rotate(self, value):
        items = self.canvas.selectedItems()
        if not items:
            return

        # Rotate each item around the center
        for item in items:
            if isinstance(item, CanvasItem):
                pass

            else:
                if isinstance(item, LeaderLineItem):
                    item.childItems()[0].setSelected(False)
                    item.updatePathEndPoint()

                elif isinstance(item, CustomTextItem):
                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

                item.setTransformOriginPoint(item.boundingRect().center())

                # Set the rotation angle
                command = RotateCommand(self, item, item.rotation(), value)
                self.canvas.addCommand(command)

    def use_rotate_direction(self, dir: str):
        items = self.canvas.selectedItems()
        if not items:
            return

        # Rotate each item around the center
        for item in items:
            if isinstance(item, CanvasItem):
                pass

            else:
                if isinstance(item, LeaderLineItem):
                    item.childItems()[0].setSelected(False)
                    item.updatePathEndPoint()

                elif isinstance(item, CustomTextItem):
                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

                item.setTransformOriginPoint(item.boundingRect().center())

                if dir == 'ccw':
                    # Set the rotation angle
                    command = RotateCommand(self, item, item.rotation(), item.rotation() - 90)
                    self.canvas.addCommand(command)

                else:
                    # Set the rotation angle
                    command = RotateCommand(self, item, item.rotation(), item.rotation() + 90)
                    self.canvas.addCommand(command)

    def use_flip_horizontal(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)
                item.updatePathEndPoint()

        self.width_scale_spin.setValue(-self.width_scale_spin.value())

    def use_flip_vertical(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)
                item.updatePathEndPoint()

        self.height_scale_spin.setValue(-self.height_scale_spin.value())

    def use_mirror(self, direction):
        for item in self.canvas.selectedItems():
            if not isinstance(item, CanvasItem):
                self.use_escape()
                child = item.duplicate()
                child.setSelected(True)
                child.setPos(item.pos())

                if direction == 'h':
                    self.use_flip_horizontal()

                    if self.width_scale_spin.value() < 0:
                        child.setX(child.pos().x() - child.boundingRect().width())
                    else:
                        child.setX(child.pos().x() + child.boundingRect().width())

                elif direction == 'v':
                    self.use_flip_vertical()

                    if self.height_scale_spin.value() < 0:
                        child.setY(child.pos().y() - child.boundingRect().height())
                    else:
                        child.setY(child.pos().y() + child.boundingRect().height())

    def use_change_opacity(self, value):
        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.opacity_spin.maximum()

        # Apply the effect to selected items
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                command = OpacityCommand(item, item.opacity(), opacity)
                self.canvas.addCommand(command)

    def use_reset_item(self):
        for item in self.canvas.selectedItems():
            command = ResetItemCommand(item)
            self.canvas.addCommand(command)

        self.update_transform_ui()

    def use_add_canvas(self):
        self.toolbox.setCurrentWidget(self.canvas_tab)
        self.add_canvas_btn.setChecked(True)
        self.canvas_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.canvas.setBackgroundBrush(QBrush(QColor('#737373')))

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                item.setCanvasActive(True)
            elif isinstance(item, CanvasTextItem):
                if item.parentItem() and isinstance(item.parentItem(), CanvasItem):
                    if item.parentItem().rect().isEmpty():
                        self.canvas.removeItem(item)

    def use_exit_add_canvas(self):
        # Deactivate the add canvas tool
        self.select_btn.trigger()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                item.setCanvasActive(False)

        if self.quick_actions_tab.gsnap_check_btn.isChecked():
            self.quick_actions_tab.gsnap_check_btn.click()

    def use_exit_grid(self):
        if self.quick_actions_tab.gsnap_check_btn.isChecked():
            self.quick_actions_tab.gsnap_check_btn.click()

    def use_smooth_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                if item.smooth == True:
                    pass

                else:
                    try:
                        smoothed_path = item.smooth_path(item.path(), 0.1)

                        add_command = SmoothPathCommand(self.canvas, item, smoothed_path, item.path())
                        self.canvas.addCommand(add_command)

                    except Exception:
                        QMessageBox.critical(self, "Smooth Path", "Cannot smooth path anymore.")
                        self.canvas.undo()

    def use_close_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                command = CloseSubpathCommand(item, self.canvas)
                self.canvas.addCommand(command)

    def use_hide_item(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)

            elif isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    command = HideCommand(item.parentItem(), True, False)
                    self.canvas.addCommand(command)
                    return

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

    def use_align_left(self):
        if len(self.canvas.selectedItems()) > 1:
            FirstSelItem = self.canvas.selectedItems()[0]
            sel = self.canvas.selectedItems()
            for selItem in sel:
                dx, dy = 0, 0
                dx = (FirstSelItem.mapToScene(FirstSelItem.boundingRect().topLeft()).x()) - \
                     (selItem.mapToScene(selItem.boundingRect().topLeft()).x())
                command = AlignItemCommand(self, selItem, selItem.pos(), QPointF(dx, dy))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF(i.sceneBoundingRect().x(), item.y())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_right(self):
        if len(self.canvas.selectedItems()) > 1:
            if not self.canvas.selectedItems():
                return
            last_sel_item = self.canvas.selectedItems()[0]
            sel = self.canvas.selectedItems()
            for sel_item in sel:
                dx = (last_sel_item.mapToScene(last_sel_item.boundingRect().topRight()).x()) - \
                     (sel_item.mapToScene(sel_item.boundingRect().topRight()).x())
                command = AlignItemCommand(self, sel_item, sel_item.pos(), QPointF(dx, 0))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF((i.sceneBoundingRect().x() + i.sceneBoundingRect().width())
                                        - item.sceneBoundingRect().width(), item.y())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_center(self):
        if len(self.canvas.selectedItems()) > 1:
            if not self.canvas.selectedItems():
                return
            selected_items = self.canvas.selectedItems()
            # Find the average x-coordinate of the center of all selected items
            center_x = sum(item.sceneBoundingRect().center().x() for item in selected_items) / len(selected_items)
            for item in selected_items:
                # Calculate the displacement needed to move the item's center to the calculated center_x
                dx = center_x - item.sceneBoundingRect().center().x()
                command = AlignItemCommand(self, item, item.pos(), QPointF(dx, 0))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF(i.sceneBoundingRect().center().x() - item.boundingRect().center().x(), item.y())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_top(self):
        if len(self.canvas.selectedItems()) > 1:
            if not self.canvas.selectedItems():
                return
            selected_items = self.canvas.selectedItems()
            # Find the minimum y-coordinate of the top edge of all selected items
            top_y = min(item.sceneBoundingRect().top() for item in selected_items)
            for item in selected_items:
                # Calculate the displacement needed to move the item's top edge to the calculated top_y
                dy = top_y - item.sceneBoundingRect().top()
                command = AlignItemCommand(self, item, item.pos(), QPointF(0, dy))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF(item.x(), i.y())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_bottom(self):
        if len(self.canvas.selectedItems()) > 1:
            if not self.canvas.selectedItems():
                return
            selected_items = self.canvas.selectedItems()
            # Find the maximum y-coordinate of the bottom edge of all selected items
            bottom_y = max(item.sceneBoundingRect().bottom() for item in selected_items)
            for item in selected_items:
                # Calculate the displacement needed to move the item's bottom edge to the calculated bottom_y
                dy = bottom_y - item.sceneBoundingRect().bottom()
                command = AlignItemCommand(self, item, item.pos(), QPointF(0, dy))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF(item.x(), (i.y() + i.boundingRect().height()) - item.boundingRect().height())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_middle(self):
        if len(self.canvas.selectedItems()) > 1:
            if not self.canvas.selectedItems():
                return
            selected_items = self.canvas.selectedItems()
            # Find the average y-coordinate of the center of all selected items
            middle_y = sum(item.sceneBoundingRect().center().y() for item in selected_items) / len(selected_items)
            for item in selected_items:
                # Calculate the displacement needed to move the item's center to the calculated middle_y
                dy = middle_y - item.sceneBoundingRect().center().y()
                command = AlignItemCommand(self, item, item.pos(), QPointF(0, dy))
                self.canvas.addCommand(command)

        elif len(self.canvas.selectedItems()) == 1:
            for item in self.canvas.selectedItems():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    for i in self.canvas.items():
                        if isinstance(i, CanvasItem):
                            for colision in i.collidingItems():
                                if colision == item:
                                    new = QPointF(item.x(), i.sceneBoundingRect().center().y() - item.boundingRect().center().y())
                                    command = PositionChangeCommand(self, item, item.pos(), new)
                                    self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

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

    def insert_image(self):
        self.canvas.importManager.importFile()

    def choose_export(self):
        self.canvas.exportManager.normalExport()

    def choose_multiple_export(self):
        self.canvas.exportManager.multipleExport()

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)

    def show_version(self):
        self.w = VersionWin(self.canvas.mpversion)
        self.w.show()

    def show_about(self):
        try:
            self.w = AboutWin()
            self.w.show()
        except Exception as e:
            print(e)

    def show_find_action(self):
        self.w = FindActionWin(self.actions)
        self.w.show()

    def show_disclaimer(self):
        w = DisclaimerWin('internal data/user_data.mpdat')

        result = w.exec_()

        if result == QMessageBox.Yes:
            # Read existing data
            with open('internal data/user_data.mpdat', 'r') as f:
                existing_data = json.load(f)

            # Update the data
            existing_data[0]['disclaimer_read'] = True

            # Write the updated data back to the file
            with open('internal data/user_data.mpdat', 'w') as f:
                json.dump(existing_data, f)
        else:
            self.close()

    def new(self):
        self.canvas.manager.restore()

    def save(self):
        try:
            if self.canvas.manager.filename != 'Untitled':
                with open(self.canvas.manager.filename, 'wb') as f:
                    pickle.dump(self.canvas.manager.serialize_items(), f)
                    self.setWindowTitle(f'{os.path.basename(self.canvas.manager.filename)} - MPRUN')
                    self.canvas.modified = False
                    return True

            else:
                self.saveas()

        except Exception as e:
            QMessageBox.critical(self, 'Open File Error', f"Error saving scene: {e}", QMessageBox.Ok)

    def saveas(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save As', '', 'MPRUN files (*.mp)')

        if filename:
            try:
                with open(filename, 'wb') as f:
                    pickle.dump(self.canvas.manager.serialize_items(), f)

                    self.canvas.manager.filename = filename
                    self.canvas.modified = False
                    self.setWindowTitle(f'{os.path.basename(self.canvas.manager.filename)} - MPRUN')

                    # Read existing data
                    with open('internal data/user_data.mpdat', 'r') as f:
                        existing_data = json.load(f)

                    # Check if 'recent_files' exists and is a list, then append the new file
                    if 'recent_files' in existing_data[0]:
                        if isinstance(existing_data[0]['recent_files'], list):
                            existing_data[0]['recent_files'].append(filename)
                        else:
                            existing_data[0]['recent_files'] = [existing_data[0]['recent_files'], filename]
                    else:
                        existing_data[0]['recent_files'] = [filename]

                    # Write the updated data back to the file
                    with open('internal data/user_data.mpdat', 'w') as f:
                        json.dump(existing_data, f)

                    self.update_user_data()

                    return True

            except Exception as e:
                print(e)

        else:
            return False

    def open(self):
        self.canvas.manager.load(self)

    def open_recent(self, filename: str):
        self.canvas.manager.load_from_file(filename, self)

    def set_user_data(self, data):
        for user_data in data:
            if not user_data['disclaimer_read']:
                self.show_disclaimer()

            for recent_file in user_data['recent_files']:
                if os.path.exists(recent_file):
                    action = QAction(os.path.basename(recent_file), self)
                    action.setToolTip(os.path.abspath(recent_file))
                    action_tooltip = action.toolTip()  # Capture the current tooltip
                    action.triggered.connect(lambda checked, path=action_tooltip: self.open_recent(path))

                    self.open_recent_menu.addAction(action)

    def update_user_data(self):
        with open('internal data/user_data.mpdat', 'r') as f:
            data = json.load(f)

            for user_data in data:
                if not user_data['disclaimer_read']:
                    self.show_disclaimer()

                for recent_file in user_data['recent_files']:
                    if os.path.exists(recent_file):
                        if os.path.abspath(recent_file) not in (action.toolTip() for action in self.open_recent_menu.actions()):
                            action = QAction(os.path.basename(recent_file), self)
                            action.setToolTip(os.path.abspath(recent_file))
                            action_tooltip = action.toolTip()
                            action.triggered.connect(lambda checked, path=action_tooltip: self.open_recent(path))

                            self.open_recent_menu.addAction(action)


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    splash = QSplashScreen(QIcon('ui/Main Logos/MPRUN_splash_v3.png').pixmap(QSize(600, 600)), Qt.WindowStaysOnTopHint)
    splash.show()

    app.processEvents()

    if sys.platform == 'darwin':
        app.setStyleSheet(windows_style)

    else:
        app.setStyleSheet(windows_style)

    window = MPRUN()
    splash.finish(window)

    with open('internal data/user_data.mpdat', 'r') as f:
        data = json.load(f)
        window.set_user_data(data)

    sys.exit(app.exec_())
