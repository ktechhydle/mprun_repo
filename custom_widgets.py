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

class CustomColorPicker(QColorDialog):
    def __init__(self):
        super().__init__()

        self.setOption(QColorDialog.ShowAlphaChannel, True)

class CanvasEditorPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
        canvas_label = QLabel('Canvas')
        canvas_label.setStyleSheet('font-size: 20px;')
        canvas_x_size_label = QLabel('X:')
        canvas_y_size_label = QLabel('Y:')
        self.canvas_x_entry = QSpinBox(self)
        self.canvas_x_entry.setMaximum(5000)
        self.canvas_x_entry.valueChanged.connect(self.update_canvas)
        self.canvas_y_entry = QSpinBox(self)
        self.canvas_y_entry.setMaximum(5000)
        self.canvas_y_entry.valueChanged.connect(self.update_canvas)
        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
        self.canvas_name_entry.textChanged.connect(self.update_canvas)

        widget1 = ToolbarHorizontalLayout()
        widget1.layout.addWidget(canvas_x_size_label)
        widget1.layout.addWidget(self.canvas_x_entry)
        widget1.layout.addWidget(canvas_y_size_label)
        widget1.layout.addWidget(self.canvas_y_entry)

        self.layout.addWidget(canvas_label)
        self.layout.addWidget(widget1)
        self.layout.addWidget(self.canvas_name_entry)
        self.layout.addSpacing(800)

    def update_canvas(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                for child in item.childItems():
                    if isinstance(child, EditableTextBlock):
                        child.setPlainText(self.canvas_name_entry.text())

                item.setToolTip(self.canvas_name_entry.text())

                try:
                    item.setRect(item.x(), item.y(), self.canvas_x_entry.value(), self.canvas_y_entry.value())

                except Exception:
                    pass
