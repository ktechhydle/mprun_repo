from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

class AddCanvasDialog(QWidget):
    def __init__(self, canvas, og_rect):
        super().__init__()

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.canvas = canvas
        self.paper = og_rect

        self.setWindowTitle('Add Canvas')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(300)

        self.create_ui()
    def create_ui(self):
        layout = QVBoxLayout()

        button_layout = QVBoxLayout()

        self.canvas_preset_dropdown = QComboBox(self)
        self.canvas_preset_dropdown.setFixedWidth(200)
        self.canvas_presets = {
            'MPRUN Standard (1000 x 700)': 1,
            'Web (1920 x 1080)': 2,
            'Letter (797 x 612)': 3,
            'Legal (1008 x 612)': 4,
            'A4 (595 x 842)': 5,
            'A6 (828 x 1169)': 6,
            'Phone (1080 x 1920)': 7,
            'Custom': 'c',

        }
        for canvas, key in self.canvas_presets.items():
            self.canvas_preset_dropdown.addItem(canvas, key)
        self.canvas_preset_dropdown.setCurrentText('Custom')
        self.canvas_preset_dropdown.setFixedWidth(275)
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.choose_canvas)

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width (in px)")

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height (in px)")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Canvas Name")

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_canvas)

        # Add widgets, set layout
        button_layout.addWidget(self.canvas_preset_dropdown)
        button_layout.addWidget(self.width_input)
        button_layout.addWidget(self.height_input)
        button_layout.addWidget(self.name_input)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def choose_canvas(self):
        choice = self.canvas_preset_dropdown.itemData(self.canvas_preset_dropdown.currentIndex())

        if choice == 'c':
            pass

        elif choice == 1:
            self.width_input.setText('1000')
            self.height_input.setText('700')

        elif choice == 2:
            self.width_input.setText('1920')
            self.height_input.setText('1080')

        elif choice == 3:
            self.width_input.setText('792')
            self.height_input.setText('612')

        elif choice == 4:
            self.width_input.setText('1008')
            self.height_input.setText('792')

        elif choice == 5:
            self.width_input.setText('595')
            self.height_input.setText('842')

        elif choice == 6:
            self.width_input.setText('828')
            self.height_input.setText('1169')

        elif choice == 7:
            self.width_input.setText('1080')
            self.height_input.setText('1920')

    def create_canvas(self):
        try:
            width = float(self.width_input.text())
            height = float(self.height_input.text())
            canvas_name = self.name_input.text()
            if width <= 0 or height <= 0:
                QMessageBox.critical(self, 'Size Error', 'Please enter positive number values for width and height.')

            elif width > 5000 or height > 5000:
                QMessageBox.critical(self, 'Size Error',
                                     'Please enter a width or height no larger than 5000px.')

            if canvas_name == '':
                QMessageBox.critical(self, 'Name Error',
                                     'Please enter a name for the canvas.')

            else:
                self.rect_item = CanvasItem(0, 0, width, height)
                text_item = EditableTextBlock(canvas_name)

                command = AddItemCommand(self.canvas, self.rect_item)
                self.canvas.addCommand(command)

                self.rect_item.setZValue(-1)
                self.rect_item.setPos(self.paper.sceneBoundingRect().width() + 10, 0)
                self.rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                self.rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.rect_item.setToolTip(canvas_name)

                text_item.setZValue(-1)
                text_item.setParentItem(self.rect_item)
                text_item.setDefaultTextColor(QColor('black'))
                text_item.setScale(1.5)
                text_item.setPos(self.rect_item.boundingRect().x(), self.rect_item.boundingRect().y() - 30)
                text_item.set_locked()

        except ValueError as e:
            QMessageBox.critical(self, 'Incorrect Value', 'Please enter a correct value in width and height entries.')

class CanvasItemSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Canvas To Export")
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        self.comboBox = QComboBox()
        layout.addWidget(self.comboBox)

        self.exportButton = QPushButton("Export")
        layout.addWidget(self.exportButton)

    def add_canvas_item(self, itemName, itemKey):
        if isinstance(itemKey, CanvasItem):
            values = {itemName: itemKey}
            for name, key in values.items():
                self.comboBox.addItem(name, key)

        else:
            pass



