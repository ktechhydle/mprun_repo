from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

class CustomGraphicsItemGroup(QGraphicsItemGroup):
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.mouse_offset = QPoint(0, 0)
        self.block_size = 10
        self.widget = widget

    def paint(self, painter, option, widget=None):
        # Call the parent class paint method first
        super().paint(painter, option, widget)

        # If the item is selected, draw a custom selection highlight
        if option.state & QStyle.State_Selected:
            pen = painter.pen()
            pen.setColor(QColor("#e00202"))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
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
                # Call the superclass's mouseMoveEvent to move the item as normal
                super().mouseMoveEvent(event)

        else:
            # Call the superclass's mouseMoveEvent to move the item as normal
            super().mouseMoveEvent(event)

class EditableTextBlock(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Editable Text Block')

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.setFocus(Qt.MouseFocusReason)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas, button, button2):
        super().__init__()
        self.setMouseTracking(True)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.button = button
        self.button2 = button2
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None

    def update_pen(self, pen):
        self.pen = pen

    def mousePressEvent(self, event):
        if self.button.isChecked():
            self.button2.setChecked(False)

            if event.button() == Qt.LeftButton:
                self.path = QPainterPath()  # Create a new QPainterPath
                self.path.moveTo(self.mapToScene(event.pos()))
                self.last_point = event.pos()
                self.setDragMode(QGraphicsView.NoDrag)

        elif self.button2.isChecked():
            self.button.setChecked(False)

            if event.button() == Qt.LeftButton:
                self.path2 = QPainterPath()  # Create a new QPainterPath
                self.path2.moveTo(self.mapToScene(event.pos()))
                self.setDragMode(QGraphicsView.NoDrag)

                self.text = EditableTextBlock('An Editable Text Block')
                self.text.setPos(self.mapToScene(event.pos()))
                self.text.setDefaultTextColor(QColor('black'))
                self.text.setToolTip("Partially locked text block (This item's position is determined by the position of another element)")

                self.rect = QGraphicsRectItem(self.text.boundingRect())
                self.rect.setPen(self.pen)
                self.rect.setPos(self.mapToScene(event.pos()))

                self.canvas.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.button.isChecked():
            if event.buttons() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()
                self.last_point = event.pos()

                if self.temp_path_item:
                    self.canvas.removeItem(self.temp_path_item)

                # Load path as QGraphicsItem
                self.temp_path_item = QGraphicsPathItem(self.path)
                self.temp_path_item.setPen(self.pen)
                self.temp_path_item.setZValue(2)

                self.canvas.addItem(self.temp_path_item)

                self.canvas.update()

        elif self.button2.isChecked():
            if event.button() == Qt.LeftButton:
                self.path2.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.button.isChecked():
            if event.button() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))

                if self.temp_path_item:
                    self.canvas.removeItem(self.temp_path_item)

                self.canvas.update()

                # Load path as QGraphicsItem
                path_item = QGraphicsPathItem(self.path)
                path_item.setPen(self.pen)
                path_item.setZValue(2)

                # Add item
                self.canvas.addItem(path_item)

                # Set Flags
                path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                path_item.setFlag(QGraphicsItem.ItemIsMovable)

                # Set Tooltop
                path_item.setToolTip('MPRUN Path Element')

                # Check if item is selected or moved so we can turn tool off
                if self.canvas.selectedItems():
                    self.button.setChecked(False)
                    self.setDragMode(QGraphicsView.RubberBandDrag)

        elif self.button2.isChecked():
            if event.button() == Qt.LeftButton:
                self.path2.lineTo(self.mapToScene(event.pos()))
                self.canvas.update()

                # Draw circle at the end
                scene_pos = self.mapToScene(event.pos())
                circle = QGraphicsEllipseItem(scene_pos.x() - 3, scene_pos.y() - 3, 6, 6)
                circle.setZValue(2)
                circle.setPen(self.pen)

                self.canvas.update()

                # Load path as QGraphicsItem, set parent items
                path_item = QGraphicsPathItem(self.path2)
                path_item.setPen(self.pen)
                path_item.setZValue(2)
                circle.setParentItem(path_item)
                self.text.setParentItem(circle)
                self.rect.setParentItem(circle)

                # Add items
                self.canvas.addItem(path_item)

                # Set Flags
                path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                path_item.setFlag(QGraphicsItem.ItemIsMovable)
                circle.setFlag(QGraphicsItem.ItemIsSelectable)
                self.text.setFlag(QGraphicsItem.ItemIsSelectable)

                # Set Tooltips
                path_item.setToolTip('Leader Line Element')
                circle.setToolTip('Leader Line End Element')

                # Check if item is selected or moved so we can turn tool off
                if self.canvas.selectedItems():
                    self.button2.setChecked(False)
                    self.setDragMode(QGraphicsView.RubberBandDrag)

        super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event):
        # Handle trackpad zoom events
        if event.angleDelta().y() > 0:
            self.scale(1.1, 1.1)
        elif event.angleDelta().y() < 0:
            self.scale(0.9, 0.9)

        super().wheelEvent(event)
        
    def fitInView(self, scale=True):
        rect = QRectF(self.canvas.rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
            self.scale(factor, factor)
        
    def set_grid_size(self, size):
        self.block_size = size