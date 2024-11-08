import os.path
import sys
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
        menu.setAnimationEnabled(True)

        help_action = QAction(self.style().standardIcon(self.style().SP_MessageBoxQuestion), '&Help', self)

        if isinstance(self.parent(), QMainWindow):
            help_action.triggered.connect(self.parent().show_help)

        else:
            return

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
        self.menu.setAnimationEnabled(True)

        self.stroke_style_options = {'Solid Stroke': Qt.SolidLine,
                                     'Dotted Stroke': Qt.DotLine,
                                     'Dashed Stroke': Qt.DashLine,
                                     'Dashed Dot Stroke': Qt.DashDotLine,
                                     'Dashed Double Dot Stroke': Qt.DashDotDotLine}
        self.stroke_style_combo = QComboBox(self)
        self.stroke_style_combo.setStyleSheet('text-decoration: none;')
        for style, value in self.stroke_style_options.items():
            self.stroke_style_combo.addItem(style, value)

        self.stroke_style_combo.setItemData(0, QPixmap('mprun_assets/assets/ui/combobox/solid_stroke.png'),
                                            Qt.DecorationRole)
        self.stroke_style_combo.setItemData(1, QPixmap('mprun_assets/assets/ui/combobox/dotted_stroke.png'),
                                            Qt.DecorationRole)
        self.stroke_style_combo.setItemData(2, QPixmap('mprun_assets/assets/ui/combobox/dashed_stroke.png'),
                                            Qt.DecorationRole)
        self.stroke_style_combo.setItemData(3, QPixmap(
            'mprun_assets/assets/ui/combobox/dashed_dotted_stroke.png'), Qt.DecorationRole)
        self.stroke_style_combo.setItemData(4, QPixmap(
            'mprun_assets/assets/ui/combobox/dashed_dot_dot_stroke.png'), Qt.DecorationRole)
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
                                             QIcon('mprun_assets/assets/ui/combobox/projecting_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(1,
                                             QIcon('mprun_assets/assets/ui/combobox/flat_cap.svg'),
                                             Qt.DecorationRole)
        self.stroke_pencap_combo.setItemData(2,
                                             QIcon('mprun_assets/assets/ui/combobox/round_cap.svg'),
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

        self.join_style_combo.setItemData(0, QIcon('mprun_assets/assets/ui/combobox/bevel_join.png'), Qt.DecorationRole)
        self.join_style_combo.setItemData(1, QIcon('mprun_assets/assets/ui/combobox/round_join.png'), Qt.DecorationRole)
        self.join_style_combo.setItemData(2, QIcon('mprun_assets/assets/ui/combobox/miter_join.png'), Qt.DecorationRole)

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

        self.menu.exec(QPoint(x, y))


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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.paint()

    def paint(self):
        self.close_btn = QPushButton('', self)
        self.close_btn.setToolTip('Close')
        self.close_btn.setIcon(QIcon('mp_software_stylesheets/assets/cross.svg'))
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setObjectName('noneBorderedButton')
        self.close_btn.setFixedSize(QSize(18, 18))

        self.title_bar = QWidget(self)
        self.title_bar.setObjectName('dockWidgetTitleBar')
        self.title_bar.setFixedHeight(25)
        self.title_bar.setLayout(QHBoxLayout())
        self.title_bar.layout().addStretch()
        self.title_bar.layout().addWidget(self.close_btn)
        self.title_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.title_bar.layout().setSpacing(0)

        self.setTitleBarWidget(self.title_bar)


class CustomButton(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setFixedHeight(27)

        self._text = text

    def paintEvent(self, event):
        super().paintEvent(event)

        pixmap = QPixmap('mp_software_stylesheets/assets/triangle-right.svg')

        if self.isChecked():
            transform = QTransform()
            transform.rotate(90)
            pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        padding_x = 30
        padding_y = 18
        new_pos = QPoint(padding_x, padding_y)

        painter = QPainter(self)
        painter.begin(self)
        painter.drawPixmap(QRect(0, -2, 30, 30), pixmap, pixmap.rect())
        painter.drawText(new_pos, self._text)
        painter.end()

    def mousePressEvent(self, event):
        # Check if the mouse is within the top 30 pixels of the button
        if event.y() < 30:
            super().mousePressEvent(event)

    def setFixedHeight(self, h):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)

        start_geometry = self.geometry()
        end_geometry = self.geometry()
        end_geometry.setHeight(h)

        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)

        self.animation.valueChanged.connect(lambda: super(CustomButton, self).setFixedHeight(
            self.animation.currentValue().height()))

        self.animation.start()

    def restoreSize(self):
        self.setFixedHeight(27)


class CustomToolbox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.horizontalScrollBar().setEnabled(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName('customScrollArea')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self)

        self._control_parent = parent
        self._buttons = []

    def contextMenuEvent(self, event: QContextMenuEvent):
        # Create a custom context menu
        menu = CustomMenu(self)
        menu.setAnimationEnabled(True)

        collapse_all_action = QAction('&Collapse All', self)
        collapse_all_action.triggered.connect(self.collapseAll)
        expand_all_action = QAction('&Expand All', self)
        expand_all_action.triggered.connect(self.expandAll)
        help_action = QAction(self.style().standardIcon(self.style().SP_MessageBoxQuestion), '&Help', self)
        help_action.triggered.connect(self.controlParent().show_help)

        menu.addAction(collapse_all_action)
        menu.addAction(expand_all_action)
        menu.addSeparator()
        menu.addAction(help_action)

        menu.exec(event.globalPos())

    def addItem(self, widget: QWidget, text: str, icon: QIcon = None):
        button = CustomButton(text)
        button.setObjectName('panelTitle')
        button.setCheckable(True)
        button.widget = widget
        button.widget.setVisible(False)
        button.clicked.connect(lambda: self.toggleWidget(button))

        button.setLayout(QVBoxLayout())
        button.layout().setContentsMargins(0, 30, 0, 0)
        button.layout().addWidget(button.widget)

        if icon:
            button.setIcon(icon)

        self._buttons.append(button)
        self.layout().insertWidget(0, button)

    def collapseAll(self):
        for button in self.buttons():
            button.setChecked(False)
            self.toggleWidget(button)

    def expandAll(self):
        for button in self.buttons():
            button.setChecked(True)
            self.toggleWidget(button)

    def toggleWidget(self, button: CustomButton):
        if button.isChecked():
            if not button.widget.isVisible():
                button.widget.setVisible(True)
                if not hasattr(button, 'expandedHeight'):
                    button.expandedHeight = button.widget.height() + button.height() + (
                        button.height() if sys.platform == 'darwin' else 0)
                button.setFixedHeight(button.expandedHeight)
                self.scroll_area.ensureWidgetVisible(button.widget)
        else:
            button.widget.setVisible(False)
            button.restoreSize()

    def buttons(self) -> list[QPushButton]:
        return self._buttons

    def setCurrentWidget(self, widget: QWidget):
        self.collapseAll()

        for button in self.buttons():
            if button.widget == widget:
                button.setChecked(True)
                self.toggleWidget(button)

    def setCurrentIndex(self, index: int):
        self.buttons()[index].setChecked(True)
        self.toggleWidget(self.buttons()[index])

    def controlParent(self) -> QWidget:
        return self._control_parent


class CustomListWidget(QListWidget):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setIconSize(QSize(80, 80))
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setSelectionMode(QListWidget.SelectionMode.ContiguousSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self.addItemToScene)

        self.scene = scene
        self.current_size = 'medium'
        self.all_items = []

    def contextMenuEvent(self, event: QContextMenuEvent):
        # Create a custom context menu
        menu = CustomMenu(self)
        menu.setAnimationEnabled(True)

        refresh_action = QAction('Refresh Library', self)
        refresh_action.triggered.connect(self.parent().reloadLibrary)
        menu.addAction(refresh_action)

        tiny_action = QAction('&Tiny', self)
        tiny_action.setCheckable(True)
        tiny_action.triggered.connect(lambda: self.setDisplaySize('tiny'))
        small_action = QAction('&Small', self)
        small_action.setCheckable(True)
        small_action.triggered.connect(lambda: self.setDisplaySize('small'))
        medium_action = QAction('&Medium', self)
        medium_action.setCheckable(True)
        medium_action.triggered.connect(lambda: self.setDisplaySize('medium'))
        big_action = QAction('&Big', self)
        big_action.setCheckable(True)
        big_action.triggered.connect(lambda: self.setDisplaySize('big'))
        large_action = QAction('&Large', self)
        large_action.setCheckable(True)
        large_action.triggered.connect(lambda: self.setDisplaySize('large'))

        icon_size_menu = menu.addMenu('Display Size')
        icon_size_menu.addAction(tiny_action)
        icon_size_menu.addAction(small_action)
        icon_size_menu.addAction(medium_action)
        icon_size_menu.addAction(big_action)
        icon_size_menu.addAction(large_action)
        action_group = QActionGroup(self)
        action_group.addAction(tiny_action)
        action_group.addAction(small_action)
        action_group.addAction(medium_action)
        action_group.addAction(big_action)
        action_group.addAction(large_action)

        if self.current_size == 'tiny':
            tiny_action.setChecked(True)
        elif self.current_size == 'small':
            small_action.setChecked(True)
        elif self.current_size == 'medium':
            medium_action.setChecked(True)
        elif self.current_size == 'big':
            big_action.setChecked(True)
        elif self.current_size == 'large':
            large_action.setChecked(True)

        menu.exec(event.globalPos())

    def setDisplaySize(self, size: str):
        for item in self.all_items:
            if size == 'tiny':
                item.setSizeHint(QSize(60, 60))
                self.setIconSize(QSize(40, 40))

            elif size == 'small':
                item.setSizeHint(QSize(90, 90))
                self.setIconSize(QSize(70, 70))

            elif size == 'medium':
                item.setSizeHint(QSize(120, 120))
                self.setIconSize(QSize(100, 100))

            elif size == 'big':
                item.setSizeHint(QSize(150, 150))
                self.setIconSize(QSize(130, 130))

            else:
                item.setSizeHint(QSize(180, 180))
                self.setIconSize(QSize(160, 160))

        self.current_size = size

    def currentDisplaySize(self):
        return self.current_size

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

    def addItemToScene(self, item: QListWidgetItem):
        file = item.data(Qt.ItemDataRole.UserRole)

        if os.path.exists(file):
            if file.endswith('.svg'):
                item = CustomSvgItem(file)
                item.store_filename(file)
                item.store_filename(os.path.abspath(file))
                item.setToolTip('Imported SVG')

            else:
                pixmap = QPixmap(file)
                item = CustomPixmapItem(pixmap)
                item.store_filename(os.path.abspath(file))
                item.setToolTip('Imported Bitmap')

            # Set default attributes
            item.setPos(0, 0)
            item.setZValue(0)
            item.setFlags(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

            # Add item to scene
            add_command = AddItemCommand(self.scene, item)
            self.scene.addCommand(add_command)


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

    def contextMenuEvent(self, event):
        menu = CustomMenu(self)
        menu.setAnimationEnabled(True)

        for dock in self.parent().findChildren(QDockWidget, options=Qt.FindChildOption.FindChildrenRecursively):
            action = QAction(dock.windowTitle(), self)
            action.dock = dock
            action.setCheckable(True)
            action.setChecked(dock.isVisible())

            # Bind the current value of dock using a default argument
            action.triggered.connect(lambda checked, d=dock: self.toggleDock(d))
            menu.addAction(action)

        help_action = QAction(self.style().standardIcon(self.style().SP_MessageBoxQuestion), '&Help', self)
        help_action.triggered.connect(self.parent().show_help)

        menu.addSeparator()
        menu.addAction(help_action)

        menu.exec(event.globalPos())

    def toggleDock(self, dock: QDockWidget):
        if dock.isVisible():
            dock.setHidden(True)
            return

        dock.setHidden(False)


class CustomMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(150, 30)
        self.radius = 10
        self._animation_enabled = False

        if not sys.platform == 'darwin':
            self.setObjectName('customMenu')

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = CustomMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def resizeEvent(self, event):
        if not sys.platform == 'darwin':
            path = QPainterPath()
            rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
            path.addRoundedRect(rect, self.radius, self.radius)

            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(0, 0, 0, 200))  # Set the color
            self.setPalette(palette)

            region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
            self.setMask(region)

    def exec(self, pos=None):
        if pos and self.animationEnabled():
            screen_rect = QApplication.primaryScreen().availableGeometry()

            # Get the menu's size (this is available after it's created)
            menu_size = self.sizeHint()

            # Check if the menu would go off the right or bottom of the screen
            if pos.x() + menu_size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - menu_size.width())
            if pos.y() + menu_size.height() > screen_rect.bottom():
                pos.setY(screen_rect.bottom() - menu_size.height())

            # If animation is enabled
            self.animation = QPropertyAnimation(self, b'pos')
            self.animation.setDuration(100)
            self.animation.setStartValue(QPoint(pos.x(), pos.y() + 10))
            self.animation.setEndValue(pos)

            self.animation.start()

        super().exec(pos)

    def setAnimationEnabled(self, enabled: bool):
        self._animation_enabled = enabled

    def animationEnabled(self):
        return self._animation_enabled


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
