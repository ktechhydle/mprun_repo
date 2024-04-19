from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

class item_stack:
    def __init__(self, initial_value=""):
        self._value = initial_value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

class CustomGraphicsItemGroup(QGraphicsItemGroup):
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.mouse_offset = QPoint(0, 0)
        self.block_size = 10
        self.widget = widget

        self.locked = False
        self.stored_items = None

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#ff0000"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.locked == False:
            if self.widget.isChecked():
                if self.isSelected():
                    # Calculate the position relative to the scene's coordinate system
                    scene_pos = event.scenePos()
                    x = (
                        int(scene_pos.x() / self.block_size) * self.block_size
                        - self.mouse_offset.x()
                    )
                    y = (
                        int(scene_pos.y() / self.block_size) * self.block_size
                        - self.mouse_offset.y()
                    )

                    # Set the position relative to the scene's coordinate system
                    self.setPos(x, y)
                else:
                    # Call the superclasses mouseMoveEvent to move the item as normal
                    super().mouseMoveEvent(event)

            else:
                # Call the superclasses mouseMoveEvent to move the item as normal
                super().mouseMoveEvent(event)
        else:
            # Call the superclasses mouseMoveEvent to move the item as normal
            super().mouseMoveEvent(event)
            
    def set_grid_size(self, size):
        self.block_size = size

    def set_locked(self):
        self.locked = True

    def set_unlocked(self):
        self.locked = False

    def store_items(self, items):
        self.stored_items = items

    def duplicate(self):
        item = CustomGraphicsItemGroup(self.widget)
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())

        self.scene().addItem(item)

        item.addToGroup(self.parentItem()) # I need help here)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

class CustomRectangleItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def duplicate(self):
        rect = self.rect()

        item = CustomRectangleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')


        self.scene().addItem(item)

class CustomCircleItem(QGraphicsEllipseItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def duplicate(self):
        rect = self.rect()

        item = CustomCircleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)

class CustomPathItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def duplicate(self):
        path = self.path()

        item = CustomPathItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)

    def duplicate_but_better(self):
        path = self.path()

        item = CustomPathItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)

class CustomPixmapItem(QGraphicsPixmapItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return str(self.filename)

    def duplicate(self):
        pixmap = QPixmap(self.return_filename())

        item = CustomPixmapItem(pixmap)
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)
        item.store_filename(self.return_filename())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)

class CustomSvgItem(QGraphicsSvgItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return str(self.filename)

    def duplicate(self):
        svg = self.return_filename()

        item = CustomSvgItem(svg)
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)
        item.store_filename(svg)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)

class EditableTextBlock(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Editable Text Block')

        self.locked = False

    def mouseDoubleClickEvent(self, event):
        if self.locked == False:
            if event.button() == Qt.LeftButton:
                self.setTextInteractionFlags(Qt.TextEditorInteraction)
                self.setFocus(Qt.MouseFocusReason)
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)

        else:
            super().mouseDoubleClickEvent(event)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.SquareCap)
            pen.setColor(QColor("#f06013"))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def set_locked(self):
        self.locked = True

    def duplicate(self):
        item = EditableTextBlock()
        item.setDefaultTextColor(self.defaultTextColor())
        item.setPlainText(self.toPlainText())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        self.scene().addItem(item)
