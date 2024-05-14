from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

class ToolbarHorizontalLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

class HorizontalSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor('#4b4b4b')
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(f'background-color: {self.color}; ')

class CustomColorPicker(QColorDialog):
    def __init__(self):
        super().__init__()

        self.setOption(QColorDialog.ShowAlphaChannel, True)

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
        canvas_label.setStyleSheet('font-size: 20px;')
        canvas_x_size_label = QLabel('W:')
        canvas_y_size_label = QLabel('H:')
        canvas_preset_label = QLabel('Preset:')
        canvas_name_label = QLabel('Name:')
        self.canvas_x_entry = QSpinBox(self)
        self.canvas_x_entry.setMaximum(5000)
        self.canvas_x_entry.setAlignment(Qt.AlignLeft)
        self.canvas_x_entry.valueChanged.connect(self.update_canvas)
        self.canvas_y_entry = QSpinBox(self)
        self.canvas_y_entry.setMaximum(5000)
        self.canvas_y_entry.setAlignment(Qt.AlignLeft)
        self.canvas_y_entry.valueChanged.connect(self.update_canvas)

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
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.update_canvas)

        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setFixedWidth(200)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
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

class StrokeLabel(QLabel):
    def __init__(self, text, parent):
        super().__init__(parent)

        self.setText(text)
        self.setObjectName('strokeLabel')

        self.pencap_combo = None
        self.stroke_combo = None
        self.stroke_options = None
        self.pencap_options = None

        self.menu = QMenu(self)

        widget1 = QWidgetAction(parent)
        widget2 = QWidgetAction(parent)

        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine,
                                     'Dotted Stroke': Qt.DotLine,
                                     'Dashed Stroke': Qt.DashLine,
                                     'Dashed Dot Stroke': Qt.DashDotLine,
                                     'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox(self)
        self.stroke_style_combo.setStyleSheet('text-decoration: none;')
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)
        self.stroke_pencap_options = {'Square Cap': Qt.SquareCap, 'Flat Cap': Qt.FlatCap, 'Round Cap': Qt.RoundCap}
        self.stroke_pencap_combo = QComboBox(self)
        self.stroke_pencap_combo.setStyleSheet('text-decoration: none;')
        for pencap, value in self.stroke_pencap_options.items():
            self.stroke_pencap_combo.addItem(pencap, value)

        widget1.setDefaultWidget(self.stroke_style_combo)
        widget2.setDefaultWidget(self.stroke_pencap_combo)

        self.menu.addAction(widget1)
        self.menu.addAction(widget2)

        self.stroke_combo = self.stroke_style_combo
        self.stroke_options = self.stroke_style_options
        self.pencap_combo = self.stroke_pencap_combo
        self.pencap_options = self.stroke_pencap_options

    def mousePressEvent(self, event):
        self.menu.exec_(event.globalPos())

class QIconWidget(QLabel):
    def __init__(self, text, icon_file, w, h, parent=None):
        super().__init__(parent)

        icon = QIcon(icon_file)
        self.setPixmap(icon.pixmap(w, h))
        self.setText(text)



