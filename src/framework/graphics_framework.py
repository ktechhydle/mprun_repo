import os.path
import mprun.gui
from mprun.constants import *
from src.framework.managers.export_manager import ExportManager
from src.framework.managers.file_manager import SceneFileManager
from src.framework.managers.import_manager import ImportManager
from src.framework.managers.template_manager import TemplateManager
from src.gui.app_screens import TipWin, ArrangeWin
from src.framework.tools import *
from src.scripts.app_internal import *
from src.scripts.imports import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class CustomViewport(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        format = QSurfaceFormat()
        format.setSamples(4)
        format.setRenderableType(QSurfaceFormat.OpenGL)
        self.setFormat(format)


class CustomGraphicsView(QGraphicsView):
    SelectTool = 0
    PanTool = 2
    PathTool = 3
    LabelTool = 4
    TextTool = 5
    SculptTool = 6
    CanvasTool = 7

    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.DontClipPainter, True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.installEventFilter(self)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.resizeEvent = self.parent().resizeEvent

        self.w = None
        self.current_drag_item = None
        self.current_tool = 0

        # Items
        self.canvas = canvas
        self.temp_path_item = None
        self.layer_height = None
        self.path = None
        self.last_point = None

        # Tools
        self.pathDrawingTool = PathDrawerTool(self.canvas, self)
        self.labelingTool = LineAndLabelTool(self.canvas, self)
        self.sculptingTool = PathSculptingTool(self.canvas, self)
        self.canvasTool = AddCanvasTool(self.canvas, self)

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [4, 50]  # furthest you can zoom out, closest you can zoom in
        self.isPanning = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.ContextMenu:
            self.contextMenuEvent(event)  # Check if this is triggered instead
            return True  # This prevents contextMenuEvent from being called
        return super().eventFilter(obj, event)

    def disable_item_flags(self):
        for item in self.canvas.items():
            if not isinstance(item, (CanvasItem, CanvasTextItem)):
                item.setFlag(ITEM_MOVABLE, False)
                item.setFlag(ITEM_SELECTABLE, False)

    def disable_item_movement(self):
        for item in self.canvas.items():
            if not isinstance(item, (CanvasItem, CanvasTextItem)):
                item.setFlag(ITEM_MOVABLE, False)

    def show_tooltip(self, event):
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        QToolTip.showText(p, f'''x: {int(self.mapToScene(point).x())} 
y: {int(self.mapToScene(point).y())}''')

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.currentTool() == CustomGraphicsView.PathTool:
            self.pathDrawingTool.mousePress(event)

        elif self.currentTool() == CustomGraphicsView.LabelTool:
            self.labelingTool.mousePress(event)
            self.disable_item_flags()

        elif self.currentTool() == CustomGraphicsView.TextTool:
            self.disable_item_flags()
            self.on_add_text(event)
            super().mousePressEvent(event)

        elif self.currentTool() == CustomGraphicsView.CanvasTool:
            self.canvasTool.mousePress(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.currentTool() == CustomGraphicsView.PanTool:
            self.on_pan_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.currentTool() == CustomGraphicsView.SculptTool:
            self.sculptingTool.mousePress(event)
            self.disable_item_flags()

        else:
            super().mousePressEvent(event)

        if event.button() == MIDDLE_BUTTON:
            self.on_pan_start(event)

        self.on_add_canvas_trigger()

    def mouseMoveEvent(self, event):
        if self.scene().selectedItems():
            self.update()

        if self.currentTool() == CustomGraphicsView.PathTool:
            self.pathDrawingTool.specialToolTip(event)
            self.pathDrawingTool.mouseMove(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.currentTool() == CustomGraphicsView.TextTool:
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

        elif self.currentTool() == CustomGraphicsView.LabelTool:
            self.show_tooltip(event)
            self.labelingTool.mouseMove(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.currentTool() == CustomGraphicsView.CanvasTool:
            self.canvasTool.specialToolTip(event)
            self.canvasTool.mouseMove(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.currentTool() == CustomGraphicsView.PanTool:
            self.show_tooltip(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.currentTool() == CustomGraphicsView.SculptTool:
            self.show_tooltip(event)
            self.sculptingTool.mouseMove(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        else:
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.currentTool() == CustomGraphicsView.PathTool:
            self.pathDrawingTool.mouseRelease(event)

        elif self.currentTool() == CustomGraphicsView.TextTool:
            super().mouseReleaseEvent(event)

        elif self.currentTool() == CustomGraphicsView.LabelTool:
            self.labelingTool.mouseRelease(event)
            super().mouseReleaseEvent(event)

        elif self.currentTool() == CustomGraphicsView.CanvasTool:
            self.canvasTool.mouseRelease(event)
            super().mouseReleaseEvent(event)

        elif self.currentTool() == CustomGraphicsView.PanTool:
            self.on_pan_end(event)
            super().mouseReleaseEvent(event)

        elif self.currentTool() == CustomGraphicsView.SculptTool:
            self.sculptingTool.mouseRelease(event)
            self.disable_item_flags()

        else:
            super().mouseReleaseEvent(event)

        if event.button() == MIDDLE_BUTTON:
            self.on_pan_end(event)
            if self.currentTool() == CustomGraphicsView.SelectTool:
                self.parent().use_select()

    def mouseDoubleClickEvent(self, event):
        if self.currentTool() == CustomGraphicsView.SculptTool:
            self.sculptingTool.mouseDoublePress(event)

        else:
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        # Create a custom context menu
        menu = mprun.gui.menu(self)
        menu.setAnimationEnabled(True)

        copy_action = QAction('&Copy', self)
        copy_action.triggered.connect(self.canvas.copy)
        cut_action = QAction('&Cut', self)
        cut_action.triggered.connect(self.canvas.cut)
        paste_action = QAction('&Paste', self)
        paste_action.triggered.connect(self.canvas.paste)
        duplicate_action = QAction('Duplicate', self)
        duplicate_action.triggered.connect(self.canvas.duplicate)
        raise_layer_action = QAction('Raise Layer', self)
        raise_layer_action.triggered.connect(self.canvas.parentWindow.use_raise_layer)
        lower_layer_action = QAction('Lower Layer', self)
        lower_layer_action.triggered.connect(self.canvas.parentWindow.use_lower_layer)
        bring_to_front_action = QAction('Bring to Front', self)
        bring_to_front_action.triggered.connect(self.canvas.parentWindow.use_bring_to_front)
        hide_action = QAction('Hide Selected', self)
        hide_action.triggered.connect(self.canvas.parentWindow.use_hide_item)
        unhide_action = QAction('Unhide All', self)
        unhide_action.triggered.connect(self.canvas.parentWindow.use_unhide_all)
        select_all_action = QAction('Select All', self)
        select_all_action.triggered.connect(self.canvas.parentWindow.use_select_all)
        select_above_action = QAction('Select Items Above', self)
        select_above_action.triggered.connect(self.canvas.selectAbove)
        select_below_action = QAction('Select Items Below', self)
        select_below_action.triggered.connect(self.canvas.selectBelow)
        select_colliding_action = QAction('Select Colliding Items', self)
        select_colliding_action.triggered.connect(self.canvas.selectColliding)
        help_action = QAction(self.style().standardIcon(self.style().SP_MessageBoxQuestion), '&Help', self)
        help_action.triggered.connect(self.canvas.parentWindow.show_help)

        menu.addAction(copy_action)
        menu.addAction(cut_action)
        menu.addAction(paste_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()
        menu.addAction(raise_layer_action)
        menu.addAction(lower_layer_action)
        menu.addSeparator()
        menu.addAction(hide_action)
        menu.addAction(unhide_action)
        menu.addSeparator()
        menu.addAction(select_all_action)
        menu.addAction(select_above_action)
        menu.addAction(select_below_action)
        menu.addSeparator()
        menu.addAction(help_action)

        if not self.canvas.selectedItems():
            for action in menu.actions():
                if not action.text().startswith((help_action.text(),
                                                 select_all_action.text(),
                                                 unhide_action.text())):
                    action.setDisabled(True)

        menu.exec(event.globalPos())

    def wheelEvent(self, event):
        if self.currentTool() == CustomGraphicsView.SculptTool and not self.isPanning:
            if self.sculptingTool.sculpting_item:
                if event.angleDelta().y() > 0:
                    self.sculptingTool.setSculptRadius(
                        self.sculptingTool.sculpt_radius + 5 if self.sculptingTool.sculpt_radius <= 1000 else 1000)
                else:
                    self.sculptingTool.setSculptRadius(
                        self.sculptingTool.sculpt_radius - 5 if self.sculptingTool.sculpt_radius >= 1 else 1)

                self.scene().parentWindow.scene_tab.sculpt_radius_spin.blockSignals(True)
                self.scene().parentWindow.scene_tab.sculpt_radius_spin.setValue(self.sculptingTool.sculpt_radius)
                self.scene().parentWindow.scene_tab.sculpt_radius_spin.blockSignals(False)

                self.sculptingTool.sculpt_shape.setPos(
                    self.mapToScene(event.pos()) - self.sculptingTool.sculpt_shape.boundingRect().center())
                return

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

        self.parent().scene_tab.zoom_widget.spinBox().blockSignals(True)
        self.parent().scene_tab.zoom_widget.spinBox().setValue(int(self.transform().m11() * 100))
        self.parent().scene_tab.zoom_widget.spinBox().blockSignals(False)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

            # Temporary item movement during drag
            if not self.current_drag_item:
                # Initialize the item based on the file type
                url = event.mimeData().urls()[0]  # Assume one file per drag
                self.current_drag_item = self.createTemporaryItem(url)

                if self.current_drag_item:
                    self.canvas.addItem(self.current_drag_item)

            if self.current_drag_item:
                # Update item position to follow cursor
                self.current_drag_item.setPos(
                    self.mapToScene(event.pos()) - self.current_drag_item.boundingRect().center()
                )

    def dropEvent(self, event):
        if not self.current_drag_item:
            return  # No item was created, abort

        # Finalize the item's position
        self.current_drag_item.setPos(
            self.mapToScene(event.pos()) - self.current_drag_item.boundingRect().center()
        )

        # Add the item via AddItemCommand
        add_command = AddItemCommand(self.canvas, self.current_drag_item)
        self.canvas.addCommand(add_command)

        self.current_drag_item = None  # Reset after drop

    def dragLeaveEvent(self, event):
        # Cleanup in case the drag is cancelled
        if self.current_drag_item:
            self.canvas.removeItem(self.current_drag_item)
            self.current_drag_item = None

    def fitInView(self, *args, **kwargs):
        super().fitInView(*args, **kwargs)
        self.applyZoom()

    def update(self):
        super().update()

        for item in self.scene().items():
            item.update()

            if hasattr(item, 'resize_orb'):
                item.resize_orb.updateOrb()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.update()

    def createTemporaryItem(self, url):
        """
        Create a temporary item based on the file type. Return None if not supported.
        """
        local_file = url.toLocalFile()
        if local_file.endswith('.svg'):
            item = CustomSvgItem(local_file)
            item.store_filename(os.path.abspath(local_file))
            item.setToolTip('Imported SVG')
        elif local_file.endswith(('.txt', '.csv')):
            with open(local_file, 'r') as f:
                item = CustomTextItem(f.read())
                item.setToolTip('Imported Text')
        else:
            pixmap = QPixmap(local_file)
            item = CustomPixmapItem(pixmap)
            item.store_filename(os.path.abspath(local_file))
            item.setToolTip('Imported Bitmap')

        # Set default attributes for the temporary item
        item.setFlags(ITEM_SELECTABLE | ITEM_MOVABLE)
        item.setZValue(0)
        return item

    def applyZoom(self):
        # Reset the transformation and apply the stored zoom level
        self.resetTransform()
        zoomFactor = self.zoomInFactor ** (self.zoom - 10)  # 15 is the initial zoom level
        self.scale(zoomFactor, zoomFactor)

    def showMessage(self, label: str, tip: str):
        if self.w is not None:
            self.w.close()

        self.w = TipWin(label, tip, self.parent())

        pos = self.mapToGlobal(self.rect().bottomLeft())
        posy = (pos.y() - self.w.height())

        self.w.move(pos.x() + TIP_WINDOW_X_PADDING, posy + TIP_WINDOW_Y_PADDING)

    def updateTip(self):
        try:
            pos = self.mapToGlobal(self.rect().bottomLeft())
            posy = (pos.y() - self.w.height())

            self.w.move(pos.x() + TIP_WINDOW_X_PADDING, posy + TIP_WINDOW_Y_PADDING)
        except:
            pass

    def currentTool(self):
        return self.current_tool

    def setCurrentTool(self, tool: int):
        self.current_tool = tool

    def on_add_text(self, event):
        if event.button() == LEFT_BUTTON:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            i = self.scene().itemAt(self.mapToScene(event.pos()), self.transform())

            if i and isinstance(i, CustomTextItem):
                i.setEditing()
                return

            else:
                for item in self.canvas.items():
                    if isinstance(item, CustomTextItem):
                        if item.hasFocus():
                            item.clearFocus()
                            return

                pos = self.mapToScene(event.pos())

                self.text = CustomTextItem('Lorem Ipsum')
                self.text.setFont(self.parent().characters_tab.getFont())
                self.text.setDefaultTextColor(self.parent().characters_tab.getFontColor())
                self.text.setTextAlignment(self.parent().characters_tab.getFontAlignment())

                add_command = AddItemCommand(self.canvas, self.text)
                self.canvas.addCommand(add_command)

                self.text.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                self.text.setZValue(0)
                self.text.setPos(pos)
                self.text.selectTextAndSetCursor()

    def on_add_canvas_trigger(self):
        if self.currentTool() == CustomGraphicsView.CanvasTool:
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(True)

        elif not self.currentTool() == CustomGraphicsView.CanvasTool:
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(False)

    def on_pan_start(self, event):
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   LEFT_BUTTON, NO_BUTTON, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.disable_item_flags()
        self.isPanning = True
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                LEFT_BUTTON, event.buttons() | LEFT_BUTTON, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def on_pan_end(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                LEFT_BUTTON, event.buttons() & ~LEFT_BUTTON, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.isPanning = False


class CustomGraphicsScene(QGraphicsScene):
    itemsMoved = pyqtSignal(object, object)

    def __init__(self, undoStack):
        super().__init__()
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.BspTreeIndex)

        self.file_name = None
        self.mpversion = open('internal data/_version.txt', 'r').read()
        self.canvas_count = 2
        self.undo_stack = undoStack
        self.copy_stack = []
        self.modified = False
        self.parentWindow = None

        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

        # Item Movement
        self.oldPositions = {}
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemsMoved.connect(self.onItemMoved)

        # Managers
        self.manager = SceneFileManager(self)
        self.template_manager = TemplateManager(self)
        self.importManager = ImportManager(self)
        self.exportManager = ExportManager(self)

    def setParentWindow(self, parent: QMainWindow):
        self.parentWindow = parent

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

    def clearSelection(self):
        super().clearSelection()
        self.update()

    def update(self, rect=None):
        super().update()

        for item in self.items():
            item.update()

    def onItemMoved(self, oldPositions, newPositions):
        self.addCommand(ItemMovedUndoCommand(oldPositions, newPositions))

    def undo(self):
        if self.undo_stack.canUndo():
            self.undo_stack.undo()
            self.modified = True
            self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        self.parentWindow.properties_tab.updateTransformUi()
        self.parentWindow.update_appearance_ui()
        self.views()[0].update()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def redo(self):
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
            self.modified = True
            self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        self.parentWindow.properties_tab.updateTransformUi()
        self.parentWindow.update_appearance_ui()
        self.views()[0].update()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def addCommand(self, command: QUndoCommand):
        self.undo_stack.push(command)
        self.primaryView().update()
        self.setHasChanges(True)
        self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        if isinstance(command, AddItemCommand):
            if isinstance(command.item, CanvasItem):
                self.canvas_count += 1

        print(f'Command At: {command}')

    def selectedItemsBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.boundingRect())
        return bounding_rect

    def selectedItemsSceneBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        return bounding_rect

    def selectItemsInMode(self, mode: str):
        if mode == 'canvas':
            self.parentWindow.add_canvas_btn.trigger()

        else:
            self.parentWindow.select_btn.trigger()

        self.clearSelection()

        for item in self.items():
            if mode == 'path':
                if isinstance(item, CustomPathItem):
                    item.setSelected(True)

            elif mode == 'leaderline':
                if isinstance(item, LeaderLineItem):
                    item.setSelected(True)

            elif mode == 'pixmap':
                if isinstance(item, CustomPixmapItem):
                    item.setSelected(True)

            elif mode == 'svg':
                if isinstance(item, CustomSvgItem):
                    item.setSelected(True)

            elif mode == 'text':
                if isinstance(item, CustomTextItem):
                    item.setSelected(True)

            elif mode == 'svg':
                if isinstance(item, CustomSvgItem):
                    item.setSelected(True)

            elif mode == 'canvas':
                if isinstance(item, CanvasItem):
                    item.setSelected(True)

    def selectBelow(self):
        selected_items = self.selectedItems()
        for selected_item in selected_items:
            for i in self.items():
                if not isinstance(i, CanvasItem) and i.collidesWithItem(selected_item):
                    if i.zValue() <= selected_item.zValue() and i != selected_item:
                        i.setSelected(True)

    def selectAbove(self):
        selected_items = self.selectedItems()
        for selected_item in selected_items:
            for i in self.items():
                if not isinstance(i, CanvasItem) and i.collidesWithItem(selected_item):
                    if i.zValue() >= selected_item.zValue() and i != selected_item:
                        i.setSelected(True)

    def selectColliding(self):
        selected_items = self.selectedItems()
        for selected_item in selected_items:
            for i in self.items():
                if not isinstance(i, CanvasItem) and i.collidesWithItem(selected_item):
                    if i != selected_item:
                        i.setSelected(True)

    def arrange(self):
        self.w = ArrangeWin(self, self.parentWindow)
        self.w.show()

    def rename(self):
        sorted_items = []

        for item in self.items():
            if isinstance(item, CanvasItem):
                sorted_items.append(item)

        # Sort by y position first (vertical), then by x position (horizontal)
        sorted_items.sort(key=lambda item: (item.pos().y(), item.pos().x()))

        new_canvas_names = []
        old_canvas_names = []
        count = 1

        if sorted_items:
            for i in sorted_items:
                old_canvas_names.append(i.name())
                new_canvas_names.append(f'Canvas {count}')
                count += 1

            command = MultiCanvasNameEditCommand(sorted_items, old_canvas_names, new_canvas_names)
            self.addCommand(command)

    def copy(self):
        self.copy_stack.clear()

        for item in self.selectedItems():
            if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                continue

            else:
                self.copy_stack.append(item.copy())

        self.views()[0].update()

    def cut(self):
        self.copy_stack.clear()

        cut_items = []

        for item in self.selectedItems():
            if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                continue

            else:
                self.copy_stack.append(item.copy())
                cut_items.append(item)

        self.addCommand(RemoveItemCommand(self, cut_items))
        self.views()[0].update()

    def paste(self):
        new_items = []

        for item in self.copy_stack:
            new_items.append(item.copy())

            if isinstance(item, CanvasItem):
                self.parentWindow.use_add_canvas()

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

            for item in new_items:
                if isinstance(item, CanvasItem):
                    self.parentWindow.use_add_canvas()

        self.views()[0].update()

    def duplicate(self):
        new_items = []

        for item in self.selectedItems():
            if isinstance(item, CustomTextItem) and isinstance(item.parentItem(), LeaderLineItem):
                continue

            else:
                new_items.append(item.duplicate())

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

            for item in new_items:
                if isinstance(item, CanvasItem):
                    self.parentWindow.use_add_canvas()

        self.views()[0].update()

    def hasChanges(self):
        return self.modified

    def setHasChanges(self, has: bool):
        self.modified = has

    def primaryView(self) -> CustomGraphicsView:
        return self.views()[0]