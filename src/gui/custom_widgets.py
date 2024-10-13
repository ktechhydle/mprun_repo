import time
from src.scripts.imports import *
from src.framework.items import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class ToolbarHorizontalLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)


class CustomToolbar(QToolBar):
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu:
            self.contextMenuEvent(event)  # Check if this is triggered instead
            return True  # This prevents contextMenuEvent from being called
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        # Define the minimum and maximum icon sizes
        min_size = 16
        max_size = 60

        # Determine the amount to change the icon size by
        if event.angleDelta().y() > 0:
            amount = 2  # Scroll up increases size
        else:
            amount = -2  # Scroll down decreases size

        # Get the current icon size
        current_size = self.iconSize()
        new_size = current_size.width() + amount

        # Ensure the new size is within the defined limits
        new_size = max(min_size, min(max_size, new_size))

        # Set the new icon size with the limited values
        new_icon_size = QSize(new_size, new_size)
        self.setIconSize(new_icon_size)

        # Dynamically adjust toolbar size to prevent unnecessary scrolling
        self.adjustSize()

    def mouseDoubleClickEvent(self, event):
        # Reset to default icon size on double click
        default_icon_size = QSize(32, 32)
        self.setIconSize(default_icon_size)

        # Adjust the toolbar size as well
        self.adjustSize()

    def setIconSize(self, iconSize):
        super().setIconSize(iconSize)

        # Iterate through all the actions in the toolbar
        for action in self.actions():
            # Get the widget corresponding to the action (usually a QToolButton)
            widget = self.widgetForAction(action)

            if isinstance(widget, QToolButton):
                widget.setIconSize(iconSize)

    def contextMenuEvent(self, event):
        # Create a custom context menu
        menu = CustomMenu(self)

        help_action = QAction(self.style().standardIcon(self.style().SP_MessageBoxQuestion), '&Help', self)

        if isinstance(self.parent(), QMainWindow):
            help_action.triggered.connect(self.parent().show_help)

        menu.addAction(help_action)

        menu.exec(event.globalPos())


class HorizontalSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName('splitter')
        self.setFixedHeight(2)  # Set the height to 1 pixel

    def sizeHint(self):
        return QSize(2, 2)

    def minimumSizeHint(self):
        return QSize(2, 2)


class CustomColorDisplayButton(QPushButton):
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
        self.repaint()

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
            painter.setPen(QPen(QColor('red'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
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
        self.setObjectName('tipWindow')

        for children in self.findChildren(QWidget):
            classname = children.metaObject().className()

            # Only hide specific widgets, keeping "OK" and "Cancel" buttons
            if classname == "QPushButton":
                button_text = children.text()

                # Check the button text and only show "OK" and "Cancel"
                if button_text not in ("OK", "Cancel"):
                    children.hide()
            elif classname not in ("QColorPicker", "QColorLuminancePicker", "QDialogButtonBox"):
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
        self.fill_transparent_btn = CustomColorDisplayButton()
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


class CustomViewWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)

            if isinstance(item, CustomTextItem):
                item.setLocked()

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


class CustomToolButton(QToolButton):
    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(32, 32))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)

        self.init()

    def init(self):
        # Create a custom menu
        self.custom_menu = CustomMenu(self)

        # Set the custom menu as the default menu
        self.setMenu(self.custom_menu)

    def addAction(self, action):
        self.custom_menu.addAction(action)

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

        self.menu = CustomMenu(self)
        self.menu.setObjectName('tipWindow')

        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine,
                                     'Dotted Stroke': Qt.DotLine,
                                     'Dashed Stroke': Qt.DashLine,
                                     'Dashed Dot Stroke': Qt.DashDotLine,
                                     'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox(self)
        self.stroke_style_combo.setStyleSheet('text-decoration: none;')
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)

        self.stroke_style_combo.setItemData(0, QPixmap('ui/UI Icons/Combobox Images/solid_stroke.png'),
                                            Qt.DecorationRole)
        self.stroke_style_combo.setItemData(1, QPixmap('ui/UI Icons/Combobox Images/dotted_stroke.png'),
                                            Qt.DecorationRole)
        self.stroke_style_combo.setItemData(2, QPixmap('ui/UI Icons/Combobox Images/dashed_stroke.png'),
                                            Qt.DecorationRole)
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

        widget = QWidget()
        widget.setObjectName('tipWindow')
        widget.setLayout(QVBoxLayout())
        widget.layout().addWidget(self.stroke_style_combo)
        widget.layout().addWidget(self.stroke_pencap_combo)
        widget.layout().addWidget(self.join_style_combo)
        action = QWidgetAction(parent)
        action.setDefaultWidget(widget)

        self.menu.addAction(action)

        self.stroke_combo = self.stroke_style_combo
        self.stroke_options = self.stroke_style_options
        self.pencap_combo = self.stroke_pencap_combo
        self.pencap_options = self.stroke_pencap_options

    def mousePressEvent(self, event):
        btn_pos = self.mapToGlobal(QPoint(0, 0))
        y = btn_pos.y() + 25
        x = btn_pos.x() - self.width()

        self.menu.exec_(QPoint(x, y))


class CustomIconWidget(QLabel):
    def __init__(self, text: str, icon_file: str, w: int, h: int, parent=None):
        super().__init__(parent)

        icon = QIcon(icon_file)
        self.setPixmap(icon.pixmap(w, h))
        self.setText(text)


class CustomMoreOrLessLabel(QWidget):
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


class CustomExternalLinkLabel(QLabel):
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
    def __init__(self, toolbox: QToolBox, parent=None):
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
        self.close_btn.setObjectName('noneBorderedButton')
        self.close_btn.setFixedSize(QSize(18, 18))

        self.minimize_btn = QPushButton('', self)
        self.minimize_btn.setToolTip('Collapse')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/minimize.svg'))
        self.minimize_btn.setIconSize(QSize(16, 16))
        self.minimize_btn.clicked.connect(self.toggleCollapse)
        self.minimize_btn.setObjectName('noneBorderedButton')
        self.minimize_btn.setFixedSize(QSize(18, 18))

        self.title_bar = QWidget(self)
        self.title_bar.setObjectName('dockWidgetTitleBar')
        self.title_bar.setFixedHeight(25)
        self.title_bar.setLayout(QHBoxLayout())
        self.title_bar.layout().addStretch()
        self.title_bar.layout().addWidget(self.minimize_btn)
        self.title_bar.layout().addWidget(self.close_btn)
        self.title_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.title_bar.layout().setSpacing(0)

        self.setTitleBarWidget(self.title_bar)

    def toggleCollapse(self):
        if self.isCollapsed():
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        self.setFixedWidth(125)
        self.is_collapsed = True
        self.icon_buttons = []

        icons_widget = QWidget(self)
        icons_layout = QVBoxLayout()
        icons_layout.setContentsMargins(5, 5, 5, 5)
        icons_widget.setLayout(icons_layout)

        for i in range(self.toolbox.count()):
            btn = QPushButton(self.toolbox.itemText(i), self)
            btn.setIcon(self.toolbox.itemIcon(i))
            btn.clicked.connect(lambda _, idx=i: self.showToolboxPanel(idx))
            icons_layout.addWidget(btn)
            self.icon_buttons.append(btn)

        icons_widget.layout().addStretch()

        self.setWidget(icons_widget)
        self.minimize_btn.setToolTip('Expand to panels')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/maximize.svg'))

    def expand(self):
        self.setFixedWidth(300)
        self.is_collapsed = False
        self.minimize_btn.setToolTip('Collapse to buttons')
        self.minimize_btn.setIcon(QIcon('mp_software_stylesheets/assets/minimize.svg'))

        if 0 < len(self.panels) == len(self.indexes):
            for i in range(len(self.indexes)):
                QTimer.singleShot(250 * i,
                                  lambda idx=i: self.toolbox.setWidgetAtIndex(self.indexes[idx], self.panels[idx],
                                                                              self.panel_names[idx]))
                print(f"Setting widget at index: {self.indexes[i]} with panel: {self.panels[i]}")

        if hasattr(self, 'popup'):
            self.popup.close()

        self.setWidget(self.toolbox)
        QTimer.singleShot(len(self.indexes) * 500, lambda: self.toolbox.createIcons())

    def showToolboxPanel(self, index):
        panel = self.toolbox.widget(index)

        if index not in self.indexes:
            self.panels.append(panel)
            self.panel_names.append(self.toolbox.itemText(index))
            self.indexes.append(index)

        print(self.panels)
        print(self.panel_names)
        print(self.indexes)

        if hasattr(self, 'popup'):
            self.popup.close()
        self.popup = CustomMenu(self)
        self.popup.setObjectName('tipWindow')
        self.popup.resize(panel.width(), panel.height())
        self.popup.setWindowFlag(Qt.WindowType.Tool)
        action = QWidgetAction(self.popup)
        action.setDefaultWidget(panel)
        self.popup.addAction(action)

        button = self.icon_buttons[index]
        button_pos = button.mapToGlobal(QPoint(0, 0))

        popup_pos = button_pos + QPoint(button.width(), 0)
        self.popup.exec_(QPoint(((popup_pos.x() - panel.width()) - button.width()) - 10, popup_pos.y()))

    def isCollapsed(self):
        return self.is_collapsed

    def closeEvent(self, event):
        if hasattr(self, 'popup'):
            self.popup.close()

        event.accept()


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

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ShiftModifier:
            if event.angleDelta().y() > 0 and self.currentIndex() > 0:
                self.setCurrentIndex(self.currentIndex() - 1)  # Scroll up
            elif event.angleDelta().y() < 0 and self.currentIndex() < self.count() - 1:
                self.setCurrentIndex(self.currentIndex() + 1)  # Scroll down
            return

        # Get the mouse position relative to the toolbox
        mouse_pos = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))

        # Get the current index
        current_index = self.currentIndex()
        max_index = self.count() - 1  # Get the maximum index

        title_rect = self.calculateTitleRect()

        if title_rect.contains(mouse_pos):
            if event.angleDelta().y() > 0 and current_index > 0:
                self.setCurrentIndex(current_index - 1)  # Scroll up
            elif event.angleDelta().y() < 0 and current_index < max_index:
                self.setCurrentIndex(current_index + 1)  # Scroll down

    def calculateTitleRect(self):
        # Calculate the height of each title item based on the index
        title_height = self.style().pixelMetric(self.style().PM_TitleBarHeight)  # Standard height for title bar

        # Create a rectangle for the title area of the current item
        return QRect(0, 0, self.width(), title_height)

    def createIcons(self):
        self.setItemIcon(0, QIcon('ui/UI Icons/Major/properties_panel.svg'))
        self.setItemIcon(1, QIcon('ui/UI Icons/Major/libraries_panel.svg'))
        self.setItemIcon(2, QIcon('ui/UI Icons/Major/characters_panel.svg'))
        self.setItemIcon(3, QIcon('ui/UI Icons/Major/image_trace_panel.svg'))
        self.setItemIcon(4, QIcon('ui/UI Icons/Major/canvas_panel.svg'))
        self.setItemIcon(5, QIcon('ui/UI Icons/Major/scene_panel.svg'))


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

            # Set a drag image to the list widget item
            pixmap = QPixmap(item.data(Qt.ItemDataRole.UserRole))

            # Create a transparent version of the pixmap by adjusting its opacity
            opacity = 0.5
            transparent_pixmap = pixmap.copy()
            painter = QPainter(transparent_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(transparent_pixmap.rect(), QColor(0, 0, 0, int(255 * opacity)))
            painter.end()

            drag.setPixmap(transparent_pixmap)

            # Center the drag pixmap at the cursor
            hotspot = QPoint(pixmap.width() // 2, pixmap.height() // 2)
            drag.setHotSpot(hotspot)

            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def filterItems(self, text):
        for item in self.all_items:
            item.setHidden(True)

            if text.lower() in item.text().lower():
                item.setHidden(False)


class CustomMenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        elif isinstance(menu, str):
            m = CustomMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m


class CustomMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(150, 30)
        self.radius = 10
        self.setObjectName('customMenu')

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = CustomMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def resizeEvent(self, event):
        path = QPainterPath()
        # the rectangle must be translated and adjusted by 1 pixel in order to
        # correctly map the rounded shape
        rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)
        # QRegion is bitmap based, so the returned QPolygonF (which uses float
        # values must be transformed to an integer based QPolygon
        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region)


class CustomSpinBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())

        self.spin = QSpinBox()
        self.lab = QLabel()

        self.layout().addWidget(self.lab)
        self.layout().addWidget(self.spin)
        self.layout().addStretch()

    def spinBox(self):
        return self.spin

    def label(self):
        return self.lab


class CustomSearchBox(QLineEdit):
    def __init__(self, actions: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setPlaceholderText('Search Actions...')

        self.available_actions = actions

        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(250)
        self.list_widget.setFixedHeight(100)
        self.list_widget.setObjectName('searchList')
        self.list_widget.setWindowFlag(Qt.ToolTip)

        # Connect the textChanged signal of the search input to the search method
        self.textEdited.connect(self.searchActions)
        self.list_widget.itemClicked.connect(self.performAction)

    def searchActions(self):
        self.list_widget.move(self.mapToGlobal(self.rect().bottomLeft()))
        self.list_widget.show()

        # Get the search text
        search_text = self.text().lower()

        # Clear the QListWidget
        self.list_widget.clear()

        # Filter actions based on search text and add them back to the QListWidget
        filtered_actions = [action for action in self.available_actions if search_text in action.lower()]

        if filtered_actions:
            self.list_widget.addItems(filtered_actions)

        else:
            self.list_widget.hide()

    def performAction(self, item):
        action_name = item.text()
        widget = self.available_actions.get(action_name)
        if widget:
            # Example action: toggling visibility of the widget
            if isinstance(widget, QAction):
                widget.trigger()

            elif isinstance(widget, (QPushButton, QCheckBox, CustomColorDisplayButton)):
                if widget.isCheckable():
                    if widget.isChecked():
                        widget.setChecked(False)
                        widget.click()

                    else:
                        widget.click()

                else:
                    widget.click()

            elif isinstance(widget, (QSpinBox, QDoubleSpinBox, QComboBox)):
                widget.setFocus(Qt.FocusReason.MouseFocusReason)

            self.list_widget.close()
            self.clearFocus()
            self.setText('')

    def focusOutEvent(self, event):
        self.list_widget.close()
        self.clearFocus()
        self.setText('')
        super().focusOutEvent(event)
