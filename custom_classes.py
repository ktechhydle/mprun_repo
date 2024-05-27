from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from PyQt5.Qt import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from scipy.interpolate import splprep, splev
from scipy.signal import savgol_filter
from skimage.measure import *
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from undo_commands import *
import numpy as np

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
        group = CustomGraphicsItemGroup(self.widget)

        # Set position, scale, and rotation
        group.setPos(self.pos())
        group.setScale(self.scale())
        group.setRotation(self.rotation())
        group.set_grid_size(self.block_size)

        # Set flags and tooltip
        group.setFlag(QGraphicsItem.ItemIsSelectable)
        group.setFlag(QGraphicsItem.ItemIsMovable)
        group.setToolTip('Group')

        # Add the new item to the scene
        add_command = AddItemCommand(self.scene(), group)
        self.scene().addCommand(add_command)

        for items in self.childItems():
            copy = items.duplicate()

            # Add items to group
            group.addToGroup(copy)

        return group

class CustomRectangleItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def duplicate(self):
        rect = self.rect()

        item = CustomRectangleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Rectangle')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CustomCircleItem(QGraphicsEllipseItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def duplicate(self):
        rect = self.rect()

        item = CustomCircleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Ellipse')

        if self.childItems():
            for child in self.childItems():
                copy = child.duplicate()

                if isinstance(copy, EditableTextBlock):
                    pass

                else:
                    copy.setFlag(QGraphicsItem.ItemIsMovable, False)
                    copy.setFlag(QGraphicsItem.ItemIsSelectable, False)

                copy.setParentItem(item)

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CustomPathItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

        path.setFillRule(Qt.FillRule.WindingFill)

        self.smooth = False

        self.text_items = []
        self.add_text = False
        self.text_along_path = ''
        self.text_along_path_font = QFont('Arial', 20)
        self.text_along_path_color = QColor('black')
        self.text_along_path_spacing = 3
        self.start_text_from_beginning = False

    def duplicate(self):
        path = self.path()

        item = CustomPathItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Path')

        if self.add_text == True:
            item.add_text = True
            item.setTextAlongPathFromBeginning(True if self.start_text_from_beginning else False)
            item.setTextAlongPath(self.text_along_path)
            item.setTextAlongPathSpacingFromPath(self.text_along_path_spacing)
            item.setTextAlongPathFont(self.text_along_path_font)
            item.setTextAlongPathColor(self.text_along_path_color)

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def smooth_path(self, path, tolerance: float):
        vertices = [(point.x(), point.y()) for point in path.toSubpathPolygons()[0]]
        x, y = zip(*vertices)

        wl = 21
        po = 3

        # Apply Savitzky-Golay filter for smoothing
        smooth_x = savgol_filter(x, window_length=wl, polyorder=po)
        smooth_y = savgol_filter(y, window_length=wl, polyorder=po)

        smoothed_vertices = np.column_stack((smooth_x, smooth_y))
        simplified_vertices = approximate_polygon(smoothed_vertices, tolerance=tolerance)

        smooth_path = QPainterPath()
        smooth_path.moveTo(simplified_vertices[0][0], simplified_vertices[0][1])

        for i in range(1, len(simplified_vertices) - 2, 3):
            smooth_path.cubicTo(
                simplified_vertices[i][0], simplified_vertices[i][1],
                simplified_vertices[i + 1][0], simplified_vertices[i + 1][1],
                simplified_vertices[i + 2][0], simplified_vertices[i + 2][1]
            )

        self.smooth = True

        return smooth_path

    def setTextAlongPathFromBeginning(self, a0):
        self.start_text_from_beginning = a0

    def setTextAlongPath(self, text):
        self.text_along_path = text
        self.update()

    def setTextAlongPathFont(self, font):
        self.text_along_path_font = font
        self.update()

    def setTextAlongPathColor(self, color):
        self.text_along_path_color = color
        self.update()

    def setTextAlongPathSpacingFromPath(self, spacing):
        self.text_along_path_spacing = spacing
        self.update()

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        if self.add_text == True:
            path = self.path()
            hw = self.text_along_path
            drawWidth = self.text_along_path_spacing
            pen = painter.pen()
            pen.setWidth(drawWidth)
            pen.setColor(self.text_along_path_color)
            painter.setPen(pen)
            font = self.text_along_path_font
            painter.setFont(font)

            if self.start_text_from_beginning == True:

                font_metrics = QFontMetricsF(font)
                total_length = path.length()

                current_length = 0

                for char in hw:
                    char_width = font_metrics.width(char)
                    percent = current_length / total_length
                    point = path.pointAtPercent(percent)
                    angle = path.angleAtPercent(percent)

                    painter.save()
                    painter.translate(point)
                    painter.rotate(-angle)
                    painter.drawText(QPointF(0, -pen.width()), char)
                    painter.restore()

                    current_length += char_width

            else:
                percentIncrease = 1 / (len(hw) + 1)
                percent = 0

                for i in range(len(hw)):
                    percent += percentIncrease
                    point = path.pointAtPercent(percent)
                    angle = path.angleAtPercent(percent)

                    painter.save()
                    painter.translate(point)
                    painter.rotate(-angle)
                    painter.drawText(QPointF(0, -pen.width()), hw[i])
                    painter.restore()

class CustomPixmapItem(QGraphicsPixmapItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return str(self.filename)

    def duplicate(self):
        pixmap = QPixmap(self.return_filename())

        item = CustomPixmapItem(pixmap)
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)
        item.store_filename(self.return_filename())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Imported Pixmap')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CustomSvgItem(QGraphicsSvgItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None
        self.render = QSvgRenderer(file)

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return str(self.filename)

    def duplicate(self):
        svg = self.return_filename()

        item = CustomSvgItem(svg)
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)
        item.store_filename(svg)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Imported SVG')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def mouseDoubleClickEvent(self, event):
        print('Logic not implemented')

class EditableTextBlock(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Text')
        self.locked = False
        self.old_text = self.toPlainText()

        self.setAcceptHoverEvents(True)

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

    def focusOutEvent(self, event):
        new_text = self.toPlainText()
        if self.old_text != new_text:
            if new_text == '':
                self.scene().removeItem(self)

            else:
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
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Text')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class LeaderLineItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        painter.setPen(self.pen())
        painter.setBrush(self.brush())

        if self.childItems():
            for child in self.childItems():
                # Map the child's bounding rect to the parent's coordinate system
                mapped_rect = self.mapRectFromItem(child, child.boundingRect())
                painter.drawRect(mapped_rect)

        try:
            painter.setPen(self.pen())
            painter.setBrush(QBrush(QColor(self.pen().color().name())))

            path = self.path()
            if path.elementCount() > 1:
                last_point = path.elementAt(path.elementCount() - 1)
                end_point = QPointF(last_point.x, last_point.y)
                # Drawing a 10x10 ellipse around the last point
                painter.drawEllipse(end_point, 5, 5)

        except Exception as e:
            print(e)

    def duplicate(self):
        path = self.path()

        item = LeaderLineItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Path')

        if self.childItems():
            for child in self.childItems():
                copy = child.duplicate()

                if isinstance(copy, EditableTextBlock):
                    pass

                else:
                    copy.setFlag(QGraphicsItem.ItemIsMovable, False)
                    copy.setFlag(QGraphicsItem.ItemIsSelectable, False)

                copy.setParentItem(item)

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CanvasItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, Qt.SolidLine)
        pen.setWidthF(0)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setBrush(brush)
        self.setPen(pen)

class CanvasTextItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent):
        super().__init__()

        self.setScale(1.5)
        self.setPos(parent.boundingRect().x(), parent.boundingRect().y())
        self.setParentItem(parent)
        self.setBrush(QBrush(QColor('black')))
        self.setText(text)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.setZValue(10000)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor('#dcdcdc')))
        painter.setPen(QPen(QColor('black')))
        painter.drawRect(self.boundingRect())

        super().paint(painter, option, widget)

class ControlPoint(QGraphicsEllipseItem):
    positionChanged = pyqtSignal()

    def __init__(self, x, y, parent=None):
        super().__init__(-5, -5, 10, 10, parent)
        self.setBrush(QBrush(Qt.blue))
        self.setPen(QPen(Qt.black))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.positionChanged.emit()
        return super().itemChange(change, value)

class WaterMarkItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)


