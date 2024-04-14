import sys
import math
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

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

        # Drawing stroke methods
        self.outline_color = item_stack()
        self.fill_color = item_stack()
        self.outline_color.set('black')
        self.fill_color.set('black')

        # Grid Size and rotating screens
        self.gsnap_grid_size = 10
        self.screen_rotate_size = 0

        # Create GUI
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
        pan_btn = QAction('Pan', self)
        pan_btn.setToolTip('''Pan Tool:
        Key-P''')
        pan_btn.setShortcut(QKeySequence("P"))
        pan_btn.triggered.connect(self.use_pan)

        # Path draw button
        self.path_btn = QAction("Path", self)
        self.path_btn.setCheckable(True)
        self.path_btn.setToolTip('''Path Draw Tool:
        Key-L''')
        self.path_btn.setShortcut(QKeySequence('L'))
        self.path_btn.triggered.connect(self.path_btn.setChecked)  # Connect to method to toggle path drawing

        # Label draw button
        self.label_btn = QAction("Line and Label", self)
        self.label_btn.setCheckable(True)
        self.label_btn.setToolTip('''Line and Label Tool:
        Key-T''')
        self.label_btn.setShortcut(QKeySequence('T'))
        self.label_btn.triggered.connect(self.label_btn.setChecked)  # Connect to method to toggle path drawing

        # Add Text Button
        add_text_btn = QAction('Text', self)
        add_text_btn.setToolTip('''Text Tool:
        Command+T (MacOS) or Control+T (Windows)''')
        add_text_btn.setShortcut(QKeySequence('Ctrl+T'))
        add_text_btn.triggered.connect(self.use_text)

        # Erase Button
        erase_btn = QAction('Erase', self)
        erase_btn.setToolTip('''Erase Tool:
        Key-E''')
        erase_btn.setShortcut(QKeySequence('E'))
        erase_btn.triggered.connect(self.use_erase)

        # Set Layer Button
        layer_set_btn = QAction('Set Layer', self)
        layer_set_btn.setToolTip('''Set Layer Tool:
        Command+L (MacOS) or Control+L (Windows)''')
        layer_set_btn.setShortcut(QKeySequence('Ctrl+L'))
        layer_set_btn.triggered.connect(self.set_layer)

        # Rotate Manager Button
        rotate_btn = QAction('Rotate', self)
        rotate_btn.setToolTip('''Rotate Tool:
        Command+3 (MacOS) or Control+3 (Windows), or Key-R''')
        rotate_btn.setShortcut(QKeySequence('Ctrl+3'))
        rotate_btn.triggered.connect(self.show_rotate_manager)

        # Scale Manager Button
        scale_btn = QAction('Scale', self)
        scale_btn.setToolTip('''Scale Tool:
        Command+4 (MacOS) or Control+4 (Windows), or Key-S''')
        scale_btn.setShortcut(QKeySequence('Ctrl+4'))
        scale_btn.triggered.connect(self.show_scale_manager)

        # Lock Item Button
        lock_btn = QAction('Lock Item', self)
        lock_btn.setToolTip('''Lock Position Tool: 
        Command+X (MacOS) or Control+X (Windows)''')
        lock_btn.setShortcut(QKeySequence('Ctrl+X'))
        lock_btn.triggered.connect(self.lock_item)

        # Unlock Item Button
        unlock_btn = QAction('Unlock Item', self)
        unlock_btn.setToolTip('''Unlock Position Tool: 
        Command+B (MacOS) or Control+B (Windows)''')
        unlock_btn.setShortcut(QKeySequence('Ctrl+B'))
        unlock_btn.triggered.connect(self.unlock_item)

        # Create Group Button
        group_create_btn = QAction('Group Create', self)
        group_create_btn.setToolTip('''Group Create Tool: 
        Key-G''')
        group_create_btn.setShortcut(QKeySequence('G'))
        group_create_btn.triggered.connect(self.create_group)

        # Insert Button
        insert_btn = QAction('Insert', self)
        insert_btn.setToolTip('''Insert Tool:
        Key-I''')
        insert_btn.setShortcut(QKeySequence('I'))
        insert_btn.triggered.connect(self.insert_image)

        # Export Button
        export_btn = QAction('Export', self)
        export_btn.setToolTip('''Export Tool:
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
        width = 64000
        height = 64000
        self.canvas.setSceneRect(-width//2, -height//2, width, height)
        brush1 = QBrush(QColor('#545454'))
        self.canvas.setBackgroundBrush(brush1)

        # QGraphicsView Logic, set the main widget
        index1 = self.stroke_style_combo.currentIndex()
        data1 = self.stroke_style_combo.itemData(index1)
        index2 = self.stroke_pencap_combo.currentIndex()
        data2 = self.stroke_pencap_combo.itemData(index2)
        
        # Set flags for view
        self.canvas_view = CustomGraphicsView(self.canvas, self.path_btn, self.label_btn)
        self.canvas_view.setRenderHint(QPainter.Antialiasing)
        self.canvas_view.setRenderHint(QPainter.TextAntialiasing)
        self.canvas_view.update_pen(QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))

        self.stroke_size_spin.valueChanged.connect(self.update_pen)
        self.stroke_style_combo.currentIndexChanged.connect(self.update_pen)
        self.stroke_pencap_combo.currentIndexChanged.connect(self.update_pen)

        if self.path_btn.isChecked():
            self.canvas_view.update_pen(
                QPen(QColor(self.outline_color.get()), self.stroke_size_spin.value(), data1, data2))

        self.canvas_view.setScene(self.canvas)
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

        # Create initial group
        self.group = CustomGraphicsItemGroup(self.gsnap_check_btn)

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
        confirmation_dialog.setText("Are you sure you want to close the open project? (This will destroy any progress)")
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

    def use_rotate_screen(self):
        self.screen_rotate_size += 90
        transform = QTransform()
        transform.rotate(self.screen_rotate_size)

        self.canvas_view.setTransform(transform)

    def set_layer(self):
        index = self.layer_combo.currentIndex()
        data = self.layer_combo.itemData(index)
        item = self.canvas.selectedItems()
        for items in item:
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
        # Create a QImage with the size of the QGraphicsRectItem
        rect = self.paper.boundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        # Fill the image with transparent background
        image.fill(Qt.transparent)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        # Save the image to file
        success = image.save(filename)

        if success:
            # If saving was successful, show a notification
            QMessageBox.information(self, "Export Finished", "Export completed successfully.")
        else:
            # If saving failed, show an error notification
            QMessageBox.critical(self, "Export Error", "Failed to export canvas to file.")

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
                svg_generator.setSize(self.paper.boundingRect().size().toSize())
                svg_generator.setViewBox(self.paper.boundingRect())

                # Clear selection
                self.canvas.clearSelection()

                # Create a QPainter to paint onto the QSvgGenerator
                painter = QPainter()
                painter.begin(svg_generator)

                # Render the scene onto the QPainter
                self.canvas.render(painter)

                # End painting
                painter.end()

                # Show export finished notification
                QMessageBox.information(self, 'Export Finished', 'Export completed successfully.',
                                        QMessageBox.Ok)

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

                # Show export finished notification
                QMessageBox.information(self, 'Export Finished', 'Export completed successfully.',
                                        QMessageBox.Ok)

            else:
                self.canvas.clearSelection()
                self.export_canvas(file_path)


    def create_group(self):
        if self.group is not None:
            self.group = CustomGraphicsItemGroup(self.gsnap_check_btn)
            self.group.set_grid_size(self.gsnap_grid_size)

            item = self.canvas.selectedItems()

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
            self.paper.setRect(-100, -100, 728, 521)
            self.paper_text.setPos(-98, -98)

        elif template_choice == 3:
            self.paper.setRect(-100, -100, 1625, 1193)
            self.paper_text.setScale(2.5)
            self.paper_text.setPos(-98, -98)

        elif template_choice == 4:
            self.paper.setRect(-100, -100, 980, 1820)
            self.paper_text.setScale(2.5)
            self.paper_text.setPos(-98, -98)

        elif template_choice == 5:
            self.paper.setRect(-100, -100, 491, 299)
            self.paper_text.setScale(1)
            self.paper_text.setPos(-98, -98)

        elif template_choice == 6:
            self.paper.setRect(-100, -100, 1747, 1147)
            self.paper_text.setScale(2.5)
            self.paper_text.setPos(-98, -98)

        elif template_choice == 7:
            self.paper.setRect(-100, -100, 1266, 924)
            self.paper_text.setScale(2)
            self.paper_text.setPos(-98, -98)
            
        elif template_choice == 8:
            self.paper.setRect(-100, -100, 1820, 980)
            self.paper_text.setScale(2.5)
            self.paper_text.setPos(-98, -98)

        else:
            pass

    def custom_template(self, x, y, default_text, grid_size):
        self.group.set_grid_size(grid_size)
        self.gsnap_grid_size = grid_size
        self.paper.setRect(-100, -100, x-100, y-100)
        self.paper_text.setPlainText(default_text)
        self.paper_text.setPos(-98, -98)

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

        btn7 = QPushButton()
        btn7.setText("Rail 2 (Skinny)")
        btn7.clicked.connect(lambda: self.create_img("Course Element/rail 2 (skinny).svg"))

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
        self.layout.addWidget(btn7)
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
            # Calculate the center point of the item
            center = item.boundingRect().center()

            # Set the transformation origin to the center point
            item.setTransformOriginPoint(center)

            # Rotate the item
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
                # Calculate the center point of the item
                center = item.boundingRect().center()

                # Set the transformation origin to the center point
                item.setTransformOriginPoint(center)

                item.setScale(value)
        except ValueError:
            pass

    def scale_x(self, value):
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

    def scale_y(self, value):
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



if __name__ == '__main__':
    app = QApplication([])
    window = MPRUN()
    window.show()
    app.exec_()
