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
        self.setObjectName('colorButton')

    def setTransparent(self, enabled: bool):
        self.transparent = enabled
        self.repaint()

    def setButtonColor(self, color: str):
        self.setTransparent(False)
        self.setStyleSheet(f'background: {color};')

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.transparent:
            rect = self.rect()
            new_rect = QRectF(1, 1, rect.width() - 3, rect.height() - 3)
            self.setStyleSheet('background-color: transparent;')
            painter = QPainter(self)
            painter.setRenderHints(QPainter.HighQualityAntialiasing)
            painter.begin(self)
            painter.setBrush(QBrush(QColor('white')))
            painter.drawRect(new_rect)
            painter.setPen(QPen(QColor('red'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
            painter.drawLine(self.rect().bottomLeft() + QPointF(2, -1), self.rect().topRight() + QPointF(-1, 2))
            painter.end()

class CustomLineEdit(QLineEdit):
    focusChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)

        self.focusChanged.emit()

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
        self.r_hlayout = ToolbarHorizontalLayout()
        self.g_hlayout = ToolbarHorizontalLayout()
        self.b_hlayout = ToolbarHorizontalLayout()
        self.rgb_layout = QVBoxLayout()

        self.r_slider = QSlider(Qt.Horizontal)
        self.r_slider.setToolTip('Change the red value')
        self.r_slider.setRange(0, 255)
        self.g_slider = QSlider(Qt.Horizontal)
        self.g_slider.setToolTip('Change the green value')
        self.g_slider.setRange(0, 255)
        self.b_slider = QSlider(Qt.Horizontal)
        self.b_slider.setToolTip('Change the blue value')
        self.b_slider.setRange(0, 255)
        hex_label = QLabel('#')
        hex_label.setStyleSheet('font-size: 15px;')
        self.hex_spin = CustomLineEdit()
        self.hex_spin.setText(self.currentColor().name()[1:])
        self.hex_spin.setToolTip('Change the hex value')
        self.fill_transparent_btn = QColorButton()
        self.fill_transparent_btn.setTransparent(True)
        self.fill_transparent_btn.setFixedWidth(28)
        self.fill_transparent_btn.setToolTip('Fill the current color transparent')
        self.hex_hlayout = ToolbarHorizontalLayout()
        self.hex_hlayout.layout.addWidget(hex_label)
        self.hex_hlayout.layout.addWidget(self.hex_spin)

        # RGB Labels
        self.r_label = QLabel("R:")
        self.g_label = QLabel("G:")
        self.b_label = QLabel("B:")

        # Update
        self.hex_spin.focusChanged.connect(self.set_hex_color)
        self.fill_transparent_btn.clicked.connect(self.set_transparent)
        self.currentColorChanged.connect(self.color_changed)
        self.r_slider.valueChanged.connect(self.update_color)
        self.g_slider.valueChanged.connect(self.update_color)
        self.b_slider.valueChanged.connect(self.update_color)

        # Layout setup
        self.r_hlayout.layout.addWidget(self.r_label)
        self.r_hlayout.layout.addWidget(self.r_slider)
        self.g_hlayout.layout.addWidget(self.g_label)
        self.g_hlayout.layout.addWidget(self.g_slider)
        self.b_hlayout.layout.addWidget(self.b_label)
        self.b_hlayout.layout.addWidget(self.b_slider)
        self.rgb_layout.addWidget(self.r_hlayout)
        self.rgb_layout.addWidget(self.g_hlayout)
        self.rgb_layout.addWidget(self.b_hlayout)

        self.layout().insertLayout(1, self.rgb_layout)
        self.layout().insertWidget(1, self.hex_hlayout)
        self.layout().insertWidget(1, self.fill_transparent_btn)

    def set_hex_color(self):
        if self.hex_spin.text().lower() == 'transparent':
            self.setCurrentColor(QColor(Qt.transparent))

        else:
            try:
                self.setCurrentColor(QColor(f'#{self.hex_spin.text()}'))

            except Exception:
                pass

    def update_color(self):
        r = self.r_slider.value()
        g = self.g_slider.value()
        b = self.b_slider.value()
        self.hex_spin.blockSignals(True)
        self.hex_spin.setText(self.currentColor().name()[1:])
        self.setCurrentColor(QColor(r, g, b))
        self.hex_spin.blockSignals(False)

    def color_changed(self):
        color = self.currentColor()
        self.hex_spin.setText(color.name()[1:])
        self.r_slider.setValue(color.red())
        self.g_slider.setValue(color.green())
        self.b_slider.setValue(color.blue())

    def set_transparent(self):
        self.setCurrentColor(QColor(Qt.transparent))
        self.hex_spin.setText('transparent')

class ViewWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)

            if isinstance(item, CustomTextItem):
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
        self.setToolTip('Change the stroke style')
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

        self.stroke_style_combo.setItemData(0, QPixmap('UI/UI Icons/Combobox Images/solid_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(1, QPixmap('UI/UI Icons/Combobox Images/dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(2, QPixmap('UI/UI Icons/Combobox Images/dashed_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(3, QPixmap(
            'UI/UI Icons/Combobox Images/dashed_dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(4, QPixmap(
            'UI/UI Icons/Combobox Images/dashed_dot_dot_stroke.png'), Qt.DecorationRole)
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
                                             QIcon('UI/UI Icons/Combobox Images/projecting_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(1,
                                             QIcon('UI/UI Icons/Combobox Images/flat_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(2,
                                             QIcon('UI/UI Icons/Combobox Images/round_cap.svg'),
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

        self.setOpenExternalLinks(True)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        webbrowser.open_new(self.link)

class CustomDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())
        self.setFeatures(QDockWidget.AllDockWidgetFeatures)

        self.close_btn = QPushButton('', self)
        self.close_btn.setIcon(QIcon('UI/UI Icons/close-button-qdockwidget.svg'))
        self.close_btn.setIconSize(QSize(12, 12))
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet('QPushButton { background: #424242;'
                            'border: none; }'
                            'QPushButton:hover {'
                            'background: #494949; }')
        self.close_btn.setFixedSize(QSize(14, 14))

        self.title_bar = QWidget(self)
        self.title_bar.setObjectName('dockWidgetTitleBar')
        self.title_bar.setFixedHeight(20)
        self.title_bar.setLayout(QHBoxLayout())
        self.title_bar.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.title_bar.layout().addWidget(self.close_btn)
        self.title_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.title_bar.layout().setSpacing(0)

        self.setTitleBarWidget(self.title_bar)









