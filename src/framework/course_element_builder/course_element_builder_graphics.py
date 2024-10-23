from src.framework.undo_commands import *
from src.scripts.imports import *


class CourseElementBuilderScene(QGraphicsScene):
    itemsMoved = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

        self.undo_stack = QUndoStack()
        self.undo_stack.setUndoLimit(200)

        self.oldPositions = {}
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemsMoved.connect(self.onItemMoved)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.oldPositions = {i: i.pos() for i in self.selectedItems()}

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self.oldPositions:
            newPositions = {i: i.pos() for i in self.oldPositions.keys()}
            if any(self.oldPositions[i] != newPositions[i] for i in self.oldPositions.keys()):
                self.itemsMoved.emit(self.oldPositions, newPositions)
            self.oldPositions = {}

    def onItemMoved(self, oldPositions, newPositions):
        self.addCommand(ItemMovedUndoCommand(oldPositions, newPositions))

    def addCommand(self, command: QUndoCommand):
        self.undo_stack.push(command)

        print(f'Command At: {command}')

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    def selectedItemsSceneBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        return bounding_rect


class CourseElementBuilderView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        self.setMouseTracking(True)

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [4, 50]  # furthest you can zoom out, closest you can zoom in
        self.isPanning = False

    def mousePressEvent(self, event):
        if self.parent().pan_btn.isChecked():
            self.onPanStart(event)
            self.disableItemFlags()
            super().mousePressEvent(event)

        elif event.button() == Qt.MiddleButton:
            self.onPanStart(event)

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.parent().pan_btn.isChecked():
            self.onPanEnd(event)
            super().mouseReleaseEvent(event)

        elif event.button() == Qt.MiddleButton:
            self.onPanEnd(event)
            if self.parent().select_btn.isChecked():
                self.parent().useSelect()

        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Calculate zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        # Deal with clamping!
        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

    def disableItemFlags(self):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

    def onPanStart(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.disableItemFlags()
        self.isPanning = True
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def onPanEnd(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.isPanning = False
