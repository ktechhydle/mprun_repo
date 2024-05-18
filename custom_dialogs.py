from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from custom_widgets import *
from undo_commands import *

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

class TextAlongPathPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.canvas = canvas

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(200)

        self.createUi()

    def createUi(self):
        main_label = QLabel('Text Along Path')
        main_label.setStyleSheet("QLabel { font-size: 12px; }")
        spacing_label = QLabel('Spacing From Path:')
        spacing_label.setStyleSheet("QLabel { font-size: 12px; }")

        self.text_along_path_check_btn = QCheckBox(self)
        self.text_along_path_check_btn.setText('Add Text Along Path')

        self.spacing_spin = QSpinBox(self)
        self.spacing_spin.setRange(-1000, 10000)
        self.spacing_spin.setSuffix(' pt')

        self.text_entry = QLineEdit(self)
        self.text_entry.setPlaceholderText('Enter Text')

        self.layout.addWidget(HorizontalSeparator())
        self.layout.addWidget(main_label)
        self.layout.addWidget(self.text_along_path_check_btn)
        self.layout.addWidget(spacing_label)
        self.layout.addWidget(self.spacing_spin)
        self.layout.addWidget(self.text_entry)

        self.text_along_path_check_btn.clicked.connect(self.update_path)
        self.spacing_spin.valueChanged.connect(self.update_path)
        self.text_entry.textChanged.connect(self.update_path)

    def update_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                if self.text_along_path_check_btn.isChecked():
                    command = AddTextToPathCommand(item, self.text_along_path_check_btn, False, True)
                    self.canvas.addCommand(command)
                    command2 = PathTextChangedCommand(item, item.text_along_path, self.text_entry.text())
                    self.canvas.addCommand(command2)
                    command3 = PathTextSpacingChangedCommand(item, item.text_along_path_spacing, self.spacing_spin.value())
                    self.canvas.addCommand(command3)
                    item.update()

                else:
                    command = AddTextToPathCommand(item, self.text_along_path_check_btn, True, False)
                    self.canvas.addCommand(command)
                    item.update()
