from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from scipy.interpolate import splprep, splev
from skimage.measure import *
import numpy as np

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class EditTextCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text):
        super().__init__()
        self.item = item
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        self.item.setPlainText(self.new_text)

    def undo(self):
        self.item.setPlainText(self.old_text)

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
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#ff0d00"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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
        # Create a new instance of CustomGraphicsItemGroup
        items = CustomGraphicsItemGroup(self.widget)

        # Set position, scale, and rotation
        items.setPos(self.pos().x() + 10, self.pos().y() + 10)
        items.setScale(self.scale())
        items.setRotation(self.rotation())

        # Set flags and tooltip
        items.setFlag(QGraphicsItem.ItemIsSelectable)
        items.setFlag(QGraphicsItem.ItemIsMovable)
        items.setToolTip('Duplicated MPRUN Element')

        # Add the new item to the scene
        add_command = AddItemCommand(self.scene(), items)
        self.scene().addCommand(add_command)

class CustomRectangleItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#009ceb"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

class CustomCircleItem(QGraphicsEllipseItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#009ceb"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

class CustomPathItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#009ceb"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

    def smooth_path(self, path):
        vertices = [(point.x(), point.y()) for point in path.toSubpathPolygons()[0]]
        x, y = zip(*vertices)
        tck, u = splprep([x, y], s=0)
        smooth_x, smooth_y = splev(np.linspace(0, 1, len(vertices) * 2), tck)  # Reduce the granularity

        smoothed_vertices = np.column_stack((smooth_x, smooth_y))
        simplified_vertices = approximate_polygon(smoothed_vertices, tolerance=2.5)  # Adjust the tolerance as needed

        smooth_path = QPainterPath()
        smooth_path.moveTo(simplified_vertices[0][0], simplified_vertices[0][1])

        for i in range(1, len(simplified_vertices) - 2, 3):
            smooth_path.cubicTo(
                simplified_vertices[i][0], simplified_vertices[i][1],
                simplified_vertices[i + 1][0], simplified_vertices[i + 1][1],
                simplified_vertices[i + 2][0], simplified_vertices[i + 2][1]
            )

        return smooth_path

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
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#009ceb"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

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
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#009ceb"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

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

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

class EditableTextBlock(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Editable Text Block')

        self.locked = False
        self.old_text = self.toPlainText()

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
            self.custom_pen = painter.pen()
            self.custom_pen.setWidth(8)
            self.custom_pen.setStyle(Qt.SolidLine)
            self.custom_pen.setCapStyle(Qt.FlatCap)
            self.custom_pen.setColor(QColor("#009ceb"))
            painter.setPen(self.custom_pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)

            if self.custom_pen.width() > 8:
                self.custom_pen.setWidth(8)

    def focusOutEvent(self, event):
        new_text = self.toPlainText()
        if self.old_text != new_text:
            edit_command = EditTextCommand(self, self.old_text, new_text)
            self.scene().addCommand(edit_command)
            self.old_text = new_text

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def set_locked(self):
        self.locked = True

    def duplicate(self):
        item = EditableTextBlock()
        item.setFont(self.font())
        item.setDefaultTextColor(self.defaultTextColor())
        item.setPlainText(self.toPlainText())
        item.setPos(self.pos().x() + 10, self.pos().y() + 10)
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Duplicated MPRUN Element')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

    def insert_table(self, rows, cols):
        cursor = self.textCursor()

        # Set the format for the table
        tableFormat = QTextTableFormat()
        tableFormat.setAlignment(Qt.AlignCenter)  # Set alignment of the table
        tableFormat.setBorderStyle(QTextTableFormat.BorderStyle_Solid)  # Set border style
        tableFormat.setBorderBrush(Qt.gray)  # Set border color
        tableFormat.setWidth(275)  # Set width of the table

        # Apply the table format to the current cursor position
        cursor.insertTable(rows, cols, tableFormat)

        # Move cursor to the beginning of the table
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor)

        # Insert header
        cursor.insertText("Trick Name")
        cursor.movePosition(QTextCursor.NextCell)
        cursor.insertText("Feature")
        cursor.movePosition(QTextCursor.NextCell)
        cursor.insertText("Score")

        self.setTextCursor(cursor)

class CanvasItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setWidth(8)
            pen.setStyle(Qt.SolidLine)
            pen.setCapStyle(Qt.FlatCap)
            pen.setColor(QColor("#d66b00"))
            painter.setPen(pen)
            painter.drawRoundedRect(self.boundingRect(), 5, 5)
