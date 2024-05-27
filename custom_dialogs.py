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
        self.setWindowTitle("Export Canvas")
        self.setWindowIcon(QIcon('logos and icons/Main Logos/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(700)
        self.setFixedHeight(500)

        self.canvas = canvas
        self.watermark_item = None

        # Create the layout
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)

        self.createUI()

    def createUI(self):
        # Scene and View
        self.view = ViewWidget()
        self.view.setScene(self.canvas)
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.fitInView(self.canvas.itemsBoundingRect())

        # Labels
        selected_canvas_label = QLabel('Selected Canvas:')
        export_options_label = QLabel('Export Options:')

        # Canvas selector
        self.canvas_chooser_combo = QComboBox()
        self.canvas_chooser_combo.setToolTip('Select a canvas to export')
        self.canvas_chooser_combo.currentIndexChanged.connect(self.canvas_changed)

        # Transparent option checkbox
        self.transparent_check_btn = QCheckBox()
        self.transparent_check_btn.setText('Transparent Background')
        self.transparent_check_btn.setToolTip('Export the selected canvas with a transparent background')

        # Watermark option checkbox
        self.watermark_check_btn = QCheckBox()
        self.watermark_check_btn.setText('Add Watermark')
        self.watermark_check_btn.setToolTip('Help support us by adding an MPRUN watermark')
        self.watermark_check_btn.clicked.connect(self.add_watermark)

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
        self.layout.addWidget(self.watermark_check_btn)
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

    def add_watermark(self):
        try:
            if self.watermark_check_btn.isChecked():
                if self.watermark_item is not None:
                    self.canvas.removeItem(self.watermark_item)

                self.watermark_item = QGraphicsPixmapItem(QPixmap('logos and icons/Main Logos/MPRUN_logo_rounded_corners_version.png'))
                self.canvas.addItem(self.watermark_item)

                selected_item = self.canvas_chooser_combo.itemData(self.canvas_chooser_combo.currentIndex())

                self.watermark_item.setScale(0.1)
                self.watermark_item.setZValue(10000)
                self.watermark_item.setToolTip('MPRUN Watermark')
                self.watermark_item.setPos(selected_item.sceneBoundingRect().bottomRight().x() - 65, selected_item.sceneBoundingRect().bottomRight().y() - 65)

            else:
                if self.watermark_item is not None:
                    self.canvas.removeItem(self.watermark_item)

        except Exception:
            pass

    def canvas_changed(self):
        selected_item = self.canvas_chooser_combo.itemData(self.canvas_chooser_combo.currentIndex())

        if self.watermark_item is not None:
            self.watermark_item.setPos(selected_item.sceneBoundingRect().bottomRight().x() - 65,
                                       selected_item.sceneBoundingRect().bottomRight().y() - 65)

        self.view.fitInView(selected_item.sceneBoundingRect(), Qt.KeepAspectRatio)

    def closeEvent(self, e):
        self.parent().use_exit_add_canvas()

        if self.watermark_item is not None:
            self.canvas.removeItem(self.watermark_item)

class CanvasEditorPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.setMaximumHeight(225)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.canvas = canvas
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
        canvas_label = QLabel('Canvas')
        canvas_label.setStyleSheet('font-size: 12px;')
        canvas_x_size_label = QLabel('W:')
        canvas_y_size_label = QLabel('H:')
        canvas_preset_label = QLabel('Preset:')
        canvas_name_label = QLabel('Name:')
        self.canvas_x_entry = QSpinBox(self)
        self.canvas_x_entry.setMaximum(5000)
        self.canvas_x_entry.setAlignment(Qt.AlignLeft)
        self.canvas_x_entry.setToolTip('Change the width of the canvas')
        self.canvas_x_entry.valueChanged.connect(self.update_canvas)
        self.canvas_y_entry = QSpinBox(self)
        self.canvas_y_entry.setMaximum(5000)
        self.canvas_y_entry.setAlignment(Qt.AlignLeft)
        self.canvas_y_entry.setToolTip('Change the height of the canvas')
        self.canvas_y_entry.valueChanged.connect(self.update_canvas)

        self.canvas_preset_dropdown = QComboBox(self)
        self.canvas_preset_dropdown.setFixedWidth(200)
        self.canvas_preset_dropdown.setToolTip('Change the preset of the canvas')
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
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.update_canvas)

        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setFixedWidth(200)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
        self.canvas_name_entry.setToolTip('Change the name of the canvas')
        self.canvas_name_entry.textChanged.connect(self.update_canvas)

        widget1 = ToolbarHorizontalLayout()
        widget1.layout.addWidget(canvas_x_size_label)
        widget1.layout.addWidget(self.canvas_x_entry)
        widget1.layout.addWidget(canvas_y_size_label)
        widget1.layout.addWidget(self.canvas_y_entry)

        widget2 = ToolbarHorizontalLayout()
        widget2.layout.addWidget(canvas_preset_label)
        widget2.layout.addWidget(self.canvas_preset_dropdown)

        widget3 = ToolbarHorizontalLayout()
        widget3.layout.addWidget(canvas_name_label)
        widget3.layout.addWidget(self.canvas_name_entry)

        self.layout.addWidget(HorizontalSeparator())
        self.layout.addWidget(canvas_label)
        self.layout.addWidget(widget1)
        self.layout.addWidget(widget2)
        self.layout.addWidget(widget3)

    def update_canvas(self):
        choice = self.canvas_preset_dropdown.itemData(self.canvas_preset_dropdown.currentIndex())

        if choice == 'c':
            pass

        elif choice == 1:
            self.canvas_x_entry.setValue(1000)
            self.canvas_y_entry.setValue(700)

        elif choice == 2:
            self.canvas_x_entry.setValue(1920)
            self.canvas_y_entry.setValue(1080)

        elif choice == 3:
            self.canvas_x_entry.setValue(792)
            self.canvas_y_entry.setValue(612)

        elif choice == 4:
            self.canvas_x_entry.setValue(1008)
            self.canvas_y_entry.setValue(792)

        elif choice == 5:
            self.canvas_x_entry.setValue(595)
            self.canvas_y_entry.setValue(842)

        elif choice == 6:
            self.canvas_x_entry.setValue(828)
            self.canvas_y_entry.setValue(1169)

        elif choice == 7:
            self.canvas_x_entry.setValue(1080)
            self.canvas_y_entry.setValue(1920)

        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                for self.child in item.childItems():
                    if isinstance(self.child, CanvasTextItem):
                        self.child.setText(self.canvas_name_entry.text())

                item.setToolTip(self.canvas_name_entry.text())

                try:
                    item.setRect(0, 0, self.canvas_x_entry.value(), self.canvas_y_entry.value())
                    self.child.setPos(item.boundingRect().x(), item.boundingRect().y())

                except Exception:
                    pass

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
