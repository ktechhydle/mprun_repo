"""
This is MPRUN's main file including attributes such as:

-Widget and UI creation
-Function declaration
-Event handling
-User data handling

If you are using our integrated Python Scripting Interface,
this file is the one you might want to read over to learn MPRUN's
internal functions.
"""

from mp_software_stylesheets.styles import macCSS, windowsCSS
from src.framework.graphics_framework import CustomGraphicsView, CustomGraphicsScene, CustomViewport
from src.framework.data_repairer import FileDataRepairer
from src.gui.app_screens import AboutWin, VersionWin, FindActionWin, DisclaimerWin, SettingsWin, ScriptingWin
from src.gui.custom_widgets import *
from src.gui.icloud_integrator import iCloudIntegraterWin
from src.gui.panels import PropertiesPanel, CharactersPanel, LibrariesPanel, ImageTracingPanel, ScenePanel, \
    CanvasEditorPanel
from src.framework.three_dimensional_viewer.three_dimensional_viewer import SceneTo3DView
from src.scripts.app_internal import *
from src.scripts.raw_functions import nameismain, ItemStack
from src.scripts.get_version import get_latest_version

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

DEFAULT_PANEL_WIDTH = 300


class MPRUN(QMainWindow):
    def __init__(self):
        super(MPRUN, self).__init__()
        # Creating the main window
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setAcceptDrops(True)

        # Settings
        self.cur_view = ''

        # Colors
        for data in self.read_settings():
            self.outline_color = ItemStack()
            self.outline_color.set(data['default_stroke'])
            self.fill_color = ItemStack()
            self.fill_color.set(data['default_fill'])
            self.font_color = ItemStack()
            self.font_color.set(data['default_font'])

        # Undo, redo
        self.undo_stack = QUndoStack()

        # Actions
        self.actions = {}

        # Create UI
        self.create_ui()
        self.show()

    def closeEvent(self, event):
        if self.canvas is not None:
            self.canvas.clearSelection()

        if self.canvas.modified:
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox(self)
            confirmation_dialog.setWindowTitle('Close Document')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText('The document has been modified. Do you want to save your changes?')
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

        data = self.read_settings()

        for _data in data:
            _data['geometry'] = ['maximized'] if self.isMaximized() or self.isFullScreen() else [self.geometry().x(),
                                                                                                 self.geometry().y(),
                                                                                                 self.geometry().width(),
                                                                                                 self.geometry().height()
                                                                                                 ]
            _data['saved_view'] = self.current_view()
            _data['toolbar_pos'] = self.current_toolbar_pos()
            _data['toolbox_pos'] = self.current_toolbox_pos()
            _data['toolbox_collapsed'] = self.tab_view_dock.isCollapsed()
            _data['control_toolbar_hidden'] = self.item_toolbar.isHidden()
            _data['toolbar_hidden'] = self.toolbar.isHidden()
            _data['last_used_tool'] = self.action_group.checkedAction().text()
            _data['grid_size'] = self.canvas.gridSize
            _data['toolbox_index'] = self.toolbox.currentIndex()

        self.write_settings(data)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        print(f'Window Resize at {event}')
        self.canvas_view.updateTip()

    def moveEvent(self, event):
        super().moveEvent(event)
        print(f'Window Move at {event}')
        self.canvas_view.updateTip()

    def create_ui(self):
        self.create_initial_canvas()
        self.create_menu()
        self.init_toolbars()
        self.create_panels()
        self.create_toolbar1()
        self.create_toolbar2()
        self.create_view()
        self.create_default_objects()
        self.create_actions_dict()
        self.update()

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
        self.menu_bar = CustomMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('&File')
        self.tool_menu = self.menu_bar.addMenu('&Tools')
        self.edit_menu = self.menu_bar.addMenu('&Edit')
        self.object_menu = self.menu_bar.addMenu('&Object')
        self.selection_menu = self.menu_bar.addMenu('&Selection')
        self.view_menu = self.menu_bar.addMenu('&View')
        self.help_menu = self.menu_bar.addMenu('&Help')

        self.create_file_menu()
        self.create_tools_menu()
        self.create_edit_menu()
        self.create_object_menu()
        self.create_selection_menu()
        self.create_view_menu()
        self.create_help_menu()

    def create_file_menu(self):
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence('Ctrl+N'))
        new_action.triggered.connect(self.canvas.manager.restore)

        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence('Ctrl+O'))
        open_action.triggered.connect(lambda: self.canvas.manager.load(self))

        self.open_recent_menu = CustomMenu('Open Recent')

        open_template_action = QAction('Open Template', self)
        open_template_action.triggered.connect(self.canvas.template_manager.load_template)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.canvas.manager.save)

        saveas_action = QAction('Save &As...', self)
        saveas_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        saveas_action.triggered.connect(self.canvas.manager.saveas)

        save_copy_action = QAction('Save &Copy...', self)
        save_copy_action.triggered.connect(self.canvas.manager.save_copy)

        saveas_template_action = QAction('Save As &Template...', self)
        saveas_template_action.triggered.connect(self.canvas.template_manager.save_template)

        save_to_icloud_action = QAction('Save To &iCloud...', self)
        save_to_icloud_action.triggered.connect(self.send_to_icloud)

        export_action = QAction('Export Canvas', self)
        export_action.setShortcut(QKeySequence('Ctrl+E'))
        export_action.triggered.connect(self.canvas.exportManager.normalExport)

        export_multiple_action = QAction('Export All', self)
        export_multiple_action.setShortcut(QKeySequence('Ctrl+Shift+E'))
        export_multiple_action.triggered.connect(self.canvas.exportManager.multipleExport)

        repair_file_action = QAction('Repair File', self)
        repair_file_action.triggered.connect(self.use_repair_file)

        close_action = QAction('Close', self)
        close_action.triggered.connect(self.close)

        self.file_menu.addAction(new_action)
        self.file_menu.addAction(open_action)
        self.file_menu.addMenu(self.open_recent_menu)
        self.file_menu.addAction(open_template_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)
        self.file_menu.addAction(save_copy_action)
        self.file_menu.addAction(saveas_template_action)
        self.file_menu.addAction(save_to_icloud_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_action)
        self.file_menu.addAction(export_multiple_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(repair_file_action)
        self.file_menu.addAction(close_action)

    def create_tools_menu(self):
        drawing_menu = self.tool_menu.addMenu('Drawing', parent=self)
        path_menu = self.tool_menu.addMenu('Path', parent=self)
        characters_menu = self.tool_menu.addMenu('Characters', parent=self)
        image_menu = self.tool_menu.addMenu('Image', parent=self)
        scene_menu = self.tool_menu.addMenu('Scene', parent=self)

        select_action = QAction('Select', self)
        select_action.setShortcut(QKeySequence(Qt.Key_Space))
        select_action.triggered.connect(self.use_select)

        pan_action = QAction('Pan', self)
        pan_action.setShortcut(QKeySequence('P'))
        pan_action.triggered.connect(self.use_pan)

        view_in_3d_action = QAction('View In 3D', self)
        view_in_3d_action.setShortcut(Qt.Key_F5)
        view_in_3d_action.triggered.connect(self.show_3d_viewer)

        add_canvas_action = QAction('Add Canvas', self)
        add_canvas_action.setShortcut(QKeySequence('A'))
        add_canvas_action.triggered.connect(self.use_add_canvas)

        arrange_canvases_action = QAction('Arrange Canvases', self)
        arrange_canvases_action.setShortcut(Qt.Key_F3)
        arrange_canvases_action.triggered.connect(self.canvas.arrange)

        rename_canvases_action = QAction('Rename Canvases', self)
        rename_canvases_action.triggered.connect(self.canvas.rename)

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

        insert_image_action = QAction('Insert Image', self)
        insert_image_action.setShortcut(QKeySequence('I'))
        insert_image_action.triggered.connect(self.insert_image)

        image_trace_action = QAction('Trace Image', self)
        image_trace_action.triggered.connect(self.use_vectorize)

        smooth_action = QAction('Smooth Path', self)
        smooth_action.setShortcut(QKeySequence('Shift+S'))
        smooth_action.triggered.connect(self.use_smooth_path)

        close_subpath_action = QAction('Close Path', self)
        close_subpath_action.triggered.connect(self.use_close_path)

        sculpt_path_action = QAction('Sculpt Path', self)
        sculpt_path_action.setShortcut(QKeySequence('S'))
        sculpt_path_action.triggered.connect(self.use_sculpt_path)

        add_shape_menu = drawing_menu.addMenu('Add Shape', parent=self)
        add_shape_rect = QAction('Add Rectangle', self)
        add_shape_rect.triggered.connect(lambda: self.use_insert_shape('rect'))
        add_shape_circle = QAction('Add Circle', self)
        add_shape_circle.triggered.connect(lambda: self.use_insert_shape('circle'))
        add_shape_tri = QAction('Add Triangle', self)
        add_shape_tri.triggered.connect(lambda: self.use_insert_shape('triangle'))

        add_shape_menu.addAction(add_shape_rect)
        add_shape_menu.addAction(add_shape_circle)
        add_shape_menu.addAction(add_shape_tri)

        drawing_menu.addAction(path_action)
        drawing_menu.addAction(pen_action)
        drawing_menu.addAction(linelabel_action)
        drawing_menu.addMenu(add_shape_menu)

        path_menu.addAction(smooth_action)
        path_menu.addAction(close_subpath_action)
        path_menu.addAction(sculpt_path_action)

        characters_menu.addAction(text_action)

        image_menu.addAction(insert_image_action)
        image_menu.addAction(image_trace_action)

        scene_menu.addAction(select_action)
        scene_menu.addAction(pan_action)
        scene_menu.addSeparator()
        scene_menu.addAction(view_in_3d_action)
        scene_menu.addSeparator()
        scene_menu.addAction(add_canvas_action)
        scene_menu.addAction(arrange_canvases_action)
        scene_menu.addAction(rename_canvases_action)

    def create_edit_menu(self):
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.canvas.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Shift+Z'))
        redo_action.triggered.connect(self.canvas.redo)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence('Ctrl+C'))
        copy_action.triggered.connect(self.canvas.copy)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence('Ctrl+V'))
        paste_action.triggered.connect(self.canvas.paste)

        delete_action = QAction('Delete', self)
        delete_action.setShortcut(QKeySequence('Backspace'))
        delete_action.triggered.connect(self.use_delete)

        hard_delete_action = QAction('Hard Delete', self)
        hard_delete_action.setShortcut(QKeySequence('Ctrl+Shift+Backspace'))
        hard_delete_action.triggered.connect(self.use_hard_delete)

        self.edit_menu.addAction(undo_action)
        self.edit_menu.addAction(redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(copy_action)
        self.edit_menu.addAction(paste_action)
        self.edit_menu.addAction(delete_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(hard_delete_action)

    def create_object_menu(self):
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.setShortcut(QKeySequence('D'))
        duplicate_action.triggered.connect(self.canvas.duplicate)

        scale_action = QAction('Scale', self)
        scale_action.setShortcut(QKeySequence('Q'))
        scale_action.triggered.connect(self.use_scale_tool)

        rotate_action = QAction('Rotate', self)
        rotate_action.setShortcut(QKeySequence('R'))
        rotate_action.triggered.connect(self.use_rotate_tool)

        flip_horizontal_action = QAction('Flip Horizontal', self)
        flip_horizontal_action.setShortcut(QKeySequence(''))
        flip_horizontal_action.triggered.connect(self.use_flip_horizontal)

        flip_vertical_action = QAction('Flip Vertical', self)
        flip_vertical_action.setShortcut(QKeySequence(''))
        flip_vertical_action.triggered.connect(self.use_flip_vertical)

        mirror_horizontal_action = QAction('Mirror Horizontal', self)
        mirror_horizontal_action.triggered.connect(lambda: self.use_mirror('h'))

        mirror_vertical_action = QAction('Mirror Vertical', self)
        mirror_vertical_action.triggered.connect(lambda: self.use_mirror('v'))

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

        self.object_menu.addAction(raise_layer_action)
        self.object_menu.addAction(lower_layer_action)
        self.object_menu.addAction(bring_to_front_action)
        self.object_menu.addSeparator()
        self.object_menu.addAction(duplicate_action)
        self.object_menu.addAction(scale_action)
        self.object_menu.addAction(rotate_action)
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

    def create_selection_menu(self):
        select_all_action = QAction('Select All', self)
        select_all_action.setShortcut(QKeySequence('Ctrl+A'))
        select_all_action.triggered.connect(self.use_select_all)

        clear_selection_action = QAction('Clear Selection', self)
        clear_selection_action.setShortcut(QKeySequence('Escape'))
        clear_selection_action.triggered.connect(self.use_escape)

        select_paths_action = QAction('Select Paths', self)
        select_paths_action.triggered.connect(lambda: self.canvas.selectItemsInMode('path'))

        select_text_action = QAction('Select Text', self)
        select_text_action.triggered.connect(lambda: self.canvas.selectItemsInMode('text'))

        select_leaderline_action = QAction('Select Leader Lines', self)
        select_leaderline_action.triggered.connect(lambda: self.canvas.selectItemsInMode('leaderline'))

        select_pixmaps_action = QAction('Select Pixmaps', self)
        select_pixmaps_action.triggered.connect(lambda: self.canvas.selectItemsInMode('pixmap'))

        select_svgs_action = QAction('Select SVGs', self)
        select_svgs_action.triggered.connect(lambda: self.canvas.selectItemsInMode('svg'))

        select_canvases_action = QAction('Select Canvases', self)
        select_canvases_action.triggered.connect(lambda: self.canvas.selectItemsInMode('canvas'))

        self.selection_menu.addAction(select_all_action)
        self.selection_menu.addAction(clear_selection_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_paths_action)
        self.selection_menu.addAction(select_text_action)
        self.selection_menu.addAction(select_leaderline_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_pixmaps_action)
        self.selection_menu.addAction(select_svgs_action)
        self.selection_menu.addSeparator()
        self.selection_menu.addAction(select_canvases_action)

    def create_view_menu(self):
        fullscreen_view_action = QAction('Full Screen', self)
        fullscreen_view_action.setShortcut(Qt.Key_F11)
        fullscreen_view_action.triggered.connect(self.show_fullscreen)

        control_toolbar_view_action = QAction('Control Toolbar', self)
        control_toolbar_view_action.setCheckable(True)
        control_toolbar_view_action.setChecked(True)
        control_toolbar_view_action.setShortcut(Qt.Key_F12)
        control_toolbar_view_action.triggered.connect(lambda: self.toggle_control_toolbar(control_toolbar_view_action))

        view_options_menu = CustomMenu('Views', self)

        read_only_view_action = QAction('Read Only', self)
        read_only_view_action.triggered.connect(lambda: self.view_as('read_only'))

        tools_only_view_action = QAction('Tools Only', self)
        tools_only_view_action.triggered.connect(lambda: self.view_as('tools_only'))

        simple_view_action = QAction('Dyslexia Friendly', self)
        simple_view_action.triggered.connect(lambda: self.view_as('simple'))

        swapped_view_action = QAction('Swapped', self)
        swapped_view_action.triggered.connect(lambda: self.view_as('swapped'))

        default_view_action = QAction('Default', self)
        default_view_action.triggered.connect(lambda: self.view_as('normal'))

        view_options_menu.addAction(read_only_view_action)
        view_options_menu.addAction(tools_only_view_action)
        view_options_menu.addAction(simple_view_action)
        view_options_menu.addAction(swapped_view_action)
        view_options_menu.addAction(default_view_action)

        self.view_menu.addAction(control_toolbar_view_action)
        self.view_menu.addAction(fullscreen_view_action)
        self.view_menu.addMenu(view_options_menu)

    def create_help_menu(self):
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)

        show_version_action = QAction('Version', self)
        show_version_action.triggered.connect(self.show_version)

        find_action_action = QAction('Find Action', self)
        find_action_action.triggered.connect(self.show_find_action)

        browse_tutorials_action = QAction('Browse Tutorials', self)
        browse_tutorials_action.setShortcut(Qt.Key_F1)
        browse_tutorials_action.triggered.connect(
            lambda: webbrowser.open('https://sites.google.com/view/mprun-studio/home')
        )

        check_update_action = QAction('Check for Updates', self)
        check_update_action.triggered.connect(self.check_for_updates)

        view_settings_action = QAction('Settings', self)
        view_settings_action.setShortcut(Qt.Key_F2)
        view_settings_action.triggered.connect(self.show_settings)

        reload_ui_action = QAction('Restart User Interface', self)
        reload_ui_action.setShortcut(Qt.Key_F4)
        reload_ui_action.triggered.connect(self.open_settings_data)

        show_tip_of_the_day_action = QAction('Show Tip Of The Day', self)
        show_tip_of_the_day_action.setShortcut(QKeySequence('Shift+T'))
        show_tip_of_the_day_action.triggered.connect(self.show_tip_of_the_day)

        python_scripting_action = QAction('Python Scripting', self)
        python_scripting_action.triggered.connect(self.show_scripts)

        self.help_menu.addAction(about_action)
        self.help_menu.addAction(show_version_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(find_action_action)
        self.help_menu.addAction(browse_tutorials_action)
        self.help_menu.addAction(check_update_action)
        self.help_menu.addAction(view_settings_action)
        self.help_menu.addAction(reload_ui_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(show_tip_of_the_day_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(python_scripting_action)

    def init_toolbars(self):
        # Toolbar
        self.toolbar = QToolBar('Toolset')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setFixedWidth(60)
        self.toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Item toolbar
        self.item_toolbar = QToolBar('Control')
        self.item_toolbar.setIconSize(QSize(32, 32))
        self.item_toolbar.setMovable(False)
        self.item_toolbar.setAllowedAreas(Qt.TopToolBarArea)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.item_toolbar)
        self.item_toolbar.visibilityChanged.connect(self.control_toolbar_visibility_changed)

    def create_panels(self):
        # ----action toolbar widgets----#

        # Dock widget
        self.toolbox = CustomToolbox(self)
        self.toolbox.setFixedWidth(DEFAULT_PANEL_WIDTH)
        self.toolbox.setMinimumHeight(680)

        self.tab_view_dock = CustomDockWidget(self.toolbox, self)
        self.tab_view_dock.setWindowTitle('Actions')
        self.tab_view_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        # Properties Tab
        self.properties_tab = PropertiesPanel(self.canvas, self)
        self.properties_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Characters Tab
        self.characters_tab = CharactersPanel(self.canvas, self)
        self.characters_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.characters_tab.setFixedHeight(185)
        self.characters_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Vectorize Tab
        self.image_trace_tab = ImageTracingPanel(self.canvas, self)
        self.image_trace_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.image_trace_tab.setFixedHeight(375)
        self.image_trace_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Libraries Tab
        self.libraries_tab = LibrariesPanel(self.canvas)
        self.libraries_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.libraries_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Canvas Tab
        self.canvas_tab = CanvasEditorPanel(self.canvas)
        self.canvas_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Quick Actions Tab
        self.scene_tab = ScenePanel(self.canvas, self)
        self.scene_tab.setFixedWidth(DEFAULT_PANEL_WIDTH)

        # Add tabs
        self.toolbox.addItem(self.properties_tab, 'Properties')
        self.toolbox.addItem(self.libraries_tab, 'Libraries')
        self.toolbox.addItem(self.characters_tab, 'Characters')
        self.toolbox.addItem(self.image_trace_tab, 'Image Trace')
        self.toolbox.addItem(self.canvas_tab, 'Canvas')
        self.toolbox.addItem(self.scene_tab, 'Scene')
        self.toolbox.setItemIcon(0, QIcon('ui/UI Icons/Major/properties_panel.svg'))
        self.toolbox.setItemIcon(1, QIcon('ui/UI Icons/Major/libraries_panel.svg'))
        self.toolbox.setItemIcon(2, QIcon('ui/UI Icons/Major/characters_panel.svg'))
        self.toolbox.setItemIcon(3, QIcon('ui/UI Icons/Major/image_trace_panel.svg'))
        self.toolbox.setItemIcon(4, QIcon('ui/UI Icons/Major/canvas_panel.svg'))
        self.toolbox.setItemIcon(5, QIcon('ui/UI Icons/Major/scene_panel.svg'))

        # Add action toolbar actions
        self.tab_view_dock.setWidget(self.toolbox)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tab_view_dock)

        # Add to actions dict
        self.actions['Change Stroke Color'] = self.properties_tab.stroke_color_btn
        self.actions['Change Fill Color'] = self.properties_tab.fill_color_btn
        self.actions['Change Font Color'] = self.characters_tab.font_color_btn
        self.actions['Open Library'] = self.libraries_tab.open_library_button
        self.actions['Reload Library'] = self.libraries_tab.reload_library_button
        self.actions['Enable Grid'] = self.scene_tab.gsnap_check_btn

        self.set_properties_tab_enabled(False)

    def create_toolbar1(self):
        self.action_group = QActionGroup(self)

        # ----toolbar buttons----#

        # Select Button
        self.select_btn = QAction(QIcon('ui/Tool Icons/selection_icon.png'), 'Select Tool (Spacebar)', self)
        self.select_btn.setToolTip(
            '<b>Select (Spacebar)</b><br>'
            'Select items on the scene by clicking and dragging a selection rectangle.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )

        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.triggered.connect(self.use_select)

        # Pan Button
        self.pan_btn = QAction(QIcon('ui/Tool Icons/pan_icon.png'), 'Pan Tool (P)', self)
        self.pan_btn.setToolTip(
            '<b>Pan (P)</b><br>'
            'Pan around the scene by clicking and dragging.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.pan_btn.setCheckable(True)
        self.pan_btn.triggered.connect(self.use_pan)

        # Drawing/editing tools
        self.path_btn = QAction(QIcon('ui/Tool Icons/pen_tool_icon.png'), 'Path Draw Tool (L)', self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip(
            '<b>Path (L)</b><br>'
            'Draw path items on the scene by clicking and drawing.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.path_btn.triggered.connect(self.update)
        self.path_btn.triggered.connect(self.use_path)

        self.pen_btn = QAction(QIcon('ui/Tool Icons/pen_draw_icon.png'), 'Pen Draw Tool (Ctrl+L)', self)
        self.pen_btn.setCheckable(True)
        self.pen_btn.setToolTip(
            '<b>Pen (Ctrl+L)</b><br>'
            'Draw smooth path items on the scene by clicking and drawing.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.pen_btn.triggered.connect(self.update)
        self.pen_btn.triggered.connect(self.use_pen_tool)

        self.sculpt_btn = QAction(QIcon('ui/Tool Icons/sculpt_icon.png'), 'Sculpt Tool (S)', self)
        self.sculpt_btn.setCheckable(True)
        self.sculpt_btn.setToolTip(
            '<b>Sculpt (S)</b><br>'
            'Edit path items by clicking and dragging on them to "sculpt" them.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.sculpt_btn.triggered.connect(self.update)
        self.sculpt_btn.triggered.connect(self.use_sculpt_path)

        self.drawing_toolbutton = CustomToolButton()
        self.drawing_toolbutton.setDefaultAction(self.path_btn)
        self.drawing_toolbutton.addAction(self.path_btn)
        self.drawing_toolbutton.addAction(self.pen_btn)
        self.drawing_toolbutton.addAction(self.sculpt_btn)

        # Label draw button
        self.label_btn = QAction(QIcon('ui/Tool Icons/label_icon.png'), 'Line and Label Tool (T)', self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip(
            '<b>Line and Label (T)</b><br>'
            'Draw line and label items by clicking and dragging.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.label_btn.triggered.connect(self.update)
        self.label_btn.triggered.connect(self.use_label)

        # Add Text Button
        self.add_text_btn = QAction(QIcon('ui/Tool Icons/text_icon.png'), 'Text Tool (Ctrl+T)', self)
        self.add_text_btn.setToolTip(
            '<b>Text (Ctrl+T)</b><br>'
            'Add text items to the scene by clicking a point.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.add_text_btn.setCheckable(True)
        self.add_text_btn.triggered.connect(self.update)
        self.add_text_btn.triggered.connect(self.use_text)

        # Scale Button
        self.scale_btn = QAction(QIcon('ui/Tool Icons/scale_icon.png'), 'Scale Tool (Q)', self)
        self.scale_btn.setToolTip(
            '<b>Scale (Q)</b><br>'
            'Scale items in the scene by clicking and dragging on them.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.scale_btn.setCheckable(True)
        self.scale_btn.triggered.connect(self.use_scale_tool)

        # Rotate Button
        self.rotate_btn = QAction(QIcon('ui/Tool Icons/rotate_tool_icon.png'), 'Rotate Tool (R)', self)
        self.rotate_btn.setToolTip(
            '<b>Rotate (R)</b><br>'
            'Rotate items in the scene by clicking and dragging on them.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.rotate_btn.setCheckable(True)
        self.rotate_btn.triggered.connect(self.use_rotate_tool)

        # Hide Button
        self.hide_btn = QAction(QIcon('ui/Tool Icons/hide_icon.png'), 'Hide Element Tool (H)', self)
        self.hide_btn.setToolTip(
            '<b>Hide (H)</b><br>'
            'Hide the selected items in the scene.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.hide_btn.triggered.connect(self.use_hide_item)

        # Unhide Button
        self.unhide_btn = QAction(QIcon('ui/Tool Icons/unhide_icon.png'), 'Unhide All Tool (Ctrl+H)', self)
        self.unhide_btn.setToolTip(
            '<b>Unhide All (Ctrl+H)</b><br>'
            'Unhide all hidden items in the scene.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.unhide_btn.triggered.connect(self.use_unhide_all)

        # Add Canvas Button
        self.add_canvas_btn = QAction(QIcon('ui/Tool Icons/add_canvas_icon.png'), 'Add Canvas Tool (A)', self)
        self.add_canvas_btn.setToolTip(
            '<b>Add Canvas (A)</b><br>'
            'Add canvas items to the scene by clicking and dragging.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.add_canvas_btn.setCheckable(True)
        self.add_canvas_btn.triggered.connect(self.use_add_canvas)

        # Insert Image Button
        self.insert_btn = QAction(QIcon('ui/Tool Icons/insert_image_icon2.png'), 'Insert Element Tool (I)', self)
        self.insert_btn.setToolTip(
            '<b>Insert (I)</b><br>'
            'Insert a supported file type on to the scene.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        self.insert_btn.triggered.connect(self.insert_image)

        # ----add actions----#

        # Add toolbar actions
        self.toolbar.addAction(self.select_btn)
        self.toolbar.addAction(self.pan_btn)
        self.toolbar.addWidget(self.drawing_toolbutton)
        self.toolbar.addAction(self.label_btn)
        self.toolbar.addAction(self.add_text_btn)
        self.toolbar.addAction(self.scale_btn)
        self.toolbar.addAction(self.rotate_btn)
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
        self.action_group.addAction(self.rotate_btn)
        self.action_group.addAction(self.hide_btn)
        self.action_group.addAction(self.unhide_btn)
        self.action_group.addAction(self.add_canvas_btn)

    def create_toolbar2(self):
        # ----item toolbar widgets----#
        align_left_btn = QAction(QIcon('ui/Tool Icons/align_left_icon.png'), '', self)
        align_left_btn.setToolTip(
            '<b>Align Left</b><br>'
            'Align the selected items to the left.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_left_btn.triggered.connect(self.use_align_left)

        align_right_btn = QAction(QIcon('ui/Tool Icons/align_right_icon.png'), '', self)
        align_right_btn.setToolTip(
            '<b>Align Right</b><br>'
            'Align the selected items to the right.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_right_btn.triggered.connect(self.use_align_right)

        align_center_btn = QAction(QIcon('ui/Tool Icons/align_center_icon.png'), '', self)
        align_center_btn.setToolTip(
            '<b>Align Center</b><br>'
            'Align the selected items to the center.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_center_btn.triggered.connect(self.use_align_center)

        align_middle_btn = QAction(QIcon('ui/Tool Icons/align_middle_icon.png'), '', self)
        align_middle_btn.setToolTip(
            '<b>Align Middle</b><br>'
            'Align the selected items to the middle.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_middle_btn.triggered.connect(self.use_align_middle)

        align_top_btn = QAction(QIcon('ui/Tool Icons/align_top_icon.png'), '', self)
        align_top_btn.setToolTip(
            '<b>Align Top</b><br>'
            'Align the selected items to the top.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_top_btn.triggered.connect(self.use_align_top)

        align_bottom_btn = QAction(QIcon('ui/Tool Icons/align_bottom_icon.png'), '', self)
        align_bottom_btn.setToolTip(
            '<b>Align Bottom</b><br>'
            'Align the selected items to the bottom.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        align_bottom_btn.triggered.connect(self.use_align_bottom)

        rotate_ccw_action = QAction(QIcon('ui/Tool Icons/rotate_ccw_icon.png'), '', self)
        rotate_ccw_action.setToolTip(
            '<b>Rotate Left</b><br>'
            'Rotate the selected items 90° counter-clockwise.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        rotate_ccw_action.triggered.connect(lambda: self.use_rotate_direction('ccw'))

        rotate_cw_action = QAction(QIcon('ui/Tool Icons/rotate_cw_icon.png'), '', self)
        rotate_cw_action.setToolTip(
            '<b>Rotate Right</b><br>'
            'Rotate the selected items 90° clockwise.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        rotate_cw_action.triggered.connect(lambda: self.use_rotate_direction('cw'))

        raise_layer_action = QAction(QIcon('ui/Tool Icons/raise_layer_icon.png'), '', self)
        raise_layer_action.setToolTip(
            '<b>Raise</b><br>'
            'Raise the selected items a layer up.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        raise_layer_action.triggered.connect(self.use_raise_layer)

        lower_layer_action = QAction(QIcon('ui/Tool Icons/lower_layer_icon.png'), '', self)
        lower_layer_action.setToolTip(
            '<b>Lower</b><br>'
            'Lower the selected items a layer down.<br>'
            '<hr>'
            '<b>Press F1 for more help.</b><br>'
        )
        lower_layer_action.triggered.connect(self.use_lower_layer)

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

    def create_view(self):
        # QGraphicsView Logic
        self.canvas_view = CustomGraphicsView(self.canvas, [self.select_btn,
                                                            self.pan_btn,
                                                            self.path_btn,
                                                            self.pen_btn,
                                                            self.sculpt_btn,
                                                            self.label_btn,
                                                            self.add_text_btn,
                                                            self.scale_btn,
                                                            self.rotate_btn,
                                                            self.add_canvas_btn,
                                                            self.scene_tab.gsnap_check_btn])
        self.canvas_view.setScene(self.canvas)
        self.action_group.triggered.connect(self.canvas_view.on_add_canvas_trigger)
        self.setCentralWidget(self.canvas_view)

        # Update default fonts, colors, etc.
        self.update('ui_update')
        self.update_item_pen()
        self.update_item_font()
        self.update_item_fill()

        # Context menu for view
        copy_action = QAction('Copy', self)
        copy_action.triggered.connect(self.canvas.copy)
        paste_action = QAction('Paste', self)
        paste_action.triggered.connect(self.canvas.paste)
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.triggered.connect(self.canvas.duplicate)
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
        select_above_action = QAction('Select Items Above', self)
        select_above_action.triggered.connect(self.canvas.selectAbove)
        select_below_action = QAction('Select Items Below', self)
        select_below_action.triggered.connect(self.canvas.selectBelow)
        select_colliding_action = QAction('Select Colliding Items', self)
        select_colliding_action.triggered.connect(self.canvas.selectColliding)
        help_action = QAction('&Help', self)
        help_action.triggered.connect(
            lambda: webbrowser.open('https://sites.google.com/view/mprun-studio/home')
        )
        sep1 = QAction(self)
        sep1.setSeparator(True)
        sep2 = QAction(self)
        sep2.setSeparator(True)
        sep3 = QAction(self)
        sep3.setSeparator(True)
        sep4 = QAction(self)
        sep4.setSeparator(True)
        sep5 = QAction(self)
        sep5.setSeparator(True)

        self.canvas_view.addAction(copy_action)
        self.canvas_view.addAction(paste_action)
        self.canvas_view.addAction(duplicate_action)
        self.canvas_view.addAction(sep1)
        self.canvas_view.addAction(raise_layer_action)
        self.canvas_view.addAction(lower_layer_action)
        self.canvas_view.addAction(sep2)
        self.canvas_view.addAction(hide_action)
        self.canvas_view.addAction(unhide_action)
        self.canvas_view.addAction(sep3)
        self.canvas_view.addAction(select_all_action)
        self.canvas_view.addAction(select_above_action)
        self.canvas_view.addAction(select_below_action)
        self.canvas_view.addAction(select_colliding_action)
        self.canvas_view.addAction(sep4)
        self.canvas_view.addAction(help_action)

    def create_default_objects(self):
        font = QFont()
        font.setFamily(self.characters_tab.font_choice_combo.currentText())
        font.setPixelSize(self.characters_tab.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.characters_tab.font_letter_spacing_spin.value())
        font.setBold(True if self.characters_tab.bold_btn.isChecked() else False)
        font.setItalic(True if self.characters_tab.italic_btn.isChecked() else False)
        font.setUnderline(True if self.characters_tab.underline_btn.isChecked() else False)

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

    def create_actions_dict(self):
        menus_and_toolbars = [
            (self.file_menu.actions(), 'Open Recent'),
            (self.tool_menu.actions(), None),
            (self.edit_menu.actions(), None),
            (self.object_menu.actions(), None),
            (self.selection_menu.actions(), None),
            (self.view_menu.actions(), None),
            (self.help_menu.actions(), 'Find Action'),
            (self.toolbar.actions(), None),
            (self.item_toolbar.actions(), None)
        ]

        # Iterate through the actions of each menu/toolbar
        for actions, skip_text in menus_and_toolbars:
            if not isinstance(actions, QMenu):
                for action in actions:
                    action_text = action.text().replace('&', '')

                    # Skip specific actions if needed
                    if skip_text and action_text == skip_text:
                        continue

                    # Add the action to self.actions dictionary
                    self.actions[action_text] = action

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
        index1 = self.properties_tab.stroke_style_combo.currentIndex()
        data1 = self.properties_tab.stroke_style_combo.itemData(index1)
        index2 = self.properties_tab.stroke_pencap_combo.currentIndex()
        data2 = self.properties_tab.stroke_pencap_combo.itemData(index2)

        pen = QPen()
        pen.setColor(QColor(self.outline_color.get()))
        pen.setWidth(self.properties_tab.stroke_size_spin.value())
        pen.setJoinStyle(
            self.properties_tab.join_style_combo.itemData(self.properties_tab.join_style_combo.currentIndex()))
        pen.setStyle(data1)
        pen.setCapStyle(data2)

        self.canvas_view.update_pen(pen)

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

    def update_item_fill(self):
        brush = QBrush(QColor(self.fill_color.get()))

        self.canvas_view.update_brush(brush)

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

    def update_item_font(self):
        # Update font
        font = QFont()
        font.setFamily(self.characters_tab.font_choice_combo.currentText())
        font.setPixelSize(self.characters_tab.font_size_spin.value())
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.characters_tab.font_letter_spacing_spin.value())
        font.setBold(True if self.characters_tab.bold_btn.isChecked() else False)
        font.setItalic(True if self.characters_tab.italic_btn.isChecked() else False)
        font.setUnderline(True if self.characters_tab.underline_btn.isChecked() else False)

        new_color = QColor(self.font_color.get())

        self.canvas_view.update_font(font, new_color)

        selected_items = self.canvas.selectedItems()
        if selected_items:
            items = []
            old_fonts = []
            old_colors = []
            for item in selected_items:
                if isinstance(item, CustomTextItem):
                    items.append(item)
                    old_fonts.append(item.font())
                    old_colors.append(item.defaultTextColor())

            if items:
                try:
                    command = FontChangeCommand(items, old_fonts, font, old_colors, new_color)
                    self.canvas.addCommand(command)
                    for item in items:
                        if isinstance(item.parentItem(), LeaderLineItem):
                            item.parentItem().updatePathEndPoint()
                except Exception as e:
                    # Handle the exception (e.g., logging)
                    print(f'Exception: {e}')

    def update_transform_ui(self):
        # Block signals for all spinboxes at once
        spinboxes = [self.properties_tab.x_pos_spin, self.properties_tab.y_pos_spin,
                     self.properties_tab.width_scale_spin, self.properties_tab.height_scale_spin,
                     self.properties_tab.rotate_item_spin, self.properties_tab.opacity_spin]
        for spinbox in spinboxes:
            spinbox.blockSignals(True)

        selected_items = self.canvas.selectedItems()

        if selected_items:
            self.set_properties_tab_enabled(False)
            first_item = selected_items[0]

            # Update based on first item only
            self.properties_tab.x_pos_spin.setValue(int(first_item.sceneBoundingRect().x()))
            self.properties_tab.y_pos_spin.setValue(int(first_item.sceneBoundingRect().y()))
            self.properties_tab.rotate_item_spin.setValue(int(first_item.rotation()))
            self.properties_tab.opacity_spin.setValue(int(first_item.opacity() * 100))

            width = first_item.boundingRect().width() * (-1 if first_item.transform().m11() < 0 else 1)
            height = first_item.boundingRect().height() * (-1 if first_item.transform().m22() < 0 else 1)
            self.properties_tab.width_scale_spin.setValue(width)
            self.properties_tab.height_scale_spin.setValue(height)

            # Update label based on selection count
            if len(selected_items) > 1:
                self.properties_tab.selection_label.setText(f'Combined Selection ({len(selected_items)} Items)')
                bounding_rect = self.canvas.selectedItemsSceneBoundingRect()
                self.properties_tab.x_pos_spin.setValue(int(bounding_rect.x()))
                self.properties_tab.y_pos_spin.setValue(int(bounding_rect.y()))
            else:
                self.properties_tab.selection_label.setText(first_item.toolTip())

        else:
            self.set_properties_tab_enabled(True)

        # Unblock signals for all spinboxes at once
        for spinbox in spinboxes:
            spinbox.blockSignals(False)

    def update_appearance_ui(self):
        self.canvas_tab.canvas_x_entry.blockSignals(True)
        self.canvas_tab.canvas_y_entry.blockSignals(True)
        self.canvas_tab.canvas_name_entry.blockSignals(True)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(True)
        self.properties_tab.stroke_size_spin.blockSignals(True)
        self.properties_tab.stroke_style_combo.blockSignals(True)
        self.properties_tab.stroke_pencap_combo.blockSignals(True)
        self.properties_tab.join_style_combo.blockSignals(True)
        self.properties_tab.fill_color_btn.blockSignals(True)
        self.properties_tab.stroke_color_btn.blockSignals(True)
        self.characters_tab.font_choice_combo.blockSignals(True)
        self.characters_tab.font_color_btn.blockSignals(True)
        self.characters_tab.font_size_spin.blockSignals(True)
        self.characters_tab.font_letter_spacing_spin.blockSignals(True)
        self.characters_tab.bold_btn.blockSignals(True)
        self.characters_tab.italic_btn.blockSignals(True)
        self.characters_tab.underline_btn.blockSignals(True)

        try:
            for item in self.canvas.selectedItems():
                if isinstance(item, CustomPathItem):
                    pen = item.pen()
                    brush = item.brush()

                    # Set Colors
                    if pen.color().alpha() != 0:
                        self.properties_tab.stroke_color_btn.setButtonColor(pen.color().name())
                        self.outline_color.set(pen.color().name())

                    else:
                        self.properties_tab.stroke_color_btn.setTransparent(True)
                        self.outline_color.set(Qt.transparent)

                    if brush.color().alpha() != 0:
                        self.properties_tab.fill_color_btn.setButtonColor(brush.color().name())
                        self.fill_color.set(brush.color().name())

                    else:
                        self.properties_tab.fill_color_btn.setTransparent(True)
                        self.fill_color.set(Qt.transparent)

                    # Set Values
                    self.properties_tab.stroke_size_spin.setValue(pen.width())

                    for index, (style, value) in enumerate(self.properties_tab.stroke_style_options.items()):
                        if pen.style() == value:
                            self.properties_tab.stroke_style_combo.setCurrentIndex(index)

                    for i, (s, v) in enumerate(self.properties_tab.stroke_pencap_options.items()):
                        if pen.capStyle() == v:
                            self.properties_tab.stroke_pencap_combo.setCurrentIndex(i)

                    for index, (s, v) in enumerate(self.properties_tab.join_style_options.items()):
                        if pen.joinStyle() == v:
                            self.properties_tab.join_style_combo.setCurrentIndex(i)

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
                        self.properties_tab.stroke_color_btn.setButtonColor(pen.color().name())
                        self.outline_color.set(pen.color().name())

                    else:
                        self.properties_tab.stroke_color_btn.setTransparent(True)
                        self.outline_color.set(Qt.transparent)

                    if brush.color().alpha() != 0:
                        self.properties_tab.fill_color_btn.setButtonColor(brush.color().name())
                        self.fill_color.set(brush.color().name())

                    else:
                        self.properties_tab.fill_color_btn.setTransparent(True)
                        self.fill_color.set(Qt.transparent)

                    # Set Values
                    self.properties_tab.stroke_size_spin.setValue(pen.width())

                    for index, (style, value) in enumerate(self.properties_tab.stroke_style_options.items()):
                        if pen.style() == value:
                            self.properties_tab.stroke_style_combo.setCurrentIndex(index)

                    for i, (s, v) in enumerate(self.properties_tab.stroke_pencap_options.items()):
                        if pen.capStyle() == v:
                            self.properties_tab.stroke_pencap_combo.setCurrentIndex(i)

                    for index, (s, v) in enumerate(self.properties_tab.join_style_options.items()):
                        if pen.joinStyle() == v:
                            self.properties_tab.join_style_combo.setCurrentIndex(i)

                    self.canvas_view.update_pen(item.pen())
                    self.canvas_view.update_brush(item.brush())

                elif isinstance(item, CustomTextItem):
                    font = item.font()
                    color = item.defaultTextColor()

                    if color.alpha() != 0:
                        self.characters_tab.font_color_btn.setButtonColor(color.name())
                        self.font_color.set(color.name())

                    else:
                        self.characters_tab.font_color_btn.setTransparent(True)
                        self.font_color.set(Qt.transparent)

                    self.characters_tab.font_choice_combo.setCurrentText(font.family())
                    self.characters_tab.font_size_spin.setValue(font.pixelSize())
                    self.characters_tab.font_letter_spacing_spin.setValue(int(font.letterSpacing()))
                    self.characters_tab.bold_btn.setChecked(True if font.bold() else False)
                    self.characters_tab.italic_btn.setChecked(True if font.italic() else False)
                    self.characters_tab.underline_btn.setChecked(True if font.underline() else False)

                    self.canvas_view.update_font(item.font(), item.defaultTextColor())
        except Exception as e:
            print(e)

        self.canvas_tab.canvas_x_entry.blockSignals(False)
        self.canvas_tab.canvas_y_entry.blockSignals(False)
        self.canvas_tab.canvas_name_entry.blockSignals(False)
        self.canvas_tab.canvas_preset_dropdown.blockSignals(False)
        self.properties_tab.stroke_size_spin.blockSignals(False)
        self.properties_tab.stroke_style_combo.blockSignals(False)
        self.properties_tab.stroke_pencap_combo.blockSignals(False)
        self.properties_tab.join_style_combo.blockSignals(False)
        self.properties_tab.fill_color_btn.blockSignals(False)
        self.properties_tab.stroke_color_btn.blockSignals(False)
        self.characters_tab.font_choice_combo.blockSignals(False)
        self.characters_tab.font_color_btn.blockSignals(False)
        self.characters_tab.font_size_spin.blockSignals(False)
        self.characters_tab.font_letter_spacing_spin.blockSignals(False)
        self.characters_tab.bold_btn.blockSignals(False)
        self.characters_tab.italic_btn.blockSignals(False)
        self.characters_tab.underline_btn.blockSignals(False)

    def set_properties_tab_enabled(self, enabled: bool):
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

    def stroke_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Stroke Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.outline_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.properties_tab.stroke_color_btn.setButtonColor(color.name())

            else:
                self.properties_tab.stroke_color_btn.setTransparent(True)

            self.outline_color.set(color.name() if color.alpha() != 0 else Qt.transparent)

    def fill_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Fill Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.fill_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.properties_tab.fill_color_btn.setButtonColor(color.name())

            else:
                self.properties_tab.fill_color_btn.setTransparent(True)

            self.fill_color.set(color.name() if color.alpha() != 0 else Qt.transparent)

    def font_color_chooser(self):
        color_dialog = CustomColorPicker(self)
        color_dialog.setWindowTitle('Font Color')
        color_dialog.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        color_dialog.hex_spin.setText(QColor(self.font_color.get()).name()[1:])

        if color_dialog.exec_():
            color = color_dialog.currentColor()
            if color.alpha() != 0:
                self.characters_tab.font_color_btn.setButtonColor(color.name())

            else:
                self.characters_tab.font_color_btn.setTransparent(True)

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
            if item.flags() & item.ItemIsSelectable:
                item.setSelected(True)

    def use_escape(self):
        self.canvas.clearSelection()

        for item in self.canvas.items():
            if isinstance(item, CustomTextItem) and item.hasFocus():
                item.clearFocus()

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

    def use_scale_x(self, value):
        self.use_scale(self.properties_tab.width_scale_spin.value(), self.properties_tab.height_scale_spin.value())

    def use_scale_y(self, value):
        self.use_scale(self.properties_tab.width_scale_spin.value(), self.properties_tab.height_scale_spin.value())

    def use_scale(self, x_value, y_value):
        try:
            items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
            if not items:
                return

            old_transforms = [item.transform() for item in items]
            new_transforms = []

            for item in items:
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
                new_transforms.append(transform)

            command = TransformCommand(items, old_transforms, new_transforms)
            self.canvas.addCommand(command)

        except Exception as e:
            print(f'Error during scaling: {e}')

    def use_scale_tool(self):
        self.scale_btn.setChecked(True)
        self.canvas_view.disable_item_flags()

        self.use_exit_grid()

    def use_rotate_tool(self):
        self.rotate_btn.setChecked(True)
        self.canvas_view.disable_item_flags()

        self.use_exit_grid()

    def use_rotate(self, value):
        items = self.canvas.selectedItems()
        if not items:
            return

        canvas_items = []
        old_rotations = []

        # Rotate each item around the center
        for item in items:
            if not isinstance(item, CanvasItem):
                if isinstance(item, LeaderLineItem):
                    item.childItems()[0].setSelected(False)
                    item.updatePathEndPoint()
                elif isinstance(item, CustomTextItem):
                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

                item.setTransformOriginPoint(item.boundingRect().center())
                canvas_items.append(item)
                old_rotations.append(item.rotation())

        if canvas_items:
            try:
                command = RotateCommand(self, canvas_items, old_rotations, value)
                self.canvas.addCommand(command)
            except Exception as e:
                # Handle the exception (e.g., logging)
                print(f'Exception: {e}')

    def use_rotate_direction(self, dir: str):
        items = self.canvas.selectedItems()
        if not items:
            return

        canvas_items = []
        old_rotations = []
        new_rotations = []

        # Determine the rotation direction and angle
        rotation_change = -90 if dir == 'ccw' else 90

        # Rotate each item around the center
        for item in items:
            if not isinstance(item, CanvasItem):
                if isinstance(item, LeaderLineItem):
                    item.childItems()[0].setSelected(False)
                    item.updatePathEndPoint()
                elif isinstance(item, CustomTextItem):
                    if isinstance(item.parentItem(), LeaderLineItem):
                        item.parentItem().updatePathEndPoint()

                item.setTransformOriginPoint(item.boundingRect().center())
                canvas_items.append(item)
                old_rotations.append(item.rotation())
                new_rotations.append(item.rotation() + rotation_change)

        if canvas_items:
            try:
                command = RotateDirectionCommand(self, canvas_items, old_rotations, new_rotations)
                self.canvas.addCommand(command)
            except Exception as e:
                # Handle the exception (e.g., logging)
                print(f'Exception: {e}')

    def use_change_view(self):
        value = self.view_zoom_spin.value() / 100

        self.canvas_view.resetTransform()
        self.canvas_view.scale(value, value)
        self.canvas_view.rotate(self.view_rotate_spin.value())

    def use_raise_layer(self):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        if not items:
            return

        old_z_values = [item.zValue() for item in items]
        new_z_values = [z + 1 for z in old_z_values]

        command = LayerChangeCommand(items, old_z_values, new_z_values)
        self.canvas.addCommand(command)

    def use_lower_layer(self):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem) and item.zValue() > 0]
        if not items:
            QMessageBox.critical(self, 'Lower Layer', 'You cannot lower this Element any lower.')
            return

        old_z_values = [item.zValue() for item in items]
        new_z_values = [z - 1 for z in old_z_values]

        command = LayerChangeCommand(items, old_z_values, new_z_values)
        self.canvas.addCommand(command)

    def use_bring_to_front(self):
        selected_items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        if not selected_items:
            return

        max_z = max([item.zValue() for item in self.canvas.items()])
        old_z_values = [item.zValue() for item in selected_items]
        new_z_values = [max_z + 1] * len(selected_items)  # Move all selected items to the front

        command = LayerChangeCommand(selected_items, old_z_values, new_z_values)
        self.canvas.addCommand(command)

    def use_vectorize(self):
        # Initialize progress dialog
        progress_dialog = QProgressDialog("Converting images...", "Cancel", 0, len(self.canvas.selectedItems()), self)
        progress_dialog.setWindowTitle("Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setFixedWidth(300)
        progress_dialog.setAutoClose(True)  # Automatically closes after reaching the maximum value

        # Update the progress
        progress = 0
        progress_dialog.setValue(progress)

        converted_items = []

        for item in self.canvas.selectedItems():
            # Check if the user pressed cancel
            if progress_dialog.wasCanceled():
                break

            if isinstance(item, CustomPixmapItem):
                try:
                    temp_pixmap_path = os.path.abspath('internal data/temp_pixmap.png')
                    item.pixmap().save(temp_pixmap_path)

                    # Convert the pixmap to SVG
                    vtracer.convert_image_to_svg_py(
                        temp_pixmap_path,
                        'internal data/output.svg',
                        colormode=self.image_trace_tab.colormode_combo.itemData(
                            self.image_trace_tab.colormode_combo.currentIndex()),
                        hierarchical='cutout',
                        mode=self.image_trace_tab.mode_combo.itemData(
                            self.image_trace_tab.mode_combo.currentIndex()),
                        filter_speckle=4,
                        color_precision=6,
                        layer_difference=16,
                        corner_threshold=self.image_trace_tab.corner_threshold_spin.value(),
                        length_threshold=4.0,
                        max_iterations=10,
                        splice_threshold=45,
                        path_precision=3
                    )

                    # Add the item to the scene
                    svg_item = CustomSvgItem()
                    svg_item.store_filename('')
                    svg_item.setToolTip('Imported SVG')
                    svg_item.setPos(item.x() + 10, item.y() + 10)
                    self.create_item_attributes(svg_item)
                    converted_items.append(svg_item)

                    with open(os.path.abspath('internal data/output.svg'), 'r', encoding='utf-8') as f:
                        data = f.read()
                        svg_item.loadFromData(data)

                    # Remove the temporary files
                    if os.path.exists(temp_pixmap_path):
                        os.remove(temp_pixmap_path)
                    os.remove(os.path.abspath('internal data/output.svg'))

                    # Update progress
                    progress += 1
                    progress_dialog.setValue(progress)

                except Exception as e:
                    QMessageBox.critical(self, 'Convert Error', f'Failed to convert bitmap to vector: {e}')
                    return  # Exit the loop on error

        if not progress_dialog.wasCanceled():
            if converted_items:
                add_command = MultiAddItemCommand(self.canvas, converted_items)
                self.canvas.addCommand(add_command)

            QMessageBox.information(self, 'Convert Finished', 'All vectors converted successfully.')

        else:
            del converted_items

    def use_set_item_pos(self):
        self.canvas.blockSignals(True)
        try:
            # Get target position from spin boxes
            target_x = self.properties_tab.x_pos_spin.value()
            target_y = self.properties_tab.y_pos_spin.value()

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

    def use_flip_horizontal(self):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        old_transforms = [item.transform() for item in items]
        new_transforms = []

        for item in items:
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)
                item.updatePathEndPoint()

            transform = item.transform()
            transform.scale(-1, 1)  # Flip horizontally
            new_transforms.append(transform)

        if items:
            command = TransformCommand(items, old_transforms, new_transforms)
            self.canvas.addCommand(command)

    def use_flip_vertical(self):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        old_transforms = [item.transform() for item in items]
        new_transforms = []

        for item in items:
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)
                item.updatePathEndPoint()

            transform = item.transform()
            transform.scale(1, -1)  # Flip vertically
            new_transforms.append(transform)

        if items:
            command = TransformCommand(items, old_transforms, new_transforms)
            self.canvas.addCommand(command)

    def use_mirror(self, direction):
        for item in self.canvas.selectedItems():
            if not isinstance(item, CanvasItem):
                self.use_escape()
                child = item.duplicate()
                child.setSelected(True)
                child.setPos(item.pos())

                if direction == 'h':
                    self.use_flip_horizontal()

                    if self.properties_tab.width_scale_spin.value() < 0:
                        child.setX(child.pos().x() - child.boundingRect().width())
                    else:
                        child.setX(child.pos().x() + child.boundingRect().width())

                elif direction == 'v':
                    self.use_flip_vertical()

                    if self.properties_tab.height_scale_spin.value() < 0:
                        child.setY(child.pos().y() - child.boundingRect().height())
                    else:
                        child.setY(child.pos().y() + child.boundingRect().height())

    def use_change_opacity(self, value):
        # Calculate opacity value (normalize slider's value to the range 0.0-1.0)
        opacity = value / self.properties_tab.opacity_spin.maximum()

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

    def use_reset_item(self):
        items = [item for item in self.canvas.selectedItems() if not isinstance(item, CanvasItem)]
        if not items:
            return

        try:
            command = ResetItemCommand(items)
            self.canvas.addCommand(command)
            self.update_transform_ui()
        except Exception as e:
            print(f'Error during resetting items: {e}')

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

            else:
                item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                item.setFlag(QGraphicsItem.ItemIsMovable, False)

    def use_exit_add_canvas(self):
        # Deactivate the add canvas tool
        self.select_btn.trigger()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                item.setCanvasActive(False)

        if self.scene_tab.gsnap_check_btn.isChecked():
            self.scene_tab.gsnap_check_btn.click()

    def use_exit_grid(self):
        if self.scene_tab.gsnap_check_btn.isChecked():
            self.scene_tab.gsnap_check_btn.click()

    def use_smooth_path(self):
        items = [item for item in self.canvas.selectedItems() if isinstance(item, CustomPathItem) and
                 item.alreadySmooth() is not True]
        if not items:
            return

        new_paths = []
        old_paths = []

        try:
            for item in items:
                smoothed_path = item.smooth_path(item.path(), 0.1)
                new_paths.append(smoothed_path)
                old_paths.append(item.path())

            command = SmoothPathCommand(self.canvas, items, new_paths, old_paths)
            self.canvas.addCommand(command)
        except Exception as e:
            # Handle the exception (e.g., logging)
            print(f'Exception: {e}')

    def use_close_path(self):
        items = [item for item in self.canvas.selectedItems() if isinstance(item, CustomPathItem)]
        if not items:
            return

        try:
            command = CloseSubpathCommand(items, self.canvas)
            self.canvas.addCommand(command)
        except Exception as e:
            # Handle the exception (e.g., logging)
            print(f'Exception: {e}')

    def use_hide_item(self):
        items = self.canvas.selectedItems()
        if not items:
            return

        canvas_items = []
        old_visibilities = []

        for item in items:
            if isinstance(item, LeaderLineItem):
                item.childItems()[0].setSelected(False)

            elif isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    canvas_items.append(item.parentItem())
                    old_visibilities.append(item.parentItem().isVisible())
                    break

            canvas_items.append(item)
            old_visibilities.append(item.isVisible())

        if canvas_items:
            try:
                command = HideCommand(canvas_items, old_visibilities, False)
                self.canvas.addCommand(command)
            except Exception as e:
                # Handle the exception (e.g., logging)
                print(f'Exception: {e}')

    def use_unhide_all(self):
        items = self.canvas.items()
        if not items:
            return

        canvas_items = []
        old_visibilities = []

        for item in items:
            if not isinstance(item, CanvasTextItem):
                if not item.isVisible():
                    canvas_items.append(item)
                    old_visibilities.append(item.isVisible())

        if canvas_items:
            try:
                command = HideCommand(canvas_items, old_visibilities, True)
                self.canvas.addCommand(command)
            except Exception as e:
                # Handle the exception (e.g., logging)
                print(f'Exception: {e}')

    def use_align_left(self):
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            first_sel_item = selected_items[0]
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(
                    (first_sel_item.mapToScene(first_sel_item.boundingRect().topLeft()).x()) -
                    (item.mapToScene(item.boundingRect().topLeft()).x()),
                    0
                )
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
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
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            last_sel_item = selected_items[0]
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(
                    (last_sel_item.mapToScene(last_sel_item.boundingRect().topRight()).x()) -
                    (item.mapToScene(item.boundingRect().topRight()).x()),
                    0
                )
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
                for i in self.canvas.items():
                    if isinstance(i, CanvasItem):
                        for colision in i.collidingItems():
                            if colision == item:
                                new = QPointF(
                                    (
                                            i.sceneBoundingRect().x() + i.sceneBoundingRect().width()) - item.sceneBoundingRect().width(),
                                    item.y()
                                )
                                command = PositionChangeCommand(self, item, item.pos(), new)
                                self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_center(self):
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            center_x = sum(item.sceneBoundingRect().center().x() for item in selected_items) / len(selected_items)
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(center_x - item.sceneBoundingRect().center().x(), 0)
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
                for i in self.canvas.items():
                    if isinstance(i, CanvasItem):
                        for colision in i.collidingItems():
                            if colision == item:
                                new = QPointF(i.sceneBoundingRect().center().x() - item.boundingRect().center().x(),
                                              item.y())
                                command = PositionChangeCommand(self, item, item.pos(), new)
                                self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_top(self):
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            top_y = min(item.sceneBoundingRect().top() for item in selected_items)
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(0, top_y - item.sceneBoundingRect().top())
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
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
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            bottom_y = max(item.sceneBoundingRect().bottom() for item in selected_items)
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(0, bottom_y - item.sceneBoundingRect().bottom())
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
                for i in self.canvas.items():
                    if isinstance(i, CanvasItem):
                        for colision in i.collidingItems():
                            if colision == item:
                                new = QPointF(
                                    item.x(),
                                    (i.y() + i.boundingRect().height()) - item.boundingRect().height()
                                )
                                command = PositionChangeCommand(self, item, item.pos(), new)
                                self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_align_middle(self):
        selected_items = self.canvas.selectedItems()
        if len(selected_items) > 1:
            middle_y = sum(item.sceneBoundingRect().center().y() for item in selected_items) / len(selected_items)
            old_positions = [item.pos() for item in selected_items]
            new_positions = [
                QPointF(0, middle_y - item.sceneBoundingRect().center().y())
                for item in selected_items
            ]
            command = AlignMultipleItemsCommand(self, selected_items, old_positions, new_positions)
            self.canvas.addCommand(command)

        elif len(selected_items) == 1:
            item = selected_items[0]
            if not isinstance(item, CanvasItem):
                for i in self.canvas.items():
                    if isinstance(i, CanvasItem):
                        for colision in i.collidingItems():
                            if colision == item:
                                new = QPointF(item.x(),
                                              i.sceneBoundingRect().center().y() - item.boundingRect().center().y())
                                command = PositionChangeCommand(self, item, item.pos(), new)
                                self.canvas.addCommand(command)

        self.update_transform_ui()
        self.update('item_update')

    def use_enable_grid(self):
        if self.scene_tab.gsnap_check_btn.isChecked():
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

    def use_insert_shape(self, shape: str):
        path = QPainterPath()

        if shape == 'rect':
            path.addRect(QRectF(0, 0, 100, 100))
            item = CustomPathItem(path)
            item.setPen(self.canvas_view.pen)
            item.setBrush(self.canvas_view.stroke_fill)

        elif shape == 'circle':
            path.addEllipse(QRectF(0, 0, 100, 100))
            item = CustomPathItem(path)
            item.setPen(self.canvas_view.pen)
            item.setBrush(self.canvas_view.stroke_fill)

        elif shape == 'triangle':
            poly = QPolygonF()
            half_width = 50
            # Calculate the height of the equilateral triangle
            height = (math.sqrt(3) / 2) * 100
            # Add the points to the polygon
            poly.append(QPointF(-half_width, height / 2))
            poly.append(QPointF(half_width, height / 2))
            poly.append(QPointF(0., -height / 2))
            poly.append(QPointF(-half_width, height / 2))

            path.addPolygon(poly)
            item = CustomPathItem(path)
            item.setPen(self.canvas_view.pen)
            item.setBrush(self.canvas_view.stroke_fill)

        item.setToolTip('Path')

        self.canvas.addCommand(AddItemCommand(self.canvas, item))
        self.create_item_attributes(item)

    def use_repair_file(self):
        self.w = FileDataRepairer(self)

    def insert_image(self):
        self.canvas.importManager.importFile()

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)

    def send_to_icloud(self):
        self.w = iCloudIntegraterWin(self.canvas, self)
        self.w.show()

    def open_recent(self, filename: str):
        self.canvas.manager.load_from_file(filename, self)

    def show_version(self):
        self.w = VersionWin(self.canvas.mpversion, self)
        self.w.show()

    def show_about(self):
        self.w = AboutWin(self)
        self.w.show()

    def show_find_action(self):
        self.w = FindActionWin(self.actions, self)
        self.w.show()

    def show_disclaimer(self):
        w = DisclaimerWin('internal data/_settings.json')

        result = w.exec_()

        if result == QMessageBox.Yes:
            if w.show_on_startup_btn.isChecked():
                return

            _data = self.read_settings()

            for data in _data:
                data['disclaimer_read'] = True

            self.write_settings(_data)

        else:
            self.close()

    def show_settings(self):
        self.w = SettingsWin(self)
        self.w.show()

    def show_scripts(self):
        self.w = ScriptingWin(self)
        self.w.show()

    def show_tip_of_the_day(self):
        with open('internal data/_tips.txt', 'r') as f:
            content = [line for line in f if not line.startswith('#') and line.strip()]
            line = random.randint(0, len(content) - 1)

        self.canvas_view.showMessage('Tip of the Day', content[line])

    def show_3d_viewer(self):
        self.w = SceneTo3DView(self.canvas, self)
        self.w.show()

    def read_settings(self):
        with open('internal data/_settings.json', 'r') as f:
            return json.load(f)

    def read_recent_files(self):
        with open('internal data/_recent_files.json', 'r') as f:
            return json.load(f)

    def write_settings(self, data):
        with open('internal data/_settings.json', 'w') as f:
            return json.dump(data, f, indent=4)

    def write_recent_file(self, data):
        with open('internal data/_recent_files.json', 'w') as f:
            return json.dump(data, f, indent=4)

    def open_settings_data(self):
        for user_data in self.read_settings():
            self.view_as(user_data['saved_view'])

            self.addToolBar(Qt.LeftToolBarArea if user_data['toolbar_pos'] == 1 else Qt.RightToolBarArea, self.toolbar)
            self.addDockWidget(Qt.RightDockWidgetArea if user_data['toolbox_pos'] == 1 else Qt.LeftDockWidgetArea,
                               self.tab_view_dock)
            self.item_toolbar.setHidden(user_data['control_toolbar_hidden'])
            self.toolbar.setHidden(user_data['toolbar_hidden'])
            self.tab_view_dock.collapse() if user_data['toolbox_collapsed'] else self.tab_view_dock.expand()
            self.undo_stack.setUndoLimit(user_data['undo_limit'])
            self.canvas.setGridSize(user_data['grid_size'])
            self.toolbox.setCurrentIndex(user_data['toolbox_index'])

            if user_data['geometry'][0] == 'maximized':
                self.showMaximized()

            else:
                self.setGeometry(user_data['geometry'][0],
                                 user_data['geometry'][1],
                                 user_data['geometry'][2],
                                 user_data['geometry'][3]
                                 )

            for action in self.action_group.actions():
                if action.text() == user_data['last_used_tool']:
                    action.trigger()

            if not user_data['disclaimer_read']:
                self.show_disclaimer()

            if user_data['use_gpu']:
                viewport = CustomViewport()
                viewport.format().setSamples(user_data['gpu_samples'])
                self.canvas_view.setViewport(viewport)

            if user_data['show_daily_tips']:
                self.show_tip_of_the_day()

        self.check_for_updates(show_message=True)

    def open_recent_file_data(self):
        data = self.read_recent_files()

        for _data in data:
            recent_files = []
            seen = set()
            for item in _data['recent_files']:
                if item not in seen:
                    if os.path.exists(item):
                        recent_files.append(item)
                    seen.add(item)

            _data['recent_files'] = recent_files  # Update the recent files in the data

            max_recent_files = 5

            for d in self.read_settings():
                max_recent_files = d['recent_file_display_limit']

            for recent_file in recent_files[:max_recent_files]:  # Slice the list
                action = QAction(os.path.basename(recent_file), self)
                action.setToolTip(os.path.abspath(recent_file))
                action_tooltip = action.toolTip()
                action.triggered.connect(lambda checked, path=action_tooltip: self.open_recent(path))

                self.open_recent_menu.addAction(action)

        self.write_recent_file(data)

    def update_recent_file_data(self, file: str):
        data = self.read_recent_files()

        for _data in data:
            # write new data and append it
            _data['recent_files'].append(file)

            recent_files = []
            seen = set()
            for item in _data['recent_files']:
                if item not in seen:
                    recent_files.append(item)
                    seen.add(item)

            _data['recent_files'] = recent_files

            self.write_recent_file(data)

            max_recent_files = 5

            for d in self.read_settings():
                max_recent_files = d['recent_file_display_limit']

            for recent_file in recent_files[:max_recent_files]:
                if os.path.exists(recent_file):
                    if os.path.abspath(recent_file) not in (action.toolTip() for action in
                                                            self.open_recent_menu.actions()):
                        action = QAction(os.path.basename(recent_file), self)
                        action.setToolTip(os.path.abspath(recent_file))
                        action_tooltip = action.toolTip()
                        action.triggered.connect(lambda checked, path=action_tooltip: self.open_recent(path))

                        self.open_recent_menu.addAction(action)

    def toggle_control_toolbar(self, action: QAction) -> None:
        if action.isChecked():
            self.item_toolbar.setHidden(False)

        else:
            self.view_as('control_bar_hidden')

    def control_toolbar_visibility_changed(self):
        if self.item_toolbar.isVisible():
            self.view_menu.actions()[0].setChecked(True)

        else:
            self.view_menu.actions()[0].setChecked(False)

    def view_as(self, view: str) -> None:
        if view == 'read_only':
            self.unhide()
            self.cur_view = 'read_only'
            self.tab_view_dock.setHidden(True)
            self.item_toolbar.setHidden(True)
            self.toolbar.setHidden(True)

        elif view == 'tools_only':
            self.unhide()
            self.item_toolbar.setHidden(True)
            self.tab_view_dock.setHidden(True)

        elif view == 'simple':
            self.unhide()
            self.cur_view = 'simple'
            self.item_toolbar.setHidden(True)
            self.toolbar.setIconSize(QSize(48, 48))
            self.toolbar.setFixedWidth(70)
            self.drawing_toolbutton.setIconSize(QSize(48, 48))
            self.tab_view_dock.collapse()

            self.menuBar().setStyleSheet('font-size: 30px;')

        elif view == 'swapped':
            self.unhide()
            self.addDockWidget(Qt.LeftDockWidgetArea, self.tab_view_dock)
            self.addToolBar(Qt.RightToolBarArea, self.toolbar)

        elif view == 'control_bar_hidden':
            self.item_toolbar.setHidden(True)

        else:
            self.unhide()

    def current_view(self) -> str:
        return self.cur_view

    def current_toolbar_pos(self):
        return 1 if self.toolBarArea(self.toolbar) == Qt.LeftToolBarArea else 2

    def current_toolbox_pos(self):
        return 1 if self.dockWidgetArea(self.tab_view_dock) == Qt.RightDockWidgetArea else 2

    def unhide(self) -> None:
        self.tab_view_dock.setHidden(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tab_view_dock)
        self.item_toolbar.setHidden(False)
        self.item_toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setHidden(False)
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setFixedWidth(60)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        self.drawing_toolbutton.setIconSize(QSize(10, 10))

        self.menuBar().setStyleSheet('font-size: 16px;')

        if self.tab_view_dock.isCollapsed():
            self.tab_view_dock.expand()

        self.cur_view = ''

    def show_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
            return

        self.showFullScreen()

    def check_for_updates(self, show_message=False):
        current_version = self.canvas.mpversion
        latest_version = get_latest_version(self)

        if latest_version > current_version:
            download = QMessageBox.information(self, 'Update Available',
                                               f'New version {latest_version} is available. '
                                               f'Would you like to download it?',
                                               QMessageBox.Yes | QMessageBox.Cancel)
            if download == QMessageBox.Yes:
                webbrowser.open('https://sites.google.com/view/mprun/download')

        else:
            if show_message is False:
                QMessageBox.information(self, 'No Updates', 'You are using the latest version.')


def main() -> None:
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    splash = QSplashScreen(QIcon('ui/Main Logos/mprun_splash.png').pixmap(QSize(7000, 600)), Qt.WindowStaysOnTopHint)
    splash.show()

    app.processEvents()

    if sys.platform == 'darwin':
        app.setStyleSheet(macCSS)

    else:
        app.setStyleSheet(windowsCSS)

    window = MPRUN()
    splash.finish(window)

    window.open_settings_data()
    window.open_recent_file_data()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        window.open_recent(file_path)

    # Crash handler
    def handle_exception(exctype, value, tb):
        window.canvas.manager.emergency_save()
        QMessageBox.critical(None, 'Uh Oh', f'''<h4>MPRUN encountered an error!</h4> 
        If the cause is known, please report it to our 
        <b><a href="https://github.com/ktechhydle/mprun_repo/issues">Issue Tracker</a></b> 
        on GitHub, and we will fix this error as soon as possible. You can also
        <b><a href="https://github.com/ktechhydle/mprun_repo/discussions/5">contact the developers</a></b>
        to get troubleshooting guides and quick fixes for your issue.
        
        <h4>Debug Info:</h4>
        <br>
        {exctype, value, tb}
        ''')
        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    sys.exit(app.exec_())


if nameismain:
    main()
