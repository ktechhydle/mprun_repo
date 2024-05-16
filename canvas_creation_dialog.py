from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

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



