# This file is the "main" script that can be run to see the full app

import random
from src.scripts.imports import *
from mp_software_stylesheets.styles import macCSS, windowsCSS
from src.scripts.raw_functions import nameismain, ItemStack
from src.scripts.app_internal import *
from src.gui.app_screens import AboutWin, VersionWin, FindActionWin, DisclaimerWin, SettingsWin
from src.gui.panels import PropertiesPanel, CharactersPanel, LibrariesPanel, ImageTracingPanel, QuickActionsPanel, \
    CanvasEditorPanel
from src.gui.icloud_integrator import iCloudIntegraterWin
from src.gui.custom_widgets import *
from src.framework.graphics_framework import CustomGraphicsView, CustomGraphicsScene, CustomViewport
from src.framework.serializer import MPDataRepairer

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


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

        # Create UI
        self.create_ui()
        self.show()

    def closeEvent(self, event):
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
            _data['geometry'] = ['maximized'] if self.isMaximized() else [self.x(), self.y(), self.width(),
                                                                          self.height()]
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
        self.create_actions_dict()
        self.create_initial_canvas()
        self.create_menu()
        self.init_toolbars()
        self.create_toolbox()
        self.create_toolbar1()
        self.create_toolbar2()
        self.create_view()
        self.create_default_objects()
        self.update()

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
        self.view_menu = self.menu_bar.addMenu('&View')
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
        new_action.triggered.connect(self.canvas.manager.restore)

        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence('Ctrl+O'))
        open_action.triggered.connect(lambda: self.canvas.manager.load(self))

        self.open_recent_menu = QMenu('Open Recent')

        open_template_action = QAction('Open Template', self)
        open_template_action.triggered.connect(self.canvas.template_manager.load_template)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.canvas.manager.save)

        saveas_action = QAction('Save As', self)
        saveas_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        saveas_action.triggered.connect(self.canvas.manager.saveas)

        saveas_template_action = QAction('Save As Template', self)
        saveas_template_action.triggered.connect(self.canvas.template_manager.save_template)

        save_to_icloud_action = QAction('Save To iCloud', self)
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

        # Create tools submenus and actions
        drawing_menu = self.tool_menu.addMenu('Drawing')
        path_menu = self.tool_menu.addMenu('Path')
        characters_menu = self.tool_menu.addMenu('Characters')
        image_menu = self.tool_menu.addMenu('Image')
        scene_menu = self.tool_menu.addMenu('Scene')

        select_action = QAction('Select', self)
        select_action.setShortcut(QKeySequence(Qt.Key_Space))
        select_action.triggered.connect(self.use_select)

        pan_action = QAction('Pan', self)
        pan_action.setShortcut(QKeySequence('P'))
        pan_action.triggered.connect(self.use_pan)

        rotate_view_action = QAction('Rotate', self)
        rotate_view_action.triggered.connect(lambda: self.view_rotate_spin.setFocus())

        zoom_view_action = QAction('Zoom', self)
        zoom_view_action.triggered.connect(lambda: self.view_zoom_spin.setFocus())

        arrange_canvases_action = QAction('Arrange Canvases', self)
        arrange_canvases_action.setShortcut(Qt.Key_F3)
        arrange_canvases_action.triggered.connect(self.canvas.arrange)

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

        add_shape_menu = QMenu('Add Shape', self)
        add_shape_rect = QAction('Add Rectangle', self)
        add_shape_rect.triggered.connect(lambda: self.use_insert_shape('rect'))
        add_shape_circle = QAction('Add Circle', self)
        add_shape_circle.triggered.connect(lambda: self.use_insert_shape('circle'))
        add_shape_tri = QAction('Add Triangle', self)
        add_shape_tri.triggered.connect(lambda: self.use_insert_shape('triangle'))

        add_shape_menu.addAction(add_shape_rect)
        add_shape_menu.addAction(add_shape_circle)
        add_shape_menu.addAction(add_shape_tri)

        # Create edit actions
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

        # Create object actions
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

        # Creat view menu actions
        fullscreen_view_action = QAction('Full Screen', self)
        fullscreen_view_action.setShortcut(Qt.Key_F11)
        fullscreen_view_action.triggered.connect(self.showMaximized)

        control_toolbar_view_action = QAction('Control Toolbar', self)
        control_toolbar_view_action.setCheckable(True)
        control_toolbar_view_action.setChecked(True)
        control_toolbar_view_action.setShortcut(Qt.Key_F12)
        control_toolbar_view_action.triggered.connect(lambda: self.toggle_control_toolbar(control_toolbar_view_action))

        view_options_menu = QMenu('Views', self)

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

        zoom_and_rotate_action = QWidgetAction(self.menu_bar)

        self.view_zoom_spin = QSpinBox()
        self.view_zoom_spin.setToolTip('Zoom view')
        self.view_zoom_spin.setRange(1, 5000)
        # self.view_zoom_spin.setFixedWidth(50)
        self.view_zoom_spin.setSuffix('%')
        self.view_zoom_spin.setValue(100)
        self.view_zoom_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.view_zoom_spin.valueChanged.connect(self.use_change_view)

        self.view_rotate_spin = QSpinBox()
        self.view_rotate_spin.setToolTip('Rotate view')
        # self.view_rotate_spin.setFixedWidth(50)
        self.view_rotate_spin.setMinimum(-10000)
        self.view_rotate_spin.setMaximum(10000)
        self.view_rotate_spin.setSuffix('°')
        self.view_rotate_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.view_rotate_spin.valueChanged.connect(self.use_change_view)

        zoom_and_rotate_hlayout1 = ToolbarHorizontalLayout()
        zoom_and_rotate_hlayout1.layout.addWidget(QLabel('<i>Zoom:</i>'))
        zoom_and_rotate_hlayout1.layout.addWidget(self.view_zoom_spin)
        zoom_and_rotate_hlayout2 = ToolbarHorizontalLayout()
        zoom_and_rotate_hlayout2.layout.addWidget(QLabel('<i>Rotation:</i>'))
        zoom_and_rotate_hlayout2.layout.addWidget(self.view_rotate_spin)
        zoom_and_rotate_widget = QWidget()
        zoom_and_rotate_widget.setLayout(QVBoxLayout())
        zoom_and_rotate_widget.layout().addWidget(zoom_and_rotate_hlayout1)
        zoom_and_rotate_widget.layout().addWidget(zoom_and_rotate_hlayout2)
        zoom_and_rotate_action.setDefaultWidget(zoom_and_rotate_widget)

        # Create help menu actions
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)

        show_version_action = QAction('Version', self)
        show_version_action.triggered.connect(self.show_version)

        find_action_action = QAction('Find Action', self)
        find_action_action.triggered.connect(self.show_find_action)

        browse_tutorials_action = QAction('Browse Tutorials', self)
        browse_tutorials_action.setShortcut(Qt.Key_F1)
        browse_tutorials_action.triggered.connect(
            lambda: webbrowser.open('https://sites.google.com/view/mprun/learn#h.dhbfsx84043q'))

        view_settings_action = QAction('Settings', self)
        view_settings_action.setShortcut(Qt.Key_F2)
        view_settings_action.triggered.connect(self.show_settings)

        reload_ui_action = QAction('Restart User Interface', self)
        reload_ui_action.setShortcut(Qt.Key_F4)
        reload_ui_action.triggered.connect(self.open_settings_data)

        show_tip_of_the_day_action = QAction('Show Tip Of The Day', self)
        show_tip_of_the_day_action.triggered.connect(self.show_tip_of_the_day)

        # Add actions
        self.file_menu.addAction(add_canvas_action)
        self.file_menu.addAction(insert_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(new_action)
        self.file_menu.addAction(open_action)
        self.file_menu.addMenu(self.open_recent_menu)
        self.file_menu.addAction(open_template_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)
        self.file_menu.addAction(saveas_template_action)
        self.file_menu.addAction(save_to_icloud_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_action)
        self.file_menu.addAction(export_multiple_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(repair_file_action)
        self.file_menu.addAction(close_action)

        self.edit_menu.addAction(undo_action)
        self.edit_menu.addAction(redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(copy_action)
        self.edit_menu.addAction(paste_action)
        self.edit_menu.addAction(delete_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(hard_delete_action)

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

        self.view_menu.addAction(control_toolbar_view_action)
        self.view_menu.addAction(fullscreen_view_action)
        self.view_menu.addMenu(view_options_menu)
        self.view_menu.addAction(zoom_and_rotate_action)

        self.help_menu.addAction(about_action)
        self.help_menu.addAction(show_version_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(find_action_action)
        self.help_menu.addAction(browse_tutorials_action)
        self.help_menu.addAction(view_settings_action)
        self.help_menu.addAction(reload_ui_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(show_tip_of_the_day_action)

        # Sub menu actions
        drawing_menu.addAction(path_action)
        drawing_menu.addAction(pen_action)
        drawing_menu.addAction(linelabel_action)
        drawing_menu.addMenu(add_shape_menu)

        path_menu.addAction(smooth_action)
        path_menu.addAction(close_subpath_action)
        path_menu.addAction(sculpt_path_action)

        characters_menu.addAction(text_action)

        image_menu.addAction(image_trace_action)

        scene_menu.addAction(select_action)
        scene_menu.addAction(pan_action)
        scene_menu.addAction(rotate_view_action)
        scene_menu.addAction(zoom_view_action)
        scene_menu.addAction(arrange_canvases_action)

        view_options_menu.addAction(read_only_view_action)
        view_options_menu.addAction(tools_only_view_action)
        view_options_menu.addAction(simple_view_action)
        view_options_menu.addAction(swapped_view_action)
        view_options_menu.addAction(default_view_action)

        # Add to actions dict
        self.actions['Insert'] = insert_action
        self.actions['Add Canvas'] = add_canvas_action
        self.actions['Open Template'] = open_template_action
        self.actions['Save As Template'] = saveas_template_action
        self.actions['Save To iCloud'] = save_to_icloud_action
        self.actions['Repair File'] = repair_file_action
        self.actions['Close'] = close_action
        self.actions['Select'] = select_action
        self.actions['Pan'] = pan_action
        self.actions['Rotate'] = rotate_view_action
        self.actions['Zoom'] = zoom_view_action
        self.actions['Arrange Canvases'] = arrange_canvases_action
        self.actions['Pen Draw'] = pen_action
        self.actions['Line and Label'] = linelabel_action
        self.actions['Text'] = text_action
        self.actions['Flip Horizontal'] = flip_horizontal_action
        self.actions['Flip Vertical'] = flip_vertical_action
        self.actions['Mirror Horizontal'] = mirror_horizontal_action
        self.actions['Mirror Vertical'] = mirror_vertical_action
        self.actions['Hide'] = hide_action
        self.actions['Unhide All'] = unhide_action
        self.actions['Raise Layer'] = raise_layer_action
        self.actions['Lower Layer'] = lower_layer_action
        self.actions['Clear Selection'] = clear_selection_action
        self.actions['Select Paths'] = select_paths_action
        self.actions['Select Text'] = select_text_action
        self.actions['Select Leader Lines'] = select_leaderline_action
        self.actions['Select Pixmaps'] = select_pixmaps_action
        self.actions['Select SVGs'] = select_svgs_action
        self.actions['Select Canvases'] = select_canvases_action
        self.actions['Full Screen'] = fullscreen_view_action
        self.actions['Control Toolbar'] = control_toolbar_view_action
        self.actions['About'] = about_action
        self.actions['Version'] = show_version_action
        self.actions['Find Action'] = find_action_action
        self.actions['Browse Tutorials'] = browse_tutorials_action
        self.actions['Settings'] = view_settings_action
        self.actions['Restart User Interface'] = reload_ui_action
        self.actions['Tip Of The Day'] = show_tip_of_the_day_action
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
        self.actions['Zoom View'] = self.view_zoom_spin
        self.actions['Rotate View'] = self.view_rotate_spin

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

    def create_toolbox(self):
        # ----action toolbar widgets----#

        # Dock widget
        self.toolbox = CustomToolbox(self)
        self.toolbox.setFixedWidth(300)
        self.toolbox.setMinimumHeight(680)

        self.tab_view_dock = CustomDockWidget(self.toolbox, self)
        self.tab_view_dock.setWindowTitle('Actions')
        self.tab_view_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        # Properties Tab
        self.properties_tab = PropertiesPanel(self.canvas, self)
        self.properties_tab.setFixedWidth(300)

        # Characters Tab
        self.characters_tab = CharactersPanel(self.canvas, self)
        self.characters_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.characters_tab.setFixedHeight(185)
        self.characters_tab.setFixedWidth(300)

        # Vectorize Tab
        self.image_trace_tab = ImageTracingPanel(self.canvas, self)
        self.image_trace_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.image_trace_tab.setFixedHeight(375)
        self.image_trace_tab.setFixedWidth(300)

        # Libraries Tab
        self.libraries_tab = LibrariesPanel(self.canvas)
        self.libraries_tab.setWindowFlag(Qt.WindowStaysOnTopHint)
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
        self.toolbox.addItem(self.image_trace_tab, 'Image Trace')
        self.toolbox.addItem(self.canvas_tab, 'Canvas')
        self.toolbox.addItem(self.quick_actions_tab, 'Quick Actions')

        # Add action toolbar actions
        self.tab_view_dock.setWidget(self.toolbox)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tab_view_dock)

        # Add to actions dict
        self.actions['Change Stroke Color'] = self.properties_tab.stroke_color_btn
        self.actions['Change Fill Color'] = self.properties_tab.fill_color_btn
        self.actions['Change Font Color'] = self.characters_tab.font_color_btn
        self.actions['Open Library'] = self.libraries_tab.open_library_button
        self.actions['Reload Library'] = self.libraries_tab.reload_library_button
        self.actions['Enable Grid'] = self.quick_actions_tab.gsnap_check_btn

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

        self.drawing_toolbutton = ToolButton()
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

        # Add to actions dict
        self.actions['Select'] = self.select_btn
        self.actions['Pan'] = self.pan_btn
        self.actions['Path Draw'] = self.path_btn
        self.actions['Pen Draw'] = self.pen_btn
        self.actions['Line and Label'] = self.label_btn
        self.actions['Add Text'] = self.add_text_btn
        self.actions['Scale'] = self.scale_btn
        self.actions['Rotate'] = self.rotate_btn
        self.actions['Hide'] = self.hide_btn
        self.actions['Unhide'] = self.unhide_btn
        self.actions['Add Canvas'] = self.add_canvas_btn
        self.actions['Insert Image'] = self.insert_btn

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

        # Add to actions dict
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
                                                            self.quick_actions_tab.gsnap_check_btn],
                                              self.view_zoom_spin)
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
            lambda: webbrowser.open('https://sites.google.com/view/mprun/learn#h.dhbfsx84043q')
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
        self.properties_tab.x_pos_spin.blockSignals(True)
        self.properties_tab.y_pos_spin.blockSignals(True)
        self.properties_tab.width_scale_spin.blockSignals(True)
        self.properties_tab.height_scale_spin.blockSignals(True)
        self.properties_tab.rotate_item_spin.blockSignals(True)
        self.properties_tab.opacity_spin.blockSignals(True)

        if len(self.canvas.selectedItems()) > 0:
            self.set_properties_tab_enabled(False)

            for item in self.canvas.selectedItems():
                self.properties_tab.x_pos_spin.setValue(int(item.sceneBoundingRect().x()))
                self.properties_tab.y_pos_spin.setValue(int(item.sceneBoundingRect().y()))
                self.properties_tab.rotate_item_spin.setValue(int(item.rotation()))
                self.properties_tab.opacity_spin.setValue(int(item.opacity() * 100))

                if item.transform().m11() < 0:
                    self.properties_tab.width_scale_spin.setValue(-item.boundingRect().width())

                else:
                    self.properties_tab.width_scale_spin.setValue(item.boundingRect().width())

                if item.transform().m22() < 0:
                    self.properties_tab.height_scale_spin.setValue(-item.boundingRect().height())

                else:
                    self.properties_tab.height_scale_spin.setValue(item.boundingRect().height())

                self.properties_tab.selection_label.setText(item.toolTip())

                if len(self.canvas.selectedItems()) > 1:
                    self.properties_tab.selection_label.setText(
                        f'Combined Selection ({len(self.canvas.selectedItems())} Items)')
                    self.properties_tab.x_pos_spin.setValue(int(self.canvas.selectedItemsSceneBoundingRect().x()))
                    self.properties_tab.y_pos_spin.setValue(int(self.canvas.selectedItemsSceneBoundingRect().y()))

        else:
            self.set_properties_tab_enabled(True)

        self.properties_tab.x_pos_spin.blockSignals(False)
        self.properties_tab.y_pos_spin.blockSignals(False)
        self.properties_tab.rotate_item_spin.blockSignals(False)
        self.properties_tab.opacity_spin.blockSignals(False)
        self.properties_tab.width_scale_spin.blockSignals(False)
        self.properties_tab.height_scale_spin.blockSignals(False)

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
                self.properties_tab.stroke_color_btn.setTransparent(False)
                self.properties_tab.stroke_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')
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
                self.properties_tab.fill_color_btn.setTransparent(False)
                self.properties_tab.fill_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')
                self.properties_tab.fill_color_btn.repaint()

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
                self.characters_tab.font_color_btn.setTransparent(False)
                self.characters_tab.font_color_btn.setStyleSheet(
                    f'background-color: {color.name()};')

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
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPixmapItem):
                try:
                    temp_pixmap_path = os.path.abspath('internal data/temp_pixmap.png')
                    item.pixmap().save(temp_pixmap_path)

                    # Convert the pixmap to SVG
                    vtracer.convert_image_to_svg_py(temp_pixmap_path,
                                                    'internal data/output.svg',
                                                    colormode=self.image_trace_tab.colormode_combo.itemData(
                                                        self.image_trace_tab.colormode_combo.currentIndex()),
                                                    # ["color"] or "binary"
                                                    hierarchical='cutout',  # ["stacked"] or "cutout"
                                                    mode=self.image_trace_tab.mode_combo.itemData(
                                                        self.image_trace_tab.mode_combo.currentIndex()),
                                                    # ["spline"] "polygon", or "none"
                                                    filter_speckle=4,  # default: 4
                                                    color_precision=6,  # default: 6
                                                    layer_difference=16,  # default: 16
                                                    corner_threshold=self.image_trace_tab.corner_threshold_spin.value(),
                                                    # default: 60
                                                    length_threshold=4.0,  # in [3.5, 10] default: 4.0
                                                    max_iterations=10,  # default: 10
                                                    splice_threshold=45,  # default: 45
                                                    path_precision=3  # default: 8
                                                    )

                    # Display information
                    QMessageBox.information(self, 'Convert Finished', 'Vector converted successfully.')

                    # Add the item to the scene
                    item = CustomSvgItem()
                    item.store_filename('')
                    item.setToolTip('Imported SVG')

                    with open(os.path.abspath('internal data/output.svg'), 'r', encoding='utf-8') as f:
                        data = f.read()
                        item.loadFromData(data)

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)
                    self.create_item_attributes(item)

                    # Remove the temporary file and SVG file
                    if os.path.exists(temp_pixmap_path):
                        os.remove(temp_pixmap_path)
                    os.remove(os.path.abspath('internal data/output.svg'))

                except Exception as e:
                    # Set cursor back
                    self.setCursor(Qt.ArrowCursor)

                    QMessageBox.critical(self, 'Convert Error', f'Failed to convert bitmap to vector: {e}')

    def use_duplicate(self):
        # Get selected items and create a copy
        selected_items = self.canvas.selectedItems()

        for item in selected_items:
            if isinstance(item, CanvasItem):
                item.duplicate()

            elif isinstance(item, CustomTextItem):
                item.duplicate()

            elif isinstance(item, CustomPathItem):
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

        if self.quick_actions_tab.gsnap_check_btn.isChecked():
            self.quick_actions_tab.gsnap_check_btn.click()

    def use_exit_grid(self):
        if self.quick_actions_tab.gsnap_check_btn.isChecked():
            self.quick_actions_tab.gsnap_check_btn.click()

    def use_smooth_path(self):
        items = [item for item in self.canvas.selectedItems() if isinstance(item, CustomPathItem) and not item.smooth]
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
        if self.quick_actions_tab.gsnap_check_btn.isChecked():
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

        self.canvas.addCommand(AddItemCommand(self.canvas, item))
        self.create_item_attributes(item)

    def use_repair_file(self):
        self.w = MPDataRepairer(self)

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
                self.canvas_view.setViewport(CustomViewport())

            if user_data['show_daily_tips']:
                self.show_tip_of_the_day()

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

            for recent_file in recent_files:
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

            # add an action to the recent files menu
            for recent_file in recent_files:
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

    def show_tip_of_the_day(self):
        with open('internal data/_tips.txt', 'r') as f:
            content = f.readlines()
            line = random.randint(0, len(content) - 1)

            self.canvas_view.showMessage('Tip of the Day', content[line])

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

    sys.exit(app.exec_())


if nameismain:
    main()
