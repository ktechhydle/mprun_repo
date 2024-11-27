from src.framework.course_element_builder.course_element_builder_tools import LipTool, LineTool, ArcTool, RectTool
from src.framework.undo_commands import *
from src.scripts.imports import *
from mprun.constants import LEFT_BUTTON, MIDDLE_BUTTON, RIGHT_BUTTON, NO_BUTTON


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
        self.copy_stack = []

        self.oldPositions = {}
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemsMoved.connect(self.onItemMoved)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == LEFT_BUTTON:
            self.oldPositions = {i: i.pos() for i in self.selectedItems()}

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == LEFT_BUTTON and self.oldPositions:
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

    def copy(self):
        self.copy_stack.clear()

        for item in self.selectedItems():
            self.copy_stack.append(item.copy())

        self.views()[0].update()

    def cut(self):
        self.copy_stack.clear()

        cut_items = []

        for item in self.selectedItems():
            self.copy_stack.append(item.copy())
            cut_items.append(item)

        self.addCommand(RemoveItemCommand(self, cut_items))
        self.views()[0].update()

    def paste(self):
        new_items = []

        for item in self.copy_stack:
            new_items.append(item.copy())

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

        self.views()[0].update()

    def duplicate(self):
        new_items = []

        for item in self.selectedItems():
            new_items.append(item.copy())

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

        self.views()[0].update()


class CourseElementBuilderView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Tools
        self.lipTool = LipTool(self.scene(), self)
        self.rectTool = RectTool(self.scene(), self)
        self.lineTool = LineTool(self.scene(), self)
        self.arcTool = ArcTool(self.scene(), self)

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

        elif self.parent().lip_btn.isChecked():
            self.lipTool.mousePress(event)
            self.disableItemFlags()
            super().mousePressEvent(event)

        elif self.parent().rect_btn.isChecked():
            self.rectTool.mousePress(event)
            self.disableItemFlags()
            super().mousePressEvent(event)

        elif self.parent().line_btn.isChecked():
            self.disableItemFlags()
            self.lineTool.mousePress(event)
            super().mousePressEvent(event)

        elif self.parent().arc_btn.isChecked():
            self.disableItemFlags()
            self.arcTool.mousePress(event)
            super().mousePressEvent(event)

        else:
            super().mousePressEvent(event)

        if event.button() == MIDDLE_BUTTON:
            self.onPanStart(event)

    def mouseMoveEvent(self, event):
        if self.parent().lip_btn.isChecked():
            self.lipTool.mouseMove(event)
            self.lipTool.specialToolTip(event)
            super().mouseMoveEvent(event)

        elif self.parent().pan_btn.isChecked():
            self.disableItemFlags()
            super().mouseMoveEvent(event)

        elif self.parent().rect_btn.isChecked():
            self.disableItemFlags()
            self.rectTool.mouseMove(event)
            self.rectTool.specialToolTip(event)
            super().mouseMoveEvent(event)

        elif self.parent().line_btn.isChecked():
            self.disableItemFlags()
            self.lineTool.mouseMove(event)
            self.lineTool.specialToolTip(event)
            super().mouseMoveEvent(event)

        elif self.parent().arc_btn.isChecked():
            self.disableItemFlags()
            self.arcTool.mouseMove(event)
            self.arcTool.specialToolTip(event)
            super().mouseMoveEvent(event)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.parent().pan_btn.isChecked():
            self.onPanEnd(event)
            super().mouseReleaseEvent(event)

        elif self.parent().lip_btn.isChecked():
            self.lipTool.mouseRelease(event)
            super().mousePressEvent(event)

        elif self.parent().rect_btn.isChecked():
            self.rectTool.mouseRelease(event)
            super().mousePressEvent(event)

        elif self.parent().line_btn.isChecked():
            self.disableItemFlags()
            self.lineTool.mouseRelease(event)
            super().mouseReleaseEvent(event)

        elif self.parent().arc_btn.isChecked():
            self.disableItemFlags()
            self.arcTool.mouseRelease(event)
            super().mouseReleaseEvent(event)

        else:
            super().mouseReleaseEvent(event)

        if event.button() == MIDDLE_BUTTON:
            self.onPanEnd(event)
            if self.parent().select_btn.isChecked():
                self.parent().useSelect()

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

    def enableItemFlags(self):
        for item in self.scene().items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def onPanStart(self, event):
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   LEFT_BUTTON, NO_BUTTON, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.disableItemFlags()
        self.isPanning = True
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                LEFT_BUTTON, event.buttons() | LEFT_BUTTON, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def onPanEnd(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                LEFT_BUTTON, event.buttons() & ~LEFT_BUTTON, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.isPanning = False

    def escape(self):
        self.scene().clearSelection()
        self.lipTool.cancel()
        self.lineTool.cancel()
