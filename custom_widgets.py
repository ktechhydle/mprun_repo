from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
import webbrowser

class ToolbarHorizontalLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

class HorizontalSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = '#4b4b4b'
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(f'background-color: {self.color}; ')

class QColorButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.transparent = False

    def setTransparent(self, enabled: bool):
        self.transparent = enabled

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.transparent:
            self.setStyleSheet('background-color: transparent;')
            painter = QPainter(self)
            painter.setRenderHints(QPainter.HighQualityAntialiasing)
            pen = painter.pen()
            pen.setColor(QColor('red'))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.begin(self)
            painter.drawLine(self.rect().topLeft(), self.rect().bottomRight())
            painter.end()

class CustomColorPicker(QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOptions(self.options() | QColorDialog.DontUseNativeDialog)

        for children in self.findChildren(QWidget):
            classname = children.metaObject().className()
            if classname not in ("QColorPicker", "QColorLuminancePicker"):
                children.hide()

        self.setOption(QColorDialog.ShowAlphaChannel, True)

        # Custom widgets
        self.swatch_hlayout = ToolbarHorizontalLayout()
        self.hex_spin = QLineEdit(self)
        self.hex_spin.setText(self.currentColor().name())
        self.fill_transparent_btn = QColorButton(self)
        self.fill_transparent_btn.setTransparent(True)
        self.fill_transparent_btn.setFixedWidth(28)
        self.fill_transparent_btn.setToolTip('Fill the current color transparent')

        # Update
        self.fill_transparent_btn.clicked.connect(self.set_transparent)
        self.currentColorChanged.connect(lambda: self.hex_spin.setText(self.currentColor().name()))
        self.hex_spin.textChanged.connect(self.update_color)

        self.layout().insertWidget(1, self.hex_spin)
        self.layout().insertWidget(1, self.fill_transparent_btn)

    def update_color(self):
        self.hex_spin.blockSignals(True)
        self.setCurrentColor(QColor(self.hex_spin.text()))
        self.hex_spin.blockSignals(False)

    def set_transparent(self):
        self.setCurrentColor(QColor(Qt.transparent))

class ViewWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)

            if isinstance(item, EditableTextBlock):
                item.set_locked()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        pass

    def keyPressEvent(self, event):
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
        self.join_style_combo = None
        self.join_style_options = None

        self.menu = QMenu(self)

        widget1 = QWidgetAction(parent)
        widget2 = QWidgetAction(parent)
        widget3 = QWidgetAction(parent)

        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine,
                                     'Dotted Stroke': Qt.DotLine,
                                     'Dashed Stroke': Qt.DashLine,
                                     'Dashed Dot Stroke': Qt.DashDotLine,
                                     'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox(self)
        self.stroke_style_combo.setStyleSheet('text-decoration: none;')
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)

        self.stroke_style_combo.setItemData(0, QPixmap('logos and icons/UI Icons/Combobox Images/solid_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(1, QPixmap('logos and icons/UI Icons/Combobox Images/dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(2, QPixmap('logos and icons/UI Icons/Combobox Images/dashed_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(3, QPixmap(
            'logos and icons/UI Icons/Combobox Images/dashed_dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(4, QPixmap(
            'logos and icons/UI Icons/Combobox Images/dashed_dot_dot_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setIconSize(QSize(65, 20))

        self.stroke_pencap_options = {'Square Cap': Qt.SquareCap,
                                      'Flat Cap': Qt.FlatCap,
                                      'Round Cap': Qt.RoundCap}
        self.stroke_pencap_combo = QComboBox(self)
        self.stroke_pencap_combo.setStyleSheet('text-decoration: none;')
        for pencap, value in self.stroke_pencap_options.items():
            self.stroke_pencap_combo.addItem(pencap, value)
        self.stroke_pencap_combo.setIconSize(QSize(65, 20))
        self.stroke_pencap_combo.setItemData(0,
                                             QIcon('logos and icons/UI Icons/Combobox Images/projecting_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(1,
                                             QIcon('logos and icons/UI Icons/Combobox Images/flat_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(2,
                                             QIcon('logos and icons/UI Icons/Combobox Images/round_cap.svg'),
                                             Qt.DecorationRole)

        self.join_style_options = {'Miter Join': Qt.MiterJoin,
                                   'Round Join': Qt.RoundJoin,
                                   'Bevel Join': Qt.BevelJoin
                                   }
        self.join_style_combo = QComboBox(self)
        self.join_style_combo.setStyleSheet('text-decoration: none;')
        for join, v in self.join_style_options.items():
            self.join_style_combo.addItem(join, v)

        widget1.setDefaultWidget(self.stroke_style_combo)
        widget2.setDefaultWidget(self.stroke_pencap_combo)
        widget3.setDefaultWidget(self.join_style_combo)


        self.menu.addAction(widget1)
        self.menu.addAction(widget2)
        self.menu.addAction(widget3)

        self.stroke_combo = self.stroke_style_combo
        self.stroke_options = self.stroke_style_options
        self.pencap_combo = self.stroke_pencap_combo
        self.pencap_options = self.stroke_pencap_options

    def mousePressEvent(self, event):
        self.menu.exec_(event.globalPos())

class QIconWidget(QLabel):
    def __init__(self, text: str, icon_file: str, w: int, h: int, parent=None):
        super().__init__(parent)

        icon = QIcon(icon_file)
        self.setPixmap(icon.pixmap(w, h))
        self.setText(text)

class QMoreOrLessLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        less_label = QLabel('Less')
        less_label.setAlignment(Qt.AlignLeft)
        more_label = QLabel('More')
        more_label.setAlignment(Qt.AlignRight)

        layout.addWidget(less_label)
        layout.addWidget(more_label)

class QLinkLabel(QLabel):
    def __init__(self, text, link: str):
        super().__init__()

        self.font = QFont()
        self.font.setUnderline(True)
        self.setText(text)
        self.setFont(self.font)
        self.link = link

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        webbrowser.open_new(self.link)







