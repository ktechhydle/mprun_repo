from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from custom_widgets import *
from undo_commands import *

class CanvasItemSelector(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Canvas")
        self.setWindowIcon(QIcon('logos and icons/Main Logos/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(700)
        self.setFixedHeight(500)

        # Activate add canvas tool
        self.parent().use_add_canvas()
        self.canvas = canvas

        # Create the layout
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)

        self.createUI()

    def createUI(self):
        # Scene and View
        self.view = ViewWidget()
        self.view.setScene(self.canvas)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.scale(0.25, 0.25)

        # Labels
        selected_canvas_label = QLabel('Selected Canvas:')
        export_options_label = QLabel('Export Options:')

        # Canvas selector
        self.canvas_chooser_combo = QComboBox()
        self.canvas_chooser_combo.setToolTip('Select a canvas to export')

        # Transparent option checkbox
        self.transparent_check_btn = QCheckBox()
        self.transparent_check_btn.setChecked(False)
        self.transparent_check_btn.setText('Transparent Background')
        self.transparent_check_btn.setToolTip('Export the selected canvas with a transparent background')

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip('Export the selected canvas')

        # Add widgets
        self.layout.addWidget(HorizontalSeparator())
        self.hlayout.addWidget(self.view)
        self.layout.addWidget(selected_canvas_label)
        self.layout.addWidget(self.canvas_chooser_combo)
        self.layout.addWidget(export_options_label)
        self.layout.addWidget(self.transparent_check_btn)
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.export_btn)
        self.hlayout.addLayout(self.layout)


    def add_canvas_item(self, itemName, itemKey):
        if isinstance(itemKey, CanvasItem):
            values = {itemName: itemKey}
            for name, key in values.items():
                self.canvas_chooser_combo.addItem(name, key)

        else:
            pass

    def closeEvent(self, e):
        self.parent().use_exit_add_canvas()


class TextAlongPathPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.canvas = canvas

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(225)

        self.createUi()

    def createUi(self):
        main_label = QLabel('Text Along Path')
        main_label.setStyleSheet("QLabel { font-size: 12px; }")
        spacing_label = QLabel('Spacing From Path:')
        spacing_label.setStyleSheet("QLabel { font-size: 12px; }")

        self.text_along_path_check_btn = QCheckBox(self)
        self.text_along_path_check_btn.setToolTip('Add text along the path')
        self.text_along_path_check_btn.setText('Add Text Along Path')

        self.distrubute_evenly_check_btn = QCheckBox(self)
        self.distrubute_evenly_check_btn.setToolTip('Distribute the text along the path evenly')
        self.distrubute_evenly_check_btn.setText('Distribute Text Evenly')

        self.spacing_spin = QSpinBox(self)
        self.spacing_spin.setRange(-1000, 10000)
        self.spacing_spin.setSuffix(' pt')
        self.spacing_spin.setToolTip('Text spacing from path')

        self.text_entry = QLineEdit(self)
        self.text_entry.setPlaceholderText('Enter Text')
        self.text_entry.setToolTip('Enter text along the path')

        self.layout.addWidget(HorizontalSeparator())
        self.layout.addWidget(main_label)
        self.layout.addWidget(self.text_along_path_check_btn)
        self.layout.addWidget(self.distrubute_evenly_check_btn)
        self.layout.addWidget(spacing_label)
        self.layout.addWidget(self.spacing_spin)
        self.layout.addWidget(self.text_entry)

        self.text_along_path_check_btn.clicked.connect(self.update_path)
        self.distrubute_evenly_check_btn.clicked.connect(self.update_path)
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

                    if self.distrubute_evenly_check_btn.isChecked():
                        item.setTextAlongPathFromBeginning(False)

                    else:
                        item.setTextAlongPathFromBeginning(True)

                    item.update()

                else:
                    command = AddTextToPathCommand(item, self.text_along_path_check_btn, True, False)
                    self.canvas.addCommand(command)
                    item.update()
