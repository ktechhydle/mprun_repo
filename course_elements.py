from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

class CourseElementsWin(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas

        self.setWindowTitle('Course Elements Picker')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
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
        svg_item = CustomSvgItem(svg_file)
        svg_item.store_filename(svg_file)
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
                btn.clicked.connect(lambda: self.create_item(CustomSvgItem(file_path)))
                self.layout.addWidget(btn)

    def create_item(self, item):
        self.canvas.addItem(item)
        item.setToolTip('Imported SVG Item (Not an MPRUN Element)')
        self.create_image_attributes(item)

    def create_image_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setZValue(0)

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