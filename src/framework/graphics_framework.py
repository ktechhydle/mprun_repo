import os.path
from src.gui.app_screens import TipWin, CanvasItemSelector, AllCanvasExporter, ArrangeWin
from src.framework.undo_commands import *
from src.framework.custom_classes import *
from src.framework.serializer import MPSerializer, MPDeserializer, MPDataRepairer
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
    def __init__(self, canvas, actions: list, zoom_spin):
        super().__init__()
        self.w = None

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Set widgets
        self.select_btn = actions[0]
        self.pan_btn = actions[1]
        self.path_btn = actions[2]
        self.pen_btn = actions[3]
        self.sculpt_btn = actions[4]
        self.line_and_label_btn = actions[5]
        self.text_btn = actions[6]
        self.scale_btn = actions[7]
        self.rotate_btn = actions[8]
        self.add_canvas_btn = actions[9]
        self.grid_checkbtn = actions[10]

        # Items
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None
        self.stroke_fill = None
        self.font = None
        self.layer_height = None
        self.path = None
        self.last_point = None

        # Tools
        self.pathDrawingTool = PathDrawerTool(self.canvas, self)
        self.penDrawingTool = PenDrawerTool(self.canvas, self)
        self.labelingTool = LineAndLabelTool(self.canvas, self)
        self.scalingTool = MouseScalingTool(self.canvas, self)
        self.rotatingTool = MouseRotatingTool(self.canvas, self)
        self.sculptingTool = PathSculptingTool(self.canvas, self)
        self.canvasTool = AddCanvasTool(self.canvas, self)

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [0, 100]
        self.zoom_spin = zoom_spin

    def update_pen(self, pen):
        self.pen = pen

    def update_brush(self, brush):
        self.stroke_fill = brush

    def update_font(self, font, color):
        self.font = font
        self.font_color = color

    def disable_item_flags(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def disable_item_movement(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsMovable, False)

    def show_tooltip(self, event):
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        QToolTip.showText(p, f'''x: {int(self.mapToScene(point).x())} 
y: {int(self.mapToScene(point).y())}''')

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.path_btn.isChecked():
            self.pathDrawingTool.on_path_draw_start(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.on_draw_start(event)
            self.disable_item_flags()

        elif self.line_and_label_btn.isChecked():
            self.labelingTool.on_label_start(event)
            self.disable_item_flags()

        elif self.text_btn.isChecked():
            self.on_add_text(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.scale_btn.isChecked():
            self.scalingTool.on_scale_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.rotate_btn.isChecked():
            self.rotatingTool.on_rotate_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.on_add_canvas_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_start(event)
            self.disable_item_flags()

        else:
            super().mousePressEvent(event)

        if event.button() == Qt.MiddleButton:
            self.on_pan_start(event)

        self.on_add_canvas_trigger()

    def mouseMoveEvent(self, event):
        if self.path_btn.isChecked():
            self.pathDrawingTool.show_tooltip(event)
            self.pathDrawingTool.on_path_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.show_tooltip(event)
            self.penDrawingTool.on_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.text_btn.isChecked():
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

        elif self.line_and_label_btn.isChecked():
            self.show_tooltip(event)
            self.labelingTool.on_label(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.scale_btn.isChecked():
            self.scalingTool.show_tooltip(event)
            self.scalingTool.on_scale(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.rotate_btn.isChecked():
            self.rotatingTool.on_rotate(event)
            self.rotatingTool.show_tooltip(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.show_tooltip(event)
            self.canvasTool.on_add_canvas_drag(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pan_btn.isChecked():
            self.show_tooltip(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.sculpt_btn.isChecked():
            self.show_tooltip(event)
            self.sculptingTool.on_sculpt(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        else:
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.path_btn.isChecked():
            self.pathDrawingTool.on_path_draw_end(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.on_draw_end(event)

        elif self.text_btn.isChecked():
            super().mouseReleaseEvent(event)

        elif self.line_and_label_btn.isChecked():
            self.labelingTool.on_label_end(event)
            super().mouseReleaseEvent(event)

        elif self.scale_btn.isChecked():
            self.scalingTool.on_scale_end(event)
            super().mouseReleaseEvent(event)

        elif self.rotate_btn.isChecked():
            self.rotatingTool.on_rotate_end(event)
            super().mouseReleaseEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.on_add_canvas_end(event)
            super().mouseReleaseEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_end(event)
            super().mouseReleaseEvent(event)

        elif self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_end(event)
            self.disable_item_flags()

        else:
            super().mouseReleaseEvent(event)

        if event.button() == Qt.MiddleButton:
            self.on_pan_end(event)
            if self.select_btn.isChecked():
                self.parent().use_select()

        self.parent().update_transform_ui()

    def mouseDoubleClickEvent(self, event):
        if self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_double_click(event)

        if self.scale_btn.isChecked():
            self.scalingTool.on_scale_double_click(event)

        elif self.rotate_btn.isChecked():
            self.rotatingTool.on_rotate_double_click(event)

        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        try:
            self.zoom_spin.blockSignals(True)
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

            current_zoom_percentage = self.transform().m11() * 100
            self.zoom_spin.setValue(int(current_zoom_percentage))
            self.zoom_spin.blockSignals(False)

        except Exception:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.toLocalFile().endswith('.svg'):
                item = CustomSvgItem(url.toLocalFile())
                item.store_filename(os.path.abspath(url.toLocalFile()))
                item.setToolTip('Imported SVG')

            elif url.toLocalFile().endswith(('.txt', '.csv')):
                with open(url.toLocalFile(), 'r') as f:
                    item = CustomTextItem(f.read())
                    item.setToolTip('Imported Text')

            elif url.toLocalFile().endswith('.md'):
                with open(url.toLocalFile(), 'r') as f:
                    item = CustomTextItem(f.read())
                    item.setToolTip('Imported Text')
                    item.toMarkdown()

            else:
                pixmap = QPixmap(url.toLocalFile())
                item = CustomPixmapItem(pixmap)
                item.store_filename(os.path.abspath(url.toLocalFile()))
                item.setToolTip('Imported Bitmap')

            # Set default attributes
            item.setPos(self.mapToScene(event.pos()) - item.boundingRect().center())
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
            item.setZValue(0)

            # Add item to scene
            add_command = AddItemCommand(self.canvas, item)
            self.canvas.addCommand(add_command)
            self.canvas.update()

    def fitInView(self, *args, **kwargs):
        super().fitInView(*args, **kwargs)
        self.applyZoom()

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
        posy = (pos.y() - self.w.height()) - 17  # account for scrollbar

        self.w.move(pos.x() + 4, posy)

    def updateTip(self):
        try:
            pos = self.mapToGlobal(self.rect().bottomLeft())
            posy = (pos.y() - self.w.height()) - 17  # account for scrollbar

            self.w.move(pos.x() + 4, posy)
        except:
            pass

    def on_add_text(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            i = self.scene().itemAt(self.mapToScene(event.pos()), self.transform())

            if i and isinstance(i, CustomTextItem):
                i.set_active()

            else:
                for item in self.canvas.items():
                    if isinstance(item, CustomTextItem):
                        if item.hasFocus():
                            item.clearFocus()
                            return

                pos = self.mapToScene(event.pos())

                self.text = CustomTextItem('Lorem Ipsum')
                self.text.setFont(self.font)
                self.text.setDefaultTextColor(self.font_color)

                add_command = AddItemCommand(self.canvas, self.text)
                self.canvas.addCommand(add_command)

                self.text.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                self.text.setZValue(0)
                self.text.setPos(pos)
                self.text.select_text_and_set_cursor()

    def on_add_canvas_trigger(self):
        if self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(True)

        elif not self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(False)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)

            self.canvas.setBackgroundBrush(QBrush(QColor('#606060')))

    def on_pan_start(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def on_pan_end(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)


class CustomGraphicsScene(QGraphicsScene):
    itemsMoved = pyqtSignal(object, object)

    def __init__(self, undoStack):
        super().__init__()
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

        # Grid
        self.gridEnabled = False
        self.gridSize = 10
        self.gridSquares = 5

        # Item Movement
        self.oldPositions = {}
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemsMoved.connect(self.onItemMoved)

        # Managers
        self.manager = SceneManager(self)
        self.template_manager = TemplateManager(self)
        self.importManager = ImportManager(self)
        self.exportManager = ExportManager(self)

    def setParentWindow(self, parent: QMainWindow):
        self.parentWindow = parent

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

    def drawBackground(self, painter, rect):
        try:
            super().drawBackground(painter, rect)

            if self.gridEnabled:
                # settings
                self._color_light = QColor("#a3a3a3")
                self._color_dark = QColor("#b8b8b8")

                self._pen_light = QPen(self._color_light)
                self._pen_light.setWidth(1)
                self._pen_dark = QPen(self._color_dark)
                self._pen_dark.setWidth(1)

                # here we create our grid
                left = int(math.floor(rect.left()))
                right = int(math.ceil(rect.right()))
                top = int(math.floor(rect.top()))
                bottom = int(math.ceil(rect.bottom()))

                first_left = left - (left % self.gridSize)
                first_top = top - (top % self.gridSize)

                # compute all lines to be drawn
                lines_light, lines_dark = [], []
                for x in range(first_left, right, self.gridSize):
                    if (x % (self.gridSize * self.gridSquares) != 0):
                        lines_light.append(QLine(x, top, x, bottom))
                    else:
                        lines_dark.append(QLine(x, top, x, bottom))

                for y in range(first_top, bottom, self.gridSize):
                    if (y % (self.gridSize * self.gridSquares) != 0):
                        lines_light.append(QLine(left, y, right, y))
                    else:
                        lines_dark.append(QLine(left, y, right, y))

                # draw the lines
                painter.setPen(self._pen_light)
                painter.drawLines(*lines_light)

                painter.setPen(self._pen_dark)
                painter.drawLines(*lines_dark)

        except Exception:
            pass

    def addItem(self, item):
        super().addItem(item)

        if self.gridEnabled:
            for item in self.items():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.gridEnabled = True

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

        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def redo(self):
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
            self.modified = True
            self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def addCommand(self, command):
        self.undo_stack.push(command)
        self.setHasChanges(True)
        self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        if isinstance(command, AddItemCommand):
            if isinstance(command.item, CanvasItem):
                self.canvas_count += 1

        print(command)

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

            elif mode == 'group':
                if isinstance(item, CustomGraphicsItemGroup):
                    item.setSelected(True)

    def setGridEnabled(self, enabled: bool):
        self.gridEnabled = enabled

    def setGridSize(self, grid_size: int):
        self.gridSize = grid_size
        self.update()

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

    def copy(self):
        self.copy_stack.clear()

        for item in self.selectedItems():
            self.copy_stack.append(item.copy())

    def paste(self):
        new_items = []

        for item in self.copy_stack:
            new_items.append(item.copy())

            if isinstance(item, CanvasItem):
                self.parentWindow.use_add_canvas()

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

    def duplicate(self):
        new_items = []

        for item in self.selectedItems():
            new_items.append(item.duplicate())

            if isinstance(item, CanvasItem):
                self.parentWindow.use_add_canvas()

        if new_items:
            self.addCommand(MultiAddItemCommand(self, new_items))

    def hasChanges(self):
        return self.modified

    def setHasChanges(self, has: bool):
        self.modified = has


class SceneManager:
    def __init__(self, scene: CustomGraphicsScene):
        self.scene = scene
        self.filename = 'Untitled'
        self.parent = None
        self.repair_needed = False

        self.serializer = MPSerializer(self.scene)
        self.deserializer = MPDeserializer(self.scene)

    def reset_to_default_scene(self):
        self.scene.clear()
        self.scene.setHasChanges(False)
        self.filename = 'Untitled'
        self.scene.parentWindow.setWindowTitle(f'{self.filename} - MPRUN')
        self.scene.parentWindow.create_default_objects()

    def restore(self):
        if self.scene.hasChanges():
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox(self.scene.parentWindow)
            confirmation_dialog.setWindowTitle('Close Document')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
            confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
            confirmation_dialog.setDefaultButton(QMessageBox.Save)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            if result == QMessageBox.Discard:
                self.reset_to_default_scene()

            elif result == QMessageBox.Save:
                success = self.scene.parentWindow.save()

                if success:
                    self.reset_to_default_scene()

        else:
            self.reset_to_default_scene()

    def save(self):
        try:
            if self.filename != 'Untitled':
                with open(self.filename, 'wb') as f:
                    pickle.dump(self.serializer.serialize_items(), f)
                    self.scene.parentWindow.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                    self.scene.setHasChanges(False)

                    return True

            else:
                self.saveas()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow, 'Open File Error', f'Error saving scene: {e}', QMessageBox.Ok)

    def saveas(self):
        filename, _ = QFileDialog.getSaveFileName(self.scene.parentWindow, 'Save As', '', 'MPRUN files (*.mp)')

        if filename:
            try:
                with open(filename, 'wb') as f:
                    pickle.dump(self.serializer.serialize_items(), f)

                    self.filename = filename
                    self.scene.setHasChanges(False)
                    self.scene.parentWindow.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                    self.scene.parentWindow.update_recent_file_data(filename)
                    self.scene.parentWindow.canvas_view.showMessage('File', f'File {self.filename} saved successfully.')

                    return True

            except Exception as e:
                print(e)

        else:
            return False

    def load(self, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.hasChanges():
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        self.scene.parentWindow.update_recent_file_data(filename)

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

                elif result == QMessageBox.Save:
                    parent.save()

                    filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        self.scene.parentWindow.update_recent_file_data(filename)

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

            else:
                filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                          'MPRUN files (*.mp)')

                if filename:
                    self.scene.undo_stack.clear()
                    self.scene.clear()
                    self.scene.parentWindow.update_recent_file_data(filename)

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserializer.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def load_from_file(self, filename, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.hasChanges():
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    if filename.endswith('.mpt'):
                        with open(filename, 'r') as f:
                            data = json.load(f)

                            self.scene.template_manager.deserialize_items(data)

                    elif filename.endswith('.mp'):
                        self.scene.undo_stack.clear()
                        self.scene.clear()

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                            self.scene.setHasChanges(False)

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

                elif result == QMessageBox.Save:
                    success = self.save()

                    if success:
                        if filename.endswith('.mpt'):
                            with open(filename, 'r') as f:
                                data = json.load(f)

                                self.scene.template_manager.deserialize_items(data)

                        elif filename.endswith('.mp'):
                            self.scene.undo_stack.clear()
                            self.scene.clear()

                            with open(filename, 'rb') as f:
                                items_data = pickle.load(f)
                                self.deserializer.deserialize_items(items_data)

                                self.filename = filename
                                parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                                self.scene.setHasChanges(False)

                                if self.repair_needed:
                                    # Display a confirmation dialog
                                    confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                    confirmation_dialog.setWindowTitle('Open Document Error')
                                    confirmation_dialog.setIcon(QMessageBox.Warning)
                                    confirmation_dialog.setText(
                                        f"The document has file directories that could not be found. Do you want to do a file repair?")
                                    confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                    confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                    # Get the result of the confirmation dialog
                                    result = confirmation_dialog.exec_()

                                    if result == QMessageBox.Yes:
                                        self.repair_file()

            else:
                if filename.endswith('.mpt'):
                    with open(filename, 'r') as f:
                        data = json.load(f)

                        self.scene.template_manager.deserialize_items(data)

                elif filename.endswith('.mp'):
                    self.scene.undo_stack.clear()
                    self.scene.clear()

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserializer.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                        self.scene.setHasChanges(False)

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def repair_file(self):
        self.w = MPDataRepairer(self.scene.parentWindow, filename=self.filename)


class TemplateManager:
    def __init__(self, scene: CustomGraphicsScene):
        self.scene = scene

    def load_template(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow,
                                                      'Open Template',
                                                      '',
                                                      'MPRUN template files (*.mpt)')

            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)

                    self.deserialize_items(data)

        except Exception as e:
            print(e)

    def save_template(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self.scene.parentWindow,
                                                      'Save Document As Template',
                                                      '',
                                                      'MPRUN template files (*.mpt)')

            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.serialize_items(), f, indent=4)

        except Exception as e:
            print(e)

    def serialize_items(self):
        data = []

        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                data.append(self.serialize_canvas(item))

        return data

    def serialize_canvas(self, canvas: CanvasItem):
        return {
            'type': 'CanvasItem',
            'rect': [0, 0, canvas.rect().width(), canvas.rect().height()],
            'name': canvas.name(),
            'x': canvas.pos().x(),
            'y': canvas.pos().y(),
        }

    def deserialize_items(self, items_data):
        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)

            if item is not None:
                self.scene.addItem(item)

        self.scene.parentWindow.use_exit_add_canvas()

    def deserialize_canvas(self, data):
        rect = QRectF(*data['rect'])
        canvas = CanvasItem(rect, data['name'])
        canvas.setPos(data['x'], data['y'])

        return canvas


class ImportManager:
    def __init__(self, scene: CustomGraphicsScene):
        self.canvas = scene

    def importFile(self):
        # Deactivate the add canvas tool
        self.canvas.parentWindow.use_exit_add_canvas()

        file_path, _ = QFileDialog().getOpenFileName(self.canvas.parentWindow,
                                                     "Insert Element",
                                                     "",
                                                     'Supported types (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.tiff *.tif *.xbm *.xpm *.svg *.md *.txt)')

        if file_path:
            if file_path.endswith('.svg'):
                svg_item = CustomSvgItem(file_path)
                svg_item.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, svg_item)
                self.canvas.addCommand(add_command)
                svg_item.setToolTip('Imported SVG')

                self.create_item_attributes(svg_item)

            elif file_path.endswith(('.txt', '.csv')):
                with open(file_path, 'r') as f:
                    item = CustomTextItem(f.read())

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)

                    self.create_item_attributes(item)

            elif file_path.endswith('.md'):
                with open(file_path, 'r') as f:
                    item = CustomTextItem(f.read())
                    item.toMarkdown()
                    item.set_locked()

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)

                    self.create_item_attributes(item)

            else:
                image1 = QPixmap(file_path)
                image2 = CustomPixmapItem(image1)
                image2.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, image2)
                self.canvas.addCommand(add_command)
                image2.setToolTip('Imported Pixmap')

                self.create_item_attributes(image2)

    def importMPBUILDFile(self):
        pass

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)


class ExportManager:
    def __init__(self, canvas: CustomGraphicsScene):
        self.canvas = canvas

    def normalExport(self):
        # Exit add canvas tool if active
        self.canvas.parentWindow.use_exit_add_canvas()
        self.canvas.parentWindow.select_btn.trigger()

        # Create a custom dialog to with a dropdown to select which canvas to export
        selector = CanvasItemSelector(self.canvas, self.canvas.parentWindow)
        selector.show()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                # Add the canvas items to the selector
                selector.add_canvas_item(itemName=item.toolTip(), itemKey=item)

        # Create a function to choose the selected item
        def export():
            index = selector.canvas_chooser_combo.currentIndex()
            selected_item = selector.canvas_chooser_combo.itemData(index)

            if selected_item:
                if selector.transparent_check_btn.isChecked():
                    self.canvas.setBackgroundBrush(QBrush(QColor(Qt.transparent)))

                    for item in self.canvas.items():
                        if isinstance(item, CanvasItem):
                            item.setTransparentMode()

                self.filterSelectedCanvasForExport(selected_item)

            else:
                QMessageBox.warning(self.canvas.parentWindow,
                                    'Export Selected Canvas',
                                    'No canvas elements found within the scene. '
                                    'Please create a canvas element to export.',
                                    QMessageBox.Ok)

        selector.export_btn.clicked.connect(export)

    def multipleExport(self):
        selector = AllCanvasExporter(self.canvas, self.canvas.parentWindow)
        selector.show()

    def exportAsBitmap(self, filename, selected_item):
        # Create a QImage with the size of the selected item (QGraphicsRectItem)
        rect = selected_item.sceneBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        print(rect)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        try:
            # Save the image to file
            success = image.save(filename)

            if success:
                self.show_export_finished()

                # Open the image with the default image viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

        except Exception as e:
            # If saving failed, show an error notification
            QMessageBox.critical(self.canvas.parentWindow, "Export Error", f"Failed to export canvas to file: {e}")

    def exportAsSVG(self, file_path, selected_item):
        try:
            # Get the bounding rect
            rect = selected_item.sceneBoundingRect()

            # Export as SVG
            svg_generator = QSvgGenerator()
            svg_generator.setFileName(file_path)
            svg_generator.setSize(rect.size().toSize())
            svg_generator.setViewBox(rect)

            # Clear selection
            self.canvas.clearSelection()

            # Create a QPainter to paint onto the QSvgGenerator
            painter = QPainter()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.begin(svg_generator)

            # Render the scene onto the QPainter
            self.canvas.render(painter, target=rect, source=rect)

            # End painting
            painter.end()

            self.show_export_finished()

            # Open the image with the default image viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

        except Exception as e:
            # Show export error notification
            QMessageBox.information(self.canvas.parentWindow, 'Export Failed', f'Export failed: {e}',
                                    QMessageBox.Ok)

    def exportAsPDF(self, file_path, selected_item):
        try:
            # Get the bounding rect of the selected item
            bounding_rect = selected_item.sceneBoundingRect()

            # Configure the printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            # Adjust the printer's page size to match the bounding rect
            printer.setPageSizeMM(QSizeF(bounding_rect.width(), bounding_rect.height()))

            # Start painting
            painter = QPainter()
            painter.begin(printer)

            # Translate painter to the bounding rect top-left
            painter.translate(-bounding_rect.topLeft())

            # Render the selected item
            self.canvas.render(painter, QRectF(), bounding_rect)

            # End painting
            painter.end()

        except Exception as e:
            print(e)

        self.show_export_finished()

        # Open the PDF with the default viewer
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def filterSelectedCanvasForExport(self, selected_item):
        # File dialog, filepath
        file_dialog = QFileDialog()

        file_path, selected_filter = file_dialog.getSaveFileName(self.canvas.parentWindow, 'Export Canvas', '',
                                                                 supported_file_exporting)

        if file_path:
            selected_extension = filter_extensions.get(selected_filter, '.png')

            # Ensure the file_path has the selected extension
            if not file_path.endswith(selected_extension):
                file_path += selected_extension

            if selected_extension == '.svg':
                self.exportAsSVG(file_path, selected_item)

            elif selected_extension == '.pdf':
                self.exportAsPDF(file_path, selected_item)

            else:
                try:
                    self.canvas.clearSelection()
                    self.exportAsBitmap(file_path, selected_item)

                except Exception as e:
                    print(e)

            self.canvas.parentWindow.use_exit_add_canvas()

    def show_export_finished(self):
        self.canvas.views()[0].showMessage('Export', 'Export completed successfully.')
