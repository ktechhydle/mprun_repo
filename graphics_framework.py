import os.path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from undo_commands import *
from OpenGL.GL import *
from OpenGL.GLU import *
from app_internal import *
import xml.etree.ElementTree as ET
import time
import json
import pickle
import math

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas,
                 button,
                 button2,
                 smooth_btn,
                 button4,
                 add_canvas_btn,
                 select_btn,
                 scale_btn,
                 pan_btn,
                 zoom_spin,
                 grid_checkbtn):
        super().__init__()
        self.scalingCommand = None
        self.points = []

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

        # File
        self.isUntitled = True
        self.current_version = '1.0.0'

        # Set widgets
        self.button = button
        self.button2 = button2
        self.pen_btn = smooth_btn
        self.text_btn = button4
        self.add_canvas_btn = add_canvas_btn
        self.select_btn = select_btn
        self.scale_btn = scale_btn
        self.pan_btn = pan_btn
        self.grid_checkbtn = grid_checkbtn

        # Items
        self.canvas = canvas
        self.mouse_offset = None
        self.is_dragging = False
        self.temp_path_item = None
        self.temp_canvas = None
        self.pen = None
        self.stroke_fill = None
        self.font = None
        self.layer_height = None
        self.path = None
        self.last_point = None

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [0, 100]
        self.zoom_spin = zoom_spin

        # Canvas item
        self.canvas_item = None

    def update_pen(self, pen):
        self.pen = pen

    def update_stroke_fill_color(self, brush):
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

    def enable_item_flags(self):
        for item in self.scene().items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                item.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.button.isChecked():
            self.on_path_draw_start(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_start(event)
            self.disable_item_flags()

        elif self.button2.isChecked():
            self.on_label_start(event)
            self.disable_item_flags()

        elif self.text_btn.isChecked():
            self.on_add_text(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.scale_btn.isChecked():
            self.on_scale_start(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        else:
            super().mousePressEvent(event)

        self.on_add_canvas_trigger()
        
    def mouseMoveEvent(self, event):
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)
        QToolTip.showText(p, f'''x: {int(p.x())} 
y: {int(p.y())}''')

        if self.button.isChecked():
            self.on_path_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)
            
        elif self.text_btn.isChecked():
            super().mouseMoveEvent(event)

        elif self.button2.isChecked():
            self.on_label(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.scale_btn.isChecked():
            self.on_scale(event)
            self.disable_item_movement()
            super().mouseMoveEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_drag(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pan_btn.isChecked():
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.button.isChecked():
            self.on_path_draw_end(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_end(event)
            
        elif self.text_btn.isChecked():
            super().mouseReleaseEvent(event)

        elif self.button2.isChecked():
            self.on_label_end(event)

        elif self.scale_btn.isChecked():
            self.on_scale_end(event)
            super().mouseReleaseEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_end(event)
            super().mouseReleaseEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_end(event)
            super().mouseReleaseEvent(event)

        else:
            super().mouseReleaseEvent(event)

        self.parent().update_transform_ui()

    def wheelEvent(self, event):
        try:
            self.zoom_spin.blockSignals(True)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

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
                item.store_filename(url.toLocalFile())
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
                item.store_filename(url.toLocalFile())
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

    def on_path_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Set drag mode
            self.setDragMode(QGraphicsView.NoDrag)

        super().mousePressEvent(event)

    def on_path_draw(self, event):
        # Check the buttons
        if event.buttons() == Qt.LeftButton:
            self.path.lineTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())
            
            # Remove temporary path if it exists
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            # Load temporary path as QGraphicsItem to view it while drawing
            self.temp_path_item = CustomPathItem(self.path)
            self.temp_path_item.setPen(self.pen)
            self.temp_path_item.setBrush(self.stroke_fill)
            self.temp_path_item.setZValue(0)
            self.canvas.addItem(self.temp_path_item)

            self.canvas.update()

    def on_path_draw_end(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            self.path.lineTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Check if there is a temporary path (if so, remove it now)
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            self.canvas.update()

            # Load main path as QGraphicsItem
            path_item = CustomPathItem(self.path)
            path_item.setPen(self.pen)
            path_item.setZValue(0)
            path_item.setBrush(self.stroke_fill)

            # Add item
            add_command = AddItemCommand(self.canvas, path_item)
            self.canvas.addCommand(add_command)

            # Set Flags
            path_item.setFlag(QGraphicsItem.ItemIsSelectable)
            path_item.setFlag(QGraphicsItem.ItemIsMovable)

            # Set Tooltip
            path_item.setToolTip('Path')

    def on_smooth_path_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Set drag mode
            self.setDragMode(QGraphicsView.NoDrag)

            super().mousePressEvent(event)

    def on_smooth_path_draw_draw(self, event):
        if self.path is not None:
            # Check the buttons
            if event.buttons() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))
                self.last_point = self.mapToScene(event.pos())

                # Remove temporary path if it exists
                if self.temp_path_item is not None:
                    self.canvas.removeItem(self.temp_path_item)

                # Load temporary path as QGraphicsItem to view it while drawing
                self.path.setFillRule(Qt.WindingFill)
                self.temp_path_item = CustomPathItem(self.path)
                self.temp_path_item.path().setFillRule(Qt.WindingFill)
                self.temp_path_item.setPen(self.pen)
                self.temp_path_item.setBrush(self.stroke_fill)
                self.temp_path_item.setZValue(0)
                self.canvas.addItem(self.temp_path_item)

                try:
                    self.temp_path_item.setPath(self.temp_path_item.smooth_path(self.temp_path_item.path(), 0.75))

                except Exception:
                    pass

                self.canvas.update()

                super().mouseMoveEvent(event)

    def on_smooth_path_draw_end(self, event):
        if self.path is not None:
            if self.path.isEmpty():
                return

            else:
                # Check the buttons
                if event.button() == Qt.LeftButton:
                    self.path.lineTo(self.mapToScene(event.pos()))
                    self.last_point = self.mapToScene(event.pos())

                    # Check if there is a temporary path (if so, remove it now)
                    if self.temp_path_item is not None:
                        self.canvas.removeItem(self.temp_path_item)

                    self.canvas.update()

                    # Load main path as QGraphicsItem
                    path_item = CustomPathItem(self.path)
                    path_item.path().setFillRule(Qt.WindingFill)
                    path_item.setPen(self.pen)
                    path_item.setZValue(0)
                    path_item.setBrush(self.stroke_fill)
                    try:
                        path_item.setPath(path_item.smooth_path(path_item.path(), 0.1))
                    except Exception:
                        pass

                    # Add item
                    add_command = AddItemCommand(self.canvas, path_item)
                    self.canvas.addCommand(add_command)

                    # Set Flags
                    path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                    path_item.setFlag(QGraphicsItem.ItemIsMovable)

                    # Set Tooltop
                    path_item.setToolTip('Path')

                    self.path = None
                    self.temp_path_item = None
                    self.last_point = None

                    super().mouseReleaseEvent(event)

    def on_label_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create the leader line
            self.leader_line = QPainterPath()  # Create a new QPainterPath
            self.leader_line.moveTo(self.mapToScene(event.pos()))
            self.setDragMode(QGraphicsView.NoDrag)
            self.clicked_label_point = self.mapToScene(event.pos())

            # Create path item
            self.pathg_item = LeaderLineItem(self.leader_line, 'Lorem Ipsum')
            self.pathg_item.setBrush(self.stroke_fill)
            self.pathg_item.text_element.setFont(self.font)
            self.pathg_item.text_element.setPos(self.mapToScene(event.pos()) - QPointF(0, self.pathg_item.text_element.sceneBoundingRect().height()))


            add_command = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command)

            self.canvas.update()

    def on_label(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            # Move line to current coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))
            self.pathg_item.setPath(self.leader_line)
            self.pathg_item.update()

            self.canvas.update()

    def on_label_end(self, event):
        # Check buttons
        if event.button() == Qt.LeftButton:
            # Move line to current mouse coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))
            self.pathg_item.setPath(self.leader_line)
            self.canvas.update()

            # Load path as QGraphicsItem, set parent items
            self.pathg_item.setPen(self.pen)
            self.pathg_item.setZValue(0)
            self.pathg_item.text_element.select_text_and_set_cursor()

            if self.leader_line.isEmpty():
                self.scene().removeItem(self.pathg_item)

            # Add item
            add_command = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command)

            # Set flags
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

            # Set Tooltips for elements
            self.pathg_item.setToolTip('Leader Line')

    def on_add_text(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())

            self.text = CustomTextItem('Lorem Ipsum')
            self.text.setFont(self.font)
            self.text.setDefaultTextColor(self.font_color)

            add_command = AddItemCommand(self.canvas, self.text)
            self.canvas.addCommand(add_command)

            self.text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.text.setZValue(0)
            self.text.setPos(pos)
            self.text.select_text_and_set_cursor()

    def on_scale_start(self, event):
        if self.canvas.gridEnabled:
            self.grid_checkbtn.click()

        try:
            self.initialScale = None
            if event.buttons() == Qt.LeftButton:
                self.startPos = self.mapToScene(event.pos())

                selected_items = self.scene().selectedItems()
                if selected_items:
                    item = selected_items[0]
                    self.initialScale = item.transform().m11(), item.transform().m22()  # Get initial scale factors
                    self.oldTransform = item.transform()  # Store the original transform
                    self.scalingCommand = MouseTransformScaleCommand(item, self.oldTransform, self.oldTransform)

        except Exception as e:
            pass

    def on_scale(self, event):
        try:
            self.setDragMode(QGraphicsView.NoDrag)

            if event.buttons() == Qt.LeftButton and self.scalingCommand:
                # Calculate delta relative to the center of the item
                item_center = self.scalingCommand.item.boundingRect().center()
                delta = self.mapToScene(event.pos()) - item_center

                # Calculate scaling factors
                scale_x = 1 + delta.x() / 100.0
                scale_y = 1 + delta.y() / 100.0

                item = self.scalingCommand.item
                if self.initialScale is not None:
                    if isinstance(item, CanvasItem):
                        pass
                    else:
                        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

                        # Check if Shift key is pressed
                        modifiers = event.modifiers()
                        if modifiers & Qt.ShiftModifier:
                            uniform_scale = 1 + max(delta.x(), delta.y()) / 100.0
                            scale_x = scale_y = uniform_scale

                        # Store original position
                        old_pos = item.pos()

                        # Set transform origin point to center
                        item.setTransformOriginPoint(item_center)

                        # Apply scaling transformation
                        transform = QTransform().translate(item_center.x(), item_center.y()) \
                            .scale(scale_x, scale_y) \
                            .translate(-item_center.x(), -item_center.y())
                        item.setTransform(transform)

                        # Update position to keep the item centered
                        new_pos = item.pos()
                        item.setPos(new_pos + old_pos - item.pos())

                        # Update the new scale in the command
                        self.scalingCommand.new_transform = transform

        except Exception as e:
            pass

    def on_scale_end(self, event):
        try:
            self.setDragMode(QGraphicsView.RubberBandDrag)

            for item in self.scene().selectedItems():
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

            if self.scalingCommand and self.scalingCommand.new_transform != self.scalingCommand.old_transform:
                self.canvas.addCommand(self.scalingCommand)
                self.scalingCommand = None

        except Exception as e:
            pass

    def on_add_canvas_trigger(self):
        if self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(True)

        elif not self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(False)

    def on_add_canvas_start(self, event):
        if event.button() == Qt.LeftButton:
            item_under_mouse = self.itemAt(event.pos())

            if item_under_mouse is None:  # No item under mouse, create new CanvasItem
                self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
                self.setDragMode(QGraphicsView.NoDrag)

                self.clicked_canvas_point = self.mapToScene(event.pos())
                self.canvas_item = CanvasItem(QRectF(0, 0, 1, 1), f'Canvas {self.scene().canvas_count}')
                self.canvas_item.setPos(self.clicked_canvas_point)

                command = AddItemCommand(self.scene(), self.canvas_item)
                self.canvas.addCommand(command)
            else:
                pass

    def on_add_canvas_drag(self, event):
        if self.canvas_item is not None and event.buttons() & Qt.LeftButton and self.clicked_canvas_point is not None:
            current_pos = self.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & Qt.ShiftModifier:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.canvas_item.setRect(0, 0, width, height)

    def on_add_canvas_end(self, event):
        if self.canvas_item is not None and event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            current_pos = self.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & Qt.ShiftModifier:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.canvas_item.setRect(0, 0, width, height)
            self.canvas_item.setPos(self.clicked_canvas_point)
            self.canvas_item.setToolTip(f'Canvas {self.scene().canvas_count}')
            self.canvas_item.setZValue(-1)
            self.canvas_item.setCanvasActive(True)
            self.scene().addItem(self.canvas_item.text)

            if self.canvas_item.rect().isEmpty():
                self.scene().removeItem(self.canvas_item)
                self.scene().removeItem(self.canvas_item.text)

            self.canvas_item = None
            self.clicked_canvas_point = None

            self.canvas.update()

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
    itemMoved = pyqtSignal(QGraphicsItem, QPointF)

    def __init__(self, undoStack):
        super().__init__()
        self.file_name = None
        self.mpversion = '1.0.0'
        self.canvas_count = 1
        self.undo_stack = undoStack
        self.scale_btn = None
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
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemMoved.connect(self.on_move_item)

        # File
        self.manager = SceneManager(self)

    def set_widget(self, w):
        self.scale_btn = w

    def setParentWindow(self, parent: QMainWindow):
        self.parentWindow = parent

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.scale_btn is not None:
            if self.scale_btn.isChecked():
                pass

            else:
                mousePos = event.buttonDownScenePos(Qt.LeftButton)
                itemList = self.items(mousePos)
                self.movingItem = None if not itemList else itemList[0]

                if self.movingItem and event.button() == Qt.LeftButton:
                    self.oldPos = self.movingItem.pos()

            self.clearSelection()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self.scale_btn is not None:
            if self.scale_btn.isChecked():
                pass

            else:
                if self.movingItem and event.button() == Qt.LeftButton:
                    if self.oldPos != self.movingItem.pos():
                        self.itemMoved.emit(self.movingItem, self.oldPos)
                    self.movingItem = None

        super().mouseReleaseEvent(event)

    def on_move_item(self, movedItem, oldPos):
        command = MoveItemCommand(movedItem, oldPos)
        self.addCommand(command)

    def undo(self):
        self.undo_stack.undo()
        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()
        self.modified = True
        self.parentWindow.setWindowTitle(f'MPRUN - *{os.path.basename(self.manager.filename)}')

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def redo(self):
        self.undo_stack.redo()
        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def addCommand(self, command):
        self.undo_stack.push(command)
        self.modified = True
        self.parentWindow.setWindowTitle(f'MPRUN - *{os.path.basename(self.manager.filename)}')

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

    def update(self, rect=None):
        super().update()

        for item in self.items():
            item.update()

    def setGridEnabled(self, enabled: bool):
        self.gridEnabled = enabled

    def setGridSize(self, grid_size: int):
        self.gridSize = grid_size
        self.update()

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

        if isinstance(item, CanvasItem):
            self.canvas_count += 1

        if self.gridEnabled:
            for item in self.items():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.gridEnabled = True

    def removeItem(self, item):
        if isinstance(item, CustomTextItem):
            if isinstance(item.parentItem(), LeaderLineItem):
                return 
            else:
                super().removeItem(item)
                
        super().removeItem(item)

        for item in self.items():
            if isinstance(item, CanvasItem):
                if self.canvas_count == 1:
                    pass

                else:
                    self.canvas_count -= 1

class SceneManager:
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.filename = 'Untitled'
        self.parent = None
        self.repair_needed = False

    def load(self, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.modified:
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
                    filename, _ = QFileDialog.getOpenFileName(self.scene.parent(), 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'MPRUN - {os.path.basename(self.filename)}')

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

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'MPRUN - {os.path.basename(self.filename)}')

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

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'MPRUN - {os.path.basename(self.filename)}')

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

    def serialize_items(self):
        items_data = []

        items_data.append({
            'mpversion': self.scene.mpversion,
            'copyright': copyright_message,
        })

        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                items_data.append(self.serialize_canvas(item))

            elif isinstance(item, CustomTextItem):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomTextItem',
                        'markdown': True if item.markdownEnabled else False,
                        'text': item.old_text if item.markdownEnabled else item.toPlainText(),
                        'font': self.serialize_font(item.font()),
                        'color': self.serialize_color(item.defaultTextColor()),
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'locked': True if item.markdownEnabled else False,
                        'visible': item.isVisible(),
                    })

            elif isinstance(item, CustomPathItem):
                if item.parentItem():
                    pass

                else:
                    path_data = {
                        'type': 'CustomPathItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'elements': self.serialize_path(item.path()),
                        'smooth': True if item.smooth else False,
                        'addtext': True if item.add_text else False,
                        'textalongpath': item.text_along_path if item.add_text else '',
                        'textfont': self.serialize_font(item.text_along_path_font) if item.add_text else self.serialize_font(QFont('Arial', 20)),
                        'textcolor': self.serialize_color(item.text_along_path_color) if item.add_text else self.serialize_color(QColor('black')),
                        'textspacing': item.text_along_path_spacing if item.add_text else 3,
                        'starttextfrombeginning': item.start_text_from_beginning if item.add_text else False,
                        'visible': item.isVisible(),
                    }

                    items_data.append(path_data)

            elif isinstance(item, CustomGraphicsItemGroup):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomGraphicsItemGroup',
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'visible': item.isVisible(),
                        'children': self.serialize_group(item)
                    })

            elif isinstance(item, LeaderLineItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'LeaderLineItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'elements': self.serialize_path(item.path()),
                        'text': item.text_element.toPlainText(),
                        'textcolor': self.serialize_color(item.text_element.defaultTextColor()),
                        'textfont': self.serialize_font(item.text_element.font()),
                        'textposx': item.text_element.pos().x(),
                        'textposy': item.text_element.pos().y(),
                        'textzval': item.text_element.zValue(),
                        'visible': item.isVisible(),
                        'textvisible': item.text_element.isVisible(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomSvgItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'CustomSvgItem',
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'filename': item.source(),
                        'visible': item.isVisible(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomPixmapItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'CustomPixmapItem',
                        'rotation': item.rotation(),
                        'transform': self.serialize_transform(item.transform()),
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'name': item.toolTip(),
                        'zval': item.zValue(),
                        'filename': item.return_filename(),
                        'visible': item.isVisible(),
                    }

                    items_data.append(data)

        return items_data

    def serialize_color(self, color: QColor):
        return {
            'red': color.red(),
            'green': color.green(),
            'blue': color.blue(),
            'alpha': color.alpha(),
        }

    def serialize_pen(self, pen: QPen):
        return {
            'width': pen.width(),
            'color': self.serialize_color(pen.color()),
            'style': pen.style(),
            'capstyle': pen.capStyle(),
            'joinstyle': pen.joinStyle()
        }

    def serialize_brush(self, brush: QBrush):
        return {
            'color': self.serialize_color(brush.color()),
            'style': brush.style()
        }

    def serialize_font(self, font: QFont):
        return {
            'family': font.family(),
            'pointsize': font.pixelSize(),
            'letterspacing': font.letterSpacing(),
            'bold': font.bold(),
            'italic': font.italic(),
            'underline': font.underline(),
        }

    def serialize_transform(self, transform: QTransform):
        return {
            'm11': transform.m11(),
            'm12': transform.m12(),
            'm13': transform.m13(),
            'm21': transform.m21(),
            'm22': transform.m22(),
            'm23': transform.m23(),
            'm31': transform.m31(),
            'm32': transform.m32(),
            'm33': transform.m33()
        }

    def serialize_canvas(self, canvas: CanvasItem):
        return {
            'type': 'CanvasItem',
            'rect': [0, 0, canvas.rect().width(), canvas.rect().height()],
            'name': canvas.name(),
            'x': canvas.pos().x(),
            'y': canvas.pos().y(),
        }

    def serialize_path(self, path: QPainterPath):
        elements = []
        for i in range(path.elementCount()):
            element = path.elementAt(i)
            if element.isMoveTo():
                elements.append({'type': 'moveTo', 'x': element.x, 'y': element.y})
            elif element.isLineTo():
                elements.append({'type': 'lineTo', 'x': element.x, 'y': element.y})
            elif element.isCurveTo():
                elements.append({'type': 'curveTo', 'x': element.x, 'y': element.y})
        return elements

    def serialize_group(self, group: CustomGraphicsItemGroup):
        children = []
        for child in group.childItems():
            if isinstance(child, CustomTextItem):
                children.append({
                    'type': 'CustomTextItem',
                    'markdown': True if child.markdownEnabled else False,
                    'text': child.toPlainText(),
                    'font': self.serialize_font(child.font()),
                    'color': self.serialize_color(child.defaultTextColor()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'locked': True if child.markdownEnabled else False,
                    'visible': child.isVisible(),
                })
            elif isinstance(child, CustomPathItem):
                path_data = {
                    'type': 'CustomPathItem',
                    'pen': self.serialize_pen(child.pen()),
                    'brush': self.serialize_brush(child.brush()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'elements': self.serialize_path(child.path()),
                    'visible': child.isVisible(),
                }

                if child.add_text:
                    path_data.update({
                        'addtext': child.add_text,
                        'text': child.text_along_path,
                        'textfont': self.serialize_font(child.text_along_path_font),
                        'textcolor': self.serialize_color(child.text_along_path_color),
                        'textspacing': child.text_along_path_spacing,
                        'starttextfrombeginning': child.start_text_from_beginning,
                    })

                children.append(path_data)

        return children

    def deserialize_items(self, items_data):
        # Handle metadata
        metadata = items_data.pop(0)
        self.scene.mpversion = metadata.get('mpversion', 'unknown')

        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)
            elif item_data['type'] == 'CustomTextItem':
                item = self.deserialize_custom_text_item(item_data)
            elif item_data['type'] == 'CustomPathItem':
                item = self.deserialize_custom_path_item(item_data)
            elif item_data['type'] == 'CustomGraphicsItemGroup':
                item = self.deserialize_custom_group_item(item_data)
            elif item_data['type'] == 'LeaderLineItem':
                item = self.deserialize_leader_line_item(item_data)
            elif item_data['type'] == 'CustomSvgItem':
                item = self.deserialize_custom_svg_item(item_data)
            elif item_data['type'] == 'CustomPixmapItem':
                item = self.deserialize_custom_pixmap_item(item_data)

            if item is not None:
                self.scene.addItem(item)

        self.scene.parentWindow.use_exit_add_canvas()

    def deserialize_color(self, color):
        return QColor(color['red'], color['green'], color['blue'], color['alpha'])

    def deserialize_pen(self, data):
        pen = QPen()
        pen.setWidth(data['width'])
        pen.setColor(self.deserialize_color(data['color']))
        pen.setStyle(data['style'])
        pen.setCapStyle(data['capstyle'])
        pen.setJoinStyle(data['joinstyle'])
        return pen

    def deserialize_brush(self, data):
        brush = QBrush()
        brush.setColor(self.deserialize_color(data['color']))
        brush.setStyle(data['style'])
        return brush

    def deserialize_font(self, data):
        font = QFont()
        font.setFamily(data['family'])
        font.setPixelSize(data['pointsize'])
        font.setLetterSpacing(QFont.AbsoluteSpacing, data['letterspacing'])
        font.setBold(data['bold'])
        font.setItalic(data['italic'])
        font.setUnderline(data['underline'])
        return font

    def deserialize_transform(self, data):
        transform = QTransform(
            data['m11'], data['m12'], data['m13'],
            data['m21'], data['m22'], data['m23'],
            data['m31'], data['m32'], data['m33']
        )
        return transform

    def deserialize_canvas(self, data):
        rect = QRectF(*data['rect'])
        canvas = CanvasItem(rect, data['name'])
        canvas.setPos(data['x'], data['y'])
        return canvas

    def deserialize_custom_text_item(self, data):
        text_item = CustomTextItem(data['text'])
        text_item.setFont(self.deserialize_font(data['font']))
        text_item.setDefaultTextColor(self.deserialize_color(data['color']))
        text_item.setRotation(data['rotation'])
        text_item.setTransform(self.deserialize_transform(data['transform']))
        text_item.setPos(data['x'], data['y'])
        text_item.setToolTip(data['name'])
        text_item.setZValue(data['zval'])
        text_item.locked = data['locked']
        text_item.setVisible(data['visible'])

        if data.get('markdown', True):
            text_item.toMarkdown()

        return text_item

    def deserialize_custom_path_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = CustomPathItem(sub_path)
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))
        path_item.setRotation(data['rotation'])
        path_item.setTransform(self.deserialize_transform(data['transform']))
        path_item.setPos(data['x'], data['y'])
        path_item.setToolTip(data['name'])
        path_item.setZValue(data['zval'])
        path_item.setVisible(data['visible'])

        if data.get('smooth', True):
            path_item.smooth = True

        else:
            path_item.smooth = False

        if data.get('addtext', True):
            path_item.add_text = True
            path_item.setTextAlongPath(data['textalongpath'])
            path_item.setTextAlongPathColor(self.deserialize_color(data['textcolor']))
            path_item.setTextAlongPathFont(self.deserialize_font(data['textfont']))
            path_item.setTextAlongPathSpacingFromPath(data['textspacing'])
            path_item.setTextAlongPathFromBeginning(data['starttextfrombeginning'])

        else:
            path_item.add_text = False

        return path_item

    def deserialize_custom_group_item(self, data):
        group_item = CustomGraphicsItemGroup()
        group_item.setRotation(data['rotation'])
        group_item.setTransform(self.deserialize_transform(data['transform']))
        group_item.setPos(data['x'], data['y'])
        group_item.setToolTip(data['name'])
        group_item.setZValue(data['zval'])
        group_item.setVisible(data['visible'])

        for child_data in data['children']:
            if child_data['type'] == 'CustomTextItem':
                child = self.deserialize_custom_text_item(child_data)
            elif child_data['type'] == 'CustomPathItem':
                child = self.deserialize_custom_path_item(child_data)
            # Add other child types as needed
            group_item.addToGroup(child)

        return group_item

    def deserialize_leader_line_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = LeaderLineItem(sub_path, data['text'])
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))
        path_item.setRotation(data['rotation'])
        path_item.setTransform(self.deserialize_transform(data['transform']))
        path_item.setPos(data['x'], data['y'])
        path_item.setToolTip(data['name'])
        path_item.setZValue(data['zval'])
        path_item.text_element.setPos(data['textposx'], data['textposy'])
        path_item.text_element.setZValue(data['textzval'])
        path_item.text_element.setDefaultTextColor(self.deserialize_color(data['textcolor']))
        path_item.text_element.setFont(self.deserialize_font(data['textfont']))
        path_item.setVisible(data['visible'])
        path_item.text_element.setVisible(data['textvisible'])

        return path_item

    def deserialize_custom_svg_item(self, data):
        if os.path.exists(data['filename']):
            svg_item = CustomSvgItem(data['filename'])
            svg_item.setRotation(data['rotation'])
            svg_item.setTransform(self.deserialize_transform(data['transform']))
            svg_item.setPos(data['x'], data['y'])
            svg_item.setToolTip(data['name'])
            svg_item.setZValue(data['zval'])
            svg_item.setVisible(data['visible'])
            return svg_item
        else:
            self.repair_needed = True
            return None

    def deserialize_custom_pixmap_item(self, data):
        if os.path.exists(data['filename']):
            pixmap = QPixmap(data['filename'])
            pixmap_item = CustomPixmapItem(pixmap)
            pixmap_item.setRotation(data['rotation'])
            pixmap_item.setTransform(self.deserialize_transform(data['transform']))
            pixmap_item.setPos(data['x'], data['y'])
            pixmap_item.setToolTip(data['name'])
            pixmap_item.setZValue(data['zval'])
            pixmap_item.setVisible(data['visible'])
            return pixmap_item
        else:
            self.repair_needed = True
            return None

    def repair_file(self):
        try:
            with open(self.filename, 'rb') as f:
                items_data = pickle.load(f)

            # Handle metadata
            metadata = items_data.pop(0)
            self.scene.mpversion = metadata.get('mpversion', 'unknown')

            repaired_items_data = []
            removed_files = []
            for item_data in items_data:
                if item_data['type'] in ('CustomPixmapItem', 'CustomSvgItem') and not os.path.exists(
                        item_data['filename']):
                    removed_files.append(item_data['filename'])
                else:
                    repaired_items_data.append(item_data)

            with open(self.filename, 'wb') as f:
                pickle.dump(repaired_items_data, f)

                QMessageBox.information(self.scene.parentWindow, 'File Repair', f"""File repair completed: 
Removed missing items with filenames: {', '.join(removed_files)}""")

        except Exception as e:
            print(f"Error repairing file: {e}")
