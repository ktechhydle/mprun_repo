import sys
import math
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

class item_stack:
    def __init__(self, initial_value=""):
        self._value = initial_value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

class CustomGraphicsItemGroup(QGraphicsItemGroup):

    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.mouse_offset = QPoint(0, 0)
        self.block_size = 10
        self.widget = widget

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setColor(QColor("#e00202"))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.widget.isChecked():
            if self.isSelected():
                # Calculate the position relative to the scene's coordinate system
                scene_pos = event.scenePos()
                x = (
                    int(scene_pos.x() / self.block_size) * self.block_size
                    - self.mouse_offset.x()
                )
                y = (
                    int(scene_pos.y() / self.block_size) * self.block_size
                    - self.mouse_offset.y()
                )

                # Set the position relative to the scene's coordinate system
                self.setPos(x, y)
            else:
                # Call the superclass's mouseMoveEvent to move the item as normal
                super().mouseMoveEvent(event)

        else:
            # Call the superclass's mouseMoveEvent to move the item as normal
            super().mouseMoveEvent(event)

class EditableTextBlock(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Editable Text Block')

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.setFocus(Qt.MouseFocusReason)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas, button, button2):
        super().__init__()
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.button = button
        self.button2 = button2
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None

    def update_pen(self, pen):
        self.pen = pen

    def mousePressEvent(self, event):
        if self.button.isChecked():
            self.button2.setChecked(False)

            if event.button() == Qt.LeftButton:
                self.path = QPainterPath()  # Create a new QPainterPath
                self.path.moveTo(self.mapToScene(event.pos()))
                self.last_point = event.pos()
                self.setDragMode(QGraphicsView.NoDrag)

        elif self.button2.isChecked():
            self.button.setChecked(False)

            if event.button() == Qt.LeftButton:
                self.path2 = QPainterPath()  # Create a new QPainterPath
                self.path2.moveTo(self.mapToScene(event.pos()))
                self.setDragMode(QGraphicsView.NoDrag)

                self.text = EditableTextBlock('An Editable Text Block')
                self.text.setPos(self.mapToScene(event.pos()))
                self.text.setDefaultTextColor(QColor('black'))
                self.text.setToolTip("Partially locked text block (This item's position is determined by the position of another element)")

                self.rect = QGraphicsRectItem(self.text.boundingRect())
                self.rect.setPen(self.pen)
                self.rect.setPos(self.mapToScene(event.pos()))

                self.canvas.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.button.isChecked():
            if event.buttons() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()
                self.last_point = event.pos()

                if self.temp_path_item:
                    self.canvas.removeItem(self.temp_path_item)

                # Load path as QGraphicsItem
                self.temp_path_item = QGraphicsPathItem(self.path)
                self.temp_path_item.setPen(self.pen)
                self.temp_path_item.setZValue(2)

                self.canvas.addItem(self.temp_path_item)

                self.canvas.update()

        elif self.button2.isChecked():
            if event.button() == Qt.LeftButton:
                self.path2.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.button.isChecked():
            if event.button() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))

                if self.temp_path_item:
                    self.canvas.removeItem(self.temp_path_item)

                self.canvas.update()

                # Load path as QGraphicsItem
                path_item = QGraphicsPathItem(self.path)
                path_item.setPen(self.pen)
                path_item.setZValue(2)

                # Add item
                self.canvas.addItem(path_item)

                # Set Flags
                path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                path_item.setFlag(QGraphicsItem.ItemIsMovable)

                # Set Tooltop
                path_item.setToolTip('MPRUN Path Element')

                # Check if item is selected or moved so we can turn tool off
                if self.canvas.selectedItems():
                    self.button.setChecked(False)
                    self.setDragMode(QGraphicsView.RubberBandDrag)

        elif self.button2.isChecked():
            if event.button() == Qt.LeftButton:
                self.path2.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()

                # Draw circle at the end
                scene_pos = self.mapToScene(event.pos())
                circle = QGraphicsEllipseItem(scene_pos.x() - 3, scene_pos.y() - 3, 6, 6)
                circle.setZValue(2)
                circle.setPen(self.pen)

                self.canvas.update()

                # Load path as QGraphicsItem, set parent items
                path_item = QGraphicsPathItem(self.path2)
                path_item.setPen(self.pen)
                path_item.setZValue(2)
                circle.setParentItem(path_item)
                self.text.setParentItem(circle)
                self.rect.setParentItem(circle)

                # Add items
                self.canvas.addItem(path_item)

                # Set Flags
                path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                path_item.setFlag(QGraphicsItem.ItemIsMovable)
                circle.setFlag(QGraphicsItem.ItemIsSelectable)
                self.text.setFlag(QGraphicsItem.ItemIsSelectable)

                # Set Tooltips
                path_item.setToolTip('Leader Line Element')
                circle.setToolTip('Leader Line End Element')

                # Check if item is selected or moved so we can turn tool off
                if self.canvas.selectedItems():
                    self.button2.setChecked(False)
                    self.setDragMode(QGraphicsView.RubberBandDrag)

        super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event):
        # Handle trackpad zoom events
        if event.angleDelta().y() > 0:
            self.scale(1.1, 1.1)
        elif event.angleDelta().y() < 0:
            self.scale(0.9, 0.9)

        super().wheelEvent(event)

class MPRUN(QMainWindow):
    def __init__(self):
        super().__init__()
        # Creating the main window
        self.setWindowTitle('MPRUN - Workspace')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_icon.ico'))
        self.setGeometry(0, 0, 1500, 800)
        self.setAcceptDrops(True)

        # Drawing undoing, redoing
        self.last_drawing = []
        self.drawing_history = []

        # File
        self.file_name = None

        # Drawing strokes
        self.outline_color = item_stack()
        self.fill_color = item_stack()
        self.outline_color.set('black')
        self.fill_color.set('black')

        self.start_pos = None
        self.end_pos = None

        self.create_menu()
        self.create_toolbars()
        self.create_canvas()


    def create_menu(self):
        pass

    def create_toolbars(self):
        # Toolbar
        self.toolbar = QToolBar('MPRUN Toolset')
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setOrientation(Qt.Vertical)
        self.addToolBar(self.toolbar)

        # Action toolbar
        self.action_toolbar = QToolBar('MPRUN Action Bar')
        self.addToolBar(self.action_toolbar)

        #----action toolbar widgets----#

        # Stroke size spinbox
        self.stroke_size_spin = QSpinBox()
        self.stroke_size_spin.setValue(3)

        # Layer Combobox
        self.layer_options = {'Layer 0 (Default)': 0,'Layer 1 (Course Elements)': 1, 'Layer 2 (Lines/Paths)': 2, 'Layer 3 (Text/Labels)': 3}
        self.layer_combo = QComboBox()
        for layer, value in self.layer_options.items():
            self.layer_combo.addItem(layer, value)

        # Outline Color Button
        self.outline_color_btn = QPushButton('Stroke Color', self)
        self.outline_color_btn.setShortcut(QKeySequence('Ctrl+1'))
        self.outline_color_btn.clicked.connect(self.outline_color_chooser)
        self.outline_color_btn.clicked.connect(self.update_pen)

        # Course Elements Launcher Button
        course_elements_launcher_btn = QPushButton('Course Elements Picker', self)
        course_elements_launcher_btn.setShortcut(QKeySequence('Ctrl+2'))
        course_elements_launcher_btn.clicked.connect(self.launch_course_elements)

        # Stroke Style Combobox
        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine, 'Dotted Stroke': Qt.DotLine, 'Dashed Stroke': Qt.DashLine, 'Dashed Dot Stroke': Qt.DashDotLine, 'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox()
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)

        # Pen Cap Style Combobox
        self.stroke_pencap_options = {'Square Cap': Qt.SquareCap, 'Flat Cap': Qt.FlatCap, 'Round Cap': Qt.RoundCap}
        self.stroke_pencap_combo = QComboBox()
        for pencap, value in self.stroke_pencap_options.items():
            self.stroke_pencap_combo.addItem(pencap, value)

        # GSNAP Related widgets
        self.gsnap_label = QLabel('GSNAP Enabled:', self)
        self.gsnap_label.setStyleSheet("font-size: 10px;")
        self.gsnap_check_btn = QCheckBox(self)





        #----toolbar buttons----#

        #Image
        icon = QAction(QIcon('logos and icons/MPRUN_icon.png'), '', self)

        # Select Button
        select_btn = QAction('Select', self)
        select_btn.setToolTip('''Shortcut:
        Key-Spacebar''')
        select_btn.setShortcut(QKeySequence(Qt.Key_Space))
        select_btn.triggered.connect(self.use_select)

        # Pan Button
        pan_btn = QAction('Pan', self)
        pan_btn.setToolTip('''Shortcut:
        Key-P''')
        pan_btn.setShortcut(QKeySequence("P"))
        pan_btn.triggered.connect(self.use_pan)

        # Path draw button
        self.path_btn = QAction("Path", self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip('''Path Draw:
        1. Creates a line (path) wherever drawn.

Methods:
        - Draw the path or line taken on the course for your run.
        - Draw course features.
        - Draw anything!
                            
Shortcut:
        Key-L''')
        self.path_btn.setShortcut(QKeySequence('L'))
        self.path_btn.triggered.connect(self.path_btn.setChecked)  # Connect to method to toggle path drawing

        # Label draw button
        self.label_btn = QAction("Line and Label", self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip('''Line and Label:
                1. Creates a leader line (line) wherever drawn.
                2. Creates an Editable Text Element at the end of the line.

        Methods:
                - Label tricks along paths.
                - Label course elements.

        Shortcut:
                Key-A''')
        self.label_btn.setShortcut(QKeySequence('A'))
        self.label_btn.triggered.connect(self.label_btn.setChecked)  # Connect to method to toggle path drawing

        # Add Text Button
        add_text_btn = QAction('Text', self)
        add_text_btn.setToolTip('''Text Tool:
        1. Inserts an Editable Text Block on the canvas.
        2. Sets the text color to the chosen stroke color.
        
Methods:
        - Create labels for paths.
        - Add text to the scene for anything!
        
Shortcuts:
        Command+T (MacOS) or Control+T (Windows)''')
        add_text_btn.setShortcut(QKeySequence('Ctrl+T'))
        add_text_btn.triggered.connect(self.use_text)

        # Erase Button
        erase_btn = QAction('Erase', self)
        erase_btn.setToolTip('''Erase Tool:
                        1. Activates the Path Tool, and sets the color to white.

                Methods:
                        - Draw white strokes to erase items.
                        - Draw white strokes to add detail to items.

                Shortcut:
                        Key-E''')
        erase_btn.setShortcut(QKeySequence('E'))
        erase_btn.triggered.connect(self.use_erase)

        # Set Layer Button
        layer_set_btn = QAction('Set Layer', self)
        layer_set_btn.setToolTip('''Set Layer:
        1. Sets the selected item to the chosen layer.
        
Methods:
        - Set layers for various objects to keep items in order
        - Create custom course elements by setting layers for various geometric items.
        
Shortcuts:
        Command+L (MacOS) or Control+L (Windows)''')
        layer_set_btn.setShortcut(QKeySequence('Ctrl+L'))
        layer_set_btn.triggered.connect(self.set_layer)

        # Rotate Manager Button
        rotate_btn = QAction('Rotate', self)
        rotate_btn.setToolTip('''Rotate Manager:
        1. Launches the Rotate Manager.
        2. Rotates selected items to the input amount.
        
Methods:
        - Rotate items to create accurate course setups
        - Rotate labels to fit text to odd angles.
        
Shortcuts:
        Command+3 (MacOS) or Control+3 (Windows), or Key-R''')
        rotate_btn.setShortcut(QKeySequence('Ctrl+3'))
        rotate_btn.triggered.connect(self.show_rotate_manager)

        # Scale Manager Button
        scale_btn = QAction('Scale', self)
        scale_btn.setToolTip('''Scale Manager:
                1. Launches the Scale Manager.
                2. Scales selected items to the input amount.

        Methods:
                - Scale course elements to desired sizes.
                - Scale anything!

        Shortcuts:
                Command+4 (MacOS) or Control+4 (Windows), or Key-S''')
        scale_btn.setShortcut(QKeySequence('Ctrl+4'))
        scale_btn.triggered.connect(self.show_scale_manager)

        # Lock Item Button
        lock_btn = QAction('Lock Item', self)
        lock_btn.setToolTip('''Lock Item:
        1. Locks the item position and removes moving functionality from the item attributes.
    	
Methods:
        - Lock items to maintain their position during the course creation process.
        
Shortcuts: 
        Command+X (MacOS) or Control+X (Windows)''')
        lock_btn.setShortcut(QKeySequence('Ctrl+X'))
        lock_btn.triggered.connect(self.lock_item)

        # Unlock Item Button
        unlock_btn = QAction('Unlock Item', self)
        unlock_btn.setToolTip('''Unlock Item:
        1. Unlocks the item position and adds moving functionality to the item attributes.
		
Methods:
        - Unlock previously locked items.

Shortcuts: 
        Command+B (MacOS) or Control+B (Windows)''')
        unlock_btn.setShortcut(QKeySequence('Ctrl+B'))
        unlock_btn.triggered.connect(self.unlock_item)

        # Create Group Button
        group_create_btn = QAction('Group Create', self)
        group_create_btn.setToolTip('''Group Create:
        1. Combines all selected items in to one group.
        2. Turns the group into one draggable and selectable item.
        3. Allows you to enable Group Snapping (GSNAP) to move the item at a grid based level.
        
Methods:
        - Create course elements by grouping various geometric items.
        - Group paths/lines, or any vector shapes to create anything!
        
Shortcut: 
        Key-G''')
        group_create_btn.setShortcut(QKeySequence('G'))
        group_create_btn.triggered.connect(self.create_group)

        # Insert Button
        insert_btn = QAction('Insert', self)
        insert_btn.setToolTip('''Insert Tool:
        1. Inserts a selected image file onto the canvas.

Methods: 
        - Insert images for course elements.
        - Insert custom logos, designs, or anything else to decorate before export.
        
Shortcut:
        Key-I''')
        insert_btn.setShortcut(QKeySequence('I'))
        insert_btn.triggered.connect(self.insert_image)

        # Export Button
        export_btn = QAction('Export', self)
        export_btn.setToolTip('''Export Tool:
        1. Asks for a file name and file type.
        2. Exports the scene as the file name and type.
        
Shortcuts:
        Command+E (MacOS) or Control+E (Windows)''')
        export_btn.setShortcut(QKeySequence('Ctrl+E'))
        export_btn.triggered.connect(self.export)

        # Add toolbar actions
        self.toolbar.addAction(icon)
        self.toolbar.addSeparator()
        self.toolbar.addAction(select_btn)
        self.toolbar.addAction(pan_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.path_btn)
        self.toolbar.addAction(erase_btn)
        self.toolbar.addAction(self.label_btn)
        self.toolbar.addAction(add_text_btn)
        self.toolbar.addAction(layer_set_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(rotate_btn)
        self.toolbar.addAction(scale_btn)
        self.toolbar.addAction(lock_btn)
        self.toolbar.addAction(unlock_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(group_create_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(insert_btn)
        self.toolbar.addAction(export_btn)
        self.toolbar.addSeparator()

        # Add action toolbar actions
        self.action_toolbar.addSeparator()
        self.action_toolbar.addWidget(self.layer_combo)
        self.action_toolbar.addWidget(self.gsnap_label)
        self.action_toolbar.addWidget(self.gsnap_check_btn)
        self.action_toolbar.addSeparator()
        self.action_toolbar.addWidget(self.stroke_size_spin)
        self.action_toolbar.addWidget(self.outline_color_btn)
        self.action_toolbar.addWidget(self.stroke_style_combo)
        self.action_toolbar.addWidget(self.stroke_pencap_combo)
        self.action_toolbar.addSeparator()
        self.action_toolbar.addWidget(course_elements_launcher_btn)
        self.action_toolbar.addSeparator()

    def create_canvas(self):
        # Canvas, canvas color
        self.canvas = QGraphicsScene()
        self.canvas.setSceneRect(0, 0, 1000, 700)
        brush1 = QBrush(QColor('#545454'))
        self.canvas.setBackgroundBrush(brush1)

        # QGraphicsView Logic, set the main widget
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        self.canvas_view = CustomGraphicsView(self.canvas, self.path_btn, self.label_btn)

        self.canvas_view.update_pen(QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))

        self.stroke_size_spin.valueChanged.connect(lambda: self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)))
        self.stroke_style_combo.currentIndexChanged.connect(lambda: self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)))
        self.stroke_pencap_combo.currentIndexChanged.connect(lambda: self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2)))

        if self.path_btn.isChecked():
            self.canvas_view.update_pen(
                QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))

        self.canvas_view.setScene(self.canvas)
        self.canvas_view.setRenderHint(QPainter.Antialiasing)
        self.use_select()
        self.setCentralWidget(self.canvas_view)

        # Drawing paper
        self.paper = QGraphicsRectItem(0, 0, 1000, 700)
        brush = QBrush(QColor('white'))
        pen = QPen(QColor('black'), 2, Qt.SolidLine)
        self.paper.setBrush(brush)
        self.paper.setPen(pen)
        self.paper.setZValue(-1)
        self.canvas.addItem(self.paper)

        # Text on paper
        self.paper_text = EditableTextBlock("""Run #:   
Page #:   
Competition:    
Athlete:    
Date:   """)
        self.paper_text.setPos(2, 2)
        self.paper_text.setDefaultTextColor(QColor('black'))
        self.paper_text.setFont(QFont("Helvetica", 9))
        self.paper_text.setFlag(QGraphicsItem.ItemIsSelectable)
        self.paper_text.setZValue(-1)
        self.paper_text.setToolTip(f"Locked Text Block (This item's position is locked)")
        self.canvas.addItem(self.paper_text)

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

            self.use_select()

        elif event.key() == QKeySequence('Z'):
            self.gsnap_check_btn.setChecked(False) if self.gsnap_check_btn.isChecked() else self.gsnap_check_btn.setChecked(True)

        elif event.key() == QKeySequence('R'):
            self.show_rotate_manager()

        elif event.key() == QKeySequence('S'):
            self.show_scale_manager()

        elif event.key() == QKeySequence('B'):
            self.outline_color_chooser()

        super().keyPressEvent(event)

    def closeEvent(self, event):
        # Display a confirmation dialog
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Warning)
        confirmation_dialog.setText("Are you sure you want to close the open project? (This will destroy all progress)")
        confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation_dialog.setDefaultButton(QMessageBox.No)

        # Get the result of the confirmation dialog
        result = confirmation_dialog.exec_()

        # If the user clicked Yes, close the window
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def update_pen(self):
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        self.canvas_view.update_pen(
            QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))

    def outline_color_chooser(self):
        self.outline_color_dialog = QColorDialog(self)
        self.outline_color.set(self.outline_color_dialog.getColor())

    def launch_course_elements(self):
        self.course_elements = CourseElementsWin(self.canvas)
        self.course_elements.show()

    def show_rotate_manager(self):
        self.rotate_manger = RotateManager(self.canvas)
        self.rotate_manger.show()

    def show_scale_manager(self):
        self.scale_manager = ScaleManager(self.canvas)
        self.scale_manager.show()

    def use_select(self):
        self.canvas_view.setDragMode(QGraphicsView.RubberBandDrag)

    def use_pan(self):
        self.canvas_view.setDragMode(QGraphicsView.ScrollHandDrag)

    def use_erase(self):
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)

        self.canvas_view.update_pen(QPen(QColor('white'), self.stroke_size_spin.value(), data1, data2))
        self.path_btn.setChecked(True)

    def use_text(self):
        text = EditableTextBlock('An Editable Text Block')
        text.setDefaultTextColor(QColor(self.outline_color.get()))

        self.canvas.addItem(text)

        text.setPos(200, 200)

        self.create_item_attributes(text)

    def set_layer(self):
        index = self.layer_combo.currentIndex()
        data = self.layer_combo.itemData(index)
        item = self.canvas.selectedItems()
        for items in item:
            z = items.zValue()
            items.setZValue(data)

    def lock_item(self):
        item = self.canvas.selectedItems()

        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable, False)
            items.setToolTip('Locked MPRUN Element')

    def unlock_item(self):
        item = self.canvas.selectedItems()
        for items in item:
            items.setFlag(QGraphicsItem.ItemIsMovable)
            items.setToolTip('Free MPRUN Element')

    def insert_image(self):
        # Create Options
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # File Dialog, file path
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("SVG files (*.svg);;JPG files (*.jpg);;JPEG files (*.jpeg);;PNG files (*.png);;Bitmap files (*.bmp)")

        file_path, _ = file_dialog.getOpenFileName(self, "Insert Element", "", "SVG files (*.svg);;JPG files (*.jpg);;JPEG files (*.jpeg);;PNG files (*.png);;BMP files (*.bmp)",
                                                   options=options)

        if file_path:
            if file_path.endswith('.svg'):
                svg_item = QGraphicsSvgItem(file_path)
                self.canvas.addItem(svg_item)
                svg_item.setPos(450, 300)
                svg_item.setToolTip('Imported SVG Item (Not an MPRUN Element)')

                self.create_item_attributes(svg_item)

            else:
                image1 = QPixmap(file_path)
                image2 = QGraphicsPixmapItem(image1)

                self.canvas.addItem(image2)
                image2.setToolTip('Imported Bitmap Item (Not an MPRUN Element)')

                self.create_item_attributes(image2)


    def export_canvas(self, filename):
        # Create a QImage with the size of the scene
        image = QImage(self.canvas.sceneRect().size().toSize(), QImage.Format_ARGB32)

        # Fill the image with transparent background
        image.fill(0)

        # Render the scene onto the image
        painter = QPainter(image)
        self.canvas.render(painter)
        painter.end()

        # Save the image to file
        image.save(filename)

    def export(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # File dialog, filepath
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix('.png')

        file_path, selected_filter = file_dialog.getSaveFileName(self, 'Export Canvas', '',
                                                                 'PNG files (*.png);;JPEG files (*.jpeg);;TIFF files (*.tiff);;PDF files (*.pdf);;SVG files (*.svg)',
                                                                 options=options)

        if file_path:
            # Get the selected filter's extension
            filter_extensions = {
                'PNG files (*.png)': '.png',
                'JPEG files (*.jpeg)': '.jpeg',
                'TIFF files (*.tiff)': '.tiff',
                'PDF files (*.pdf)': '.pdf',
                'SVG files (*.svg)': '.svg'
            }
            selected_extension = filter_extensions.get(selected_filter, '.png')

            # Ensure the file_path has the selected extension
            if not file_path.endswith(selected_extension):
                file_path += selected_extension

            if selected_extension == '.svg':
                # Export as SVG
                svg_generator = QSvgGenerator()
                svg_generator.setFileName(file_path)
                svg_generator.setSize(self.canvas.sceneRect().size().toSize())
                svg_generator.setViewBox(self.canvas.sceneRect())

                # Clear selection
                self.canvas.clearSelection()

                # Create a QPainter to paint onto the QSvgGenerator
                painter = QPainter()
                painter.begin(svg_generator)

                # Render the scene onto the QPainter
                self.canvas.render(painter)

                # End painting
                painter.end()

            elif selected_extension == '.pdf':
                # Export as PDF
                printer = QPdfWriter(file_path)
                printer.setPageSize(QPdfWriter.A4)
                printer.setResolution(300)  # Set the resolution (in DPI)

                # Clear selection
                self.canvas.clearSelection()

                # Create painter, save file
                painter = QPainter(printer)
                self.canvas.render(painter)
                painter.end()

            else:
                self.canvas.clearSelection()
                self.export_canvas(file_path)


    def create_group(self):
        item = self.canvas.selectedItems()
        self.group = CustomGraphicsItemGroup(self.gsnap_check_btn)

        # Set flags for group
        self.group.setFlag(QGraphicsItem.ItemIsMovable)
        self.group.setFlag(QGraphicsItem.ItemIsSelectable)

        # Add group
        self.canvas.addItem(self.group)
        self.canvas.update()

        for items in item:
            # Clear Selection
            self.canvas.clearSelection()

            # Set flag
            items.setFlag(QGraphicsItem.ItemIsSelectable, False)

            # Check if the item is an instance
            if isinstance(items, QGraphicsTextItem):
                items.setTextInteractionFlags(Qt.NoTextInteraction)

                # Set an object name
                items.setToolTip(f"Grouped Text Block (This item's text is not editable)")

            elif isinstance(items, CustomGraphicsItemGroup):
                self.group.setToolTip('Grouped Object (Free MPRUN Element)')
                
            elif isinstance(items, EditableTextBlock):
                items.setTextInteractionFlags(Qt.NoTextInteraction)

                # Set an object name
                items.setToolTip(f"Grouped Text Block (This item's text is not editable)")


            # Add items to group
            self.group.addToGroup(items)

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        index = self.layer_combo.currentIndex()
        data = self.layer_combo.itemData(index)
        item.setZValue(data)

    def set_template(self, template_choice):
        if template_choice == 1:
            pass

        elif template_choice == 2:
            self.canvas_view.setSceneRect(0, 0, 828, 621)
            self.canvas.setSceneRect(0, 0, 828, 621)
            self.paper.setRect(0, 0, 828, 621)

        elif template_choice == 3:
            self.canvas_view.setSceneRect(0, 0, 1725, 1293)
            self.canvas.setSceneRect(0, 0, 1725, 1293)
            self.paper.setRect(0, 0, 1725, 1293)
            self.paper_text.setScale(2.5)

        elif template_choice == 4:
            self.canvas_view.setSceneRect(0, 0, 1080, 1920)
            self.canvas.setSceneRect(0, 0, 1080, 1920)
            self.paper.setRect(0, 0, 1080, 1920)
            self.paper_text.setScale(2.5)

        elif template_choice == 5:
            self.canvas_view.setSceneRect(0, 0, 591, 399)
            self.canvas.setSceneRect(0, 0, 591, 399)
            self.paper.setRect(0, 0, 591, 399)
            self.paper_text.setScale(1)

        elif template_choice == 6:
            self.canvas_view.setSceneRect(0, 0, 1847, 1247)
            self.canvas.setSceneRect(0, 0, 1847, 1247)
            self.paper.setRect(0, 0, 1847, 1247)
            self.paper_text.setScale(2.5)

        elif template_choice == 7:
            self.canvas_view.setSceneRect(0, 0, 1366, 1024)
            self.canvas.setSceneRect(0, 0, 1366, 1024)
            self.paper.setRect(0, 0, 1366, 1024)
            self.paper_text.setScale(2)

        else:
            pass

    def custom_template(self, x, y, default_text):
        self.canvas_view.setSceneRect(0, 0, x, y)
        self.canvas.setSceneRect(0, 0, x, y)
        self.paper.setRect(0, 0, x, y)
        self.paper_text.setPlainText(default_text)

class CourseElementsWin(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas

        self.setWindowTitle('Course Elements Picker')
        self.setGeometry(50, 100, 300, 250)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.create_ui()

    def create_ui(self):
        # Create a layout
        self.layout = QVBoxLayout()

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Create a widget to hold the layout
        widget = QWidget()
        widget.setLayout(self.layout)

        # Set the widget as the scroll area's widget
        scroll_area.setWidget(widget)

        # Set the layout of the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        self.create_buttons()

    def create_buttons(self):
        # Course Element Spawn Buttons
        btn1 = QPushButton()
        btn1.setText('Rail 1 (Long Tube)')
        btn1.clicked.connect(lambda: self.create_img('Course Element/rail 1 (long tube).svg'))

        btn2 = QPushButton()
        btn2.setText('Rail 1 (Short Tube)')
        btn2.clicked.connect(lambda: self.create_img('Course Element/rail 1 (short tube).svg'))

        btn3 = QPushButton()
        btn3.setText('Jump 1 (Small)')
        btn3.clicked.connect(lambda: self.create_img('Course Element/jump 1 (small).svg'))

        btn4 = QPushButton()
        btn4.setText('Jump 1 (Medium)')
        btn4.clicked.connect(lambda: self.create_img('Course Element/jump 1 (medium).svg'))

        btn5 = QPushButton()
        btn5.setText('Jump 1 (Large)')
        btn5.clicked.connect(lambda: self.create_img('Course Element/jump 1 (large).svg'))

        btn6 = QPushButton()
        btn6.setText("Halfpipe 1 (22')")
        btn6.clicked.connect(lambda: self.create_img("Course Element/halfpipe 1 (22').svg"))

        # Other Buttons
        import_btn = QPushButton()
        import_btn.setText('Import Course Element...')
        import_btn.clicked.connect(self.import_course_element)

        # Labels
        rail_label = QLabel('Rails:')
        jump_label = QLabel('Jumps:')
        halfpipe_label = QLabel('Half/Quarter Pipes:')
        import_label = QLabel('Imported Course Elements:')

        # Add buttons to layout
        self.layout.addWidget(rail_label)
        self.layout.addWidget(btn1)
        self.layout.addWidget(btn2)
        self.layout.addWidget(jump_label)
        self.layout.addWidget(btn3)
        self.layout.addWidget(btn4)
        self.layout.addWidget(btn5)
        self.layout.addWidget(halfpipe_label)
        self.layout.addWidget(btn6)
        self.layout.addWidget(import_label)
        self.layout.addWidget(import_btn)

    def create_img(self, svg_file):
        svg_item = QGraphicsSvgItem(svg_file)
        self.canvas.addItem(svg_item)
        svg_item.setPos(450, 300)
        svg_item.setToolTip('MPRUN Course Element')

        self.create_image_attributes(svg_item)

    def import_course_element(self):
        # Create Options
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # File Dialog, file path
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("SVG files (*.svg)")

        file_path, _ = file_dialog.getOpenFileName(self, "Import Course Element", "", "SVG Files (*.svg)",
                                                   options=options)

        if file_path:
            # Get name for button
            entry, ok = QInputDialog.getText(self, 'Import Course Element', 'Enter a name for the imported element:')
            if ok:
                # Add element
                btn = QPushButton()
                btn.setText(entry)
                btn.clicked.connect(lambda: self.create_item(QGraphicsSvgItem(file_path)))
                self.layout.addWidget(btn)

    def create_item(self, item):
        self.canvas.addItem(item)
        item.setToolTip('Imported SVG Item (Not an MPRUN Element)')
        self.create_image_attributes(item)

    def create_image_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setPos(450, 300)
        item.setZValue(1)

    def closeEvent(self, event):
        # Display a confirmation dialog
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Warning)
        confirmation_dialog.setText("Are you sure you want to close the Course Elements Picker? (This will delete imported Course Element spawn buttons)")
        confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation_dialog.setDefaultButton(QMessageBox.No)

        # Get the result of the confirmation dialog
        result = confirmation_dialog.exec_()

        # If the user clicked Yes, close the window
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
class RotateManager(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas

        self.setWindowTitle('Rotate Manager')
        self.setGeometry(50, 373, 300, 50)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
        self.spinbox = QSpinBox()
        self.spinbox.setMaximum(360)
        self.spinbox.valueChanged.connect(self.rotate)

        self.layout.addWidget(self.spinbox)

    def rotate(self, value):
        items = self.canvas.selectedItems()
        for item in items:
            item.setRotation(value)
class ScaleManager(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas

        self.setWindowTitle('Scale Manager')
        self.setGeometry(50, 456, 300, 50)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
        self.entry1 = QLineEdit()
        self.entry1.textChanged.connect(self.scale_all)
        self.entry1.setPlaceholderText("Enter overall scale factor")

        self.entry2 = QLineEdit()
        self.entry2.textChanged.connect(self.scale_x)
        self.entry2.setPlaceholderText("Enter horizontal scale factor")

        self.entry3 = QLineEdit()
        self.entry3.textChanged.connect(self.scale_y)
        self.entry3.setPlaceholderText("Enter vertical scale factor")

        self.layout.addWidget(self.entry1)
        self.layout.addWidget(self.entry2)
        self.layout.addWidget(self.entry3)


    def scale_all(self, value):
        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                item.setScale(value)
        except ValueError:
            pass

    def scale_x(self, value):
        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                transform = QTransform()
                transform.scale(value, 1.0)
                item.setTransform(transform)
        except ValueError:
            pass

    def scale_y(self, value):
        try:
            value = float(value)
            items = self.canvas.selectedItems()
            for item in items:
                transform = QTransform()
                transform.scale(1.0, value)
                item.setTransform(transform)
        except ValueError:
            pass



if __name__ == '__main__':
    app = QApplication([])
    window = MPRUN()
    window.show()
    app.exec_()
