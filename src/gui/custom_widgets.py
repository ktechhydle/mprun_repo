from src.scripts.imports import *
from src.framework.custom_classes import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

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
        self.setStyleSheet(f'background-color: {self.color}; color: {self.color}')
        self.setFixedHeight(2)  # Set the height to 1 pixel

    def sizeHint(self):
        return QSize(2, 2)

    def minimumSizeHint(self):
        return QSize(2, 2)

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
        if color == 'transparent':
            self.setTransparent(True)
            return

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
    
class ToolButton(QToolButton):
    def __init__(self):
        super().__init__()

        self.setIconSize(QSize(10, 10))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if event.button() == Qt.RightButton:
            self.showMenu()

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

        self.stroke_style_combo.setItemData(0, QPixmap('ui/UI Icons/Combobox Images/solid_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(1, QPixmap('ui/UI Icons/Combobox Images/dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(2, QPixmap('ui/UI Icons/Combobox Images/dashed_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(3, QPixmap(
            'ui/UI Icons/Combobox Images/dashed_dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(4, QPixmap(
            'ui/UI Icons/Combobox Images/dashed_dot_dot_stroke.png'), Qt.DecorationRole)
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
                                             QIcon('ui/UI Icons/Combobox Images/projecting_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(1,
                                             QIcon('ui/UI Icons/Combobox Images/flat_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(2,
                                             QIcon('ui/UI Icons/Combobox Images/round_cap.svg'),
                                             Qt.DecorationRole)

        self.join_style_options = {
            'Bevel Join': Qt.BevelJoin,
            'Round Join': Qt.RoundJoin,
            'Miter Join': Qt.MiterJoin,
                                   }
        self.join_style_combo = QComboBox(self)
        self.join_style_combo.setStyleSheet('text-decoration: none;')
        self.join_style_combo.setIconSize(QSize(65, 20))
        for join, v in self.join_style_options.items():
            self.join_style_combo.addItem(join, v)

        self.join_style_combo.setItemData(0, QIcon('ui/UI Icons/Combobox Images/bevel_join.png'), Qt.DecorationRole)
        self.join_style_combo.setItemData(1, QIcon('ui/UI Icons/Combobox Images/round_join.png'), Qt.DecorationRole)
        self.join_style_combo.setItemData(2, QIcon('ui/UI Icons/Combobox Images/miter_join.png'), Qt.DecorationRole)

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
        btn_pos = self.mapToGlobal(QPoint(0, 0))
        y = btn_pos.y() + 25
        x = btn_pos.x() - self.width()

        self.menu.exec_(QPoint(x, y))

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
    def __init__(self, toolbox, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.toolbox = toolbox
        self.icon_buttons = []
        self.panels = []
        self.panel_names = []
        self.indexes = []
        self.is_collapsed = False
        self.paint()

    def paint(self):
        self.close_btn = QPushButton('', self)
        self.close_btn.setToolTip('Close')
        self.close_btn.setIcon(QIcon('mp_software_stylesheets/assets/cross.svg'))
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet('QPushButton { background: #424242;'
                                     'border: none; }'
                                     'QPushButton:hover {'
                                     'background: #494949; }')
        self.close_btn.setFixedSize(QSize(18, 18))

        self.minimize_btn = QPushButton('', self)
        self.minimize_btn.setToolTip('Collapse')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/minimize.svg'))
        self.minimize_btn.setIconSize(QSize(16, 16))
        self.minimize_btn.clicked.connect(self.toggle_collapse)
        self.minimize_btn.setStyleSheet('QPushButton { background: #424242;'
                                        'border: none; }'
                                        'QPushButton:hover {'
                                        'background: #494949; }')
        self.minimize_btn.setFixedSize(QSize(18, 18))

        self.title_bar = QWidget(self)
        self.title_bar.setObjectName('dockWidgetTitleBar')
        self.title_bar.setFixedHeight(20)
        self.title_bar.setLayout(QHBoxLayout())
        self.title_bar.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.title_bar.layout().addWidget(self.minimize_btn)
        self.title_bar.layout().addWidget(self.close_btn)
        self.title_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.title_bar.layout().setSpacing(0)

        self.setTitleBarWidget(self.title_bar)

    def toggle_collapse(self):
        if self.isCollapsed():
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        self.setFixedWidth(100)
        self.is_collapsed = True
        self.toolbox.setHidden(True)
        self.icon_buttons = []

        icons_widget = QWidget(self)
        icons_layout = QVBoxLayout()
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_widget.setLayout(icons_layout)

        for i in range(self.toolbox.count()):
            btn = QPushButton(self.toolbox.itemText(i), self)
            btn.setIcon(self.toolbox.itemIcon(i))
            btn.clicked.connect(lambda _, idx=i: self.show_toolbox_panel(idx))
            icons_layout.addWidget(btn)
            self.icon_buttons.append(btn)

        icons_widget.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.setWidget(icons_widget)
        self.minimize_btn.setToolTip('Expand to panels')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/maximize.svg'))

    def expand(self):
        self.setFixedWidth(300)
        self.is_collapsed = False
        self.setWidget(self.toolbox)
        self.toolbox.setHidden(False)
        self.minimize_btn.setToolTip('Collapse to buttons')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/minimize.svg'))

        if len(self.panels) > 0:
            for i in range(len(self.indexes)):
                self.toolbox.setWidgetAtIndex(self.indexes[i], self.panels[i], self.panel_names[i])

    def show_toolbox_panel(self, index):
        panel = self.toolbox.widget(index)
        self.panels.append(panel)
        self.panel_names.append(self.toolbox.itemText(index))
        self.indexes.append(index)

        unique_items1 = []
        seen1 = set()
        for item in self.panels:
            if item not in seen1:
                unique_items1.append(item)
                seen1.add(item)

        unique_items2 = []
        seen2 = set()
        for item in self.panel_names:
            if item not in seen2:
                unique_items2.append(item)
                seen2.add(item)

        unique_items3 = []
        seen3 = set()
        for item in self.indexes:
            if item not in seen3:
                unique_items3.append(item)
                seen3.add(item)

        self.panels = unique_items1
        self.panel_names = unique_items2
        self.indexes = unique_items3

        popup = QMenu(self)
        action = QWidgetAction(popup)
        action.setDefaultWidget(panel)
        popup.addAction(action)

        button = self.icon_buttons[index]
        button_pos = button.mapToGlobal(QPoint(0, 0))

        # Adjust the position to show the menu at the top-right corner of the button
        popup_pos = button_pos + QPoint(button.width(), 0)
        popup.exec_(QPoint(((popup_pos.x() - panel.width()) - button.width()) - 10, popup_pos.y()))

        print(self.panels)
        print(self.panel_names)
        print(self.indexes)

    def isCollapsed(self):
        return self.is_collapsed

class CustomToolbox(QToolBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        for i in range(self.count()):
            page = self.widget(i)
            scroll_area = page.findChild(QScrollArea)
            if scroll_area:
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setWidgetAtIndex(self, index, widget, name):
        self.removeItem(index)
        self.insertItem(index, widget, name)

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.all_items = []

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(item.data(Qt.UserRole))])
            drag.setMimeData(mime_data)

            # Optional: set a drag image
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def filter_items(self, text):
        for item in self.all_items:
            item.setHidden(True)

            if text.lower() in item.text().lower():
               item.setHidden(False)










