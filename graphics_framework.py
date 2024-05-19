from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from undo_commands import *
import time

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas, button, button2, option_btn, button4, erase_btn, add_canvas_btn, select_btn, scale_btn):
        super().__init__()
        self.points = []

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Set widgets
        self.button = button
        self.button2 = button2
        self.button3 = option_btn
        self.text_btn = button4
        self.erase_btn = erase_btn
        self.add_canvas_btn = add_canvas_btn
        self.select_btn = select_btn
        self.scale_btn = scale_btn

        # Items
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None
        self.stroke_fill = None
        self.font = None
        self.font = None
        self.layer_height = None

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [0, 100]

        # Canvas item
        self.canvas_item = None

    def update_pen(self, pen):
        self.pen = pen

    def update_stroke_fill_color(self, brush):
        self.stroke_fill = brush

    def update_font(self, font, color):
        self.font = font
        self.font_color = color

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.button.isChecked() or self.erase_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    self.scene().clearSelection()
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_path_draw_start(event)

        # Check if the Line and Label tool is turned on
        elif self.button2.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    self.scene().clearSelection()
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_label_start(event)

        elif self.text_btn.isChecked():
            self.on_add_text(event)

        elif self.scale_btn.isChecked():
            self.on_scale_start(event)

        elif self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_add_canvas_start(event)

        self.on_add_canvas(event)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Create a tooltip for whenever we move the mouse
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)
        QToolTip.showText(p, f'''x: {int(p.x())} 
y: {int(p.y())}''')

        # Check if the path tool is enabled
        if self.button.isChecked() or self.erase_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_path_draw(event)

        # Check if the line and label tool is enabled
        elif self.button2.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_label(event)

        elif self.scale_btn.isChecked():
            self.on_scale(event)

        elif self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

            self.on_add_canvas_drag(event)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Check if path tool is enabled
        if self.button.isChecked() or self.erase_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

            self.on_path_draw_end(event)

        # Check if the line and label tool is enabled
        elif self.button2.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

            self.on_label_end(event)

        elif self.scale_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

            self.on_scale_end(event)

        elif self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    pass

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

            self.on_add_canvas_end(event)

        super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event):
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

    def dragMoveEvent(self, event):
        item = event.source()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.toLocalFile().endswith('.svg'):
                item = CustomSvgItem(url.toLocalFile())
                item.store_filename(url.toLocalFile())

            else:
                pixmap = QPixmap(url.toLocalFile())
                item = CustomPixmapItem(pixmap)
                item.store_filename(url.toLocalFile())

            # Set default attributes
            item.setPos(self.mapToScene(event.pos()))
            item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            item.setZValue(0)

            # Add item
            add_command = AddItemCommand(self.canvas, item)
            self.canvas.addCommand(add_command)
            self.canvas.update()

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

            # If stroke fill button is checked, close the subpath
            if self.button3.isChecked():
                self.path.closeSubpath()

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

            # Set Tooltop
            path_item.setToolTip('Path')

            # Check if item is selected or moved so we can turn tool off
            if self.canvas.selectedItems():
                self.button.setChecked(False)
                self.setDragMode(QGraphicsView.RubberBandDrag)
                self.select_btn.setChecked(True)

    def on_label_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create the leader line
            self.leader_line = QPainterPath()  # Create a new QPainterPath
            self.leader_line.moveTo(self.mapToScene(event.pos()))
            self.setDragMode(QGraphicsView.NoDrag)
            self.clicked_label_point = self.mapToScene(event.pos())

            # Create the label text
            self.label_text = EditableTextBlock('An Editable Text Block')
            self.label_text.setFont(self.font)
            self.label_text.setPos(self.mapToScene(event.pos()))
            self.label_text.setDefaultTextColor(QColor('black'))
            self.label_text.setToolTip("Text")

            # Create path item
            self.pathg_item = LeaderLineItem(self.leader_line)
            self.pathg_item.setBrush(QBrush(QColor(Qt.transparent)))

            add_command2 = AddItemCommand(self.canvas, self.label_text)
            self.canvas.addCommand(add_command2)
            add_command3 = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command3)

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

            # Draw circle at the end of path
            scene_pos = self.mapToScene(event.pos())

            self.canvas.update()

            # Load path as QGraphicsItem, set parent items
            self.pathg_item.setPen(self.pen)
            self.pathg_item.setZValue(0)
            self.label_text.setParentItem(self.pathg_item)

            if self.leader_line.isEmpty():
                self.scene().removeItem(self.pathg_item)

            # Add items (no need to add rect, circle, and label because parent is path_item)
            add_command = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command)

            # Set flags
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.label_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

            # Set Tooltips for elements
            self.pathg_item.setToolTip('Leader Line')

            # Check if item is selected or moved so we can turn tool off
            if self.canvas.selectedItems():
                self.setDragMode(QGraphicsView.RubberBandDrag)
                self.select_btn.setChecked(True)

    def on_add_text(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())

            self.text = EditableTextBlock('Lorem Ipsum')
            self.text.setFont(self.font)
            self.text.setDefaultTextColor(self.font_color)

            add_command = AddItemCommand(self.canvas, self.text)
            self.canvas.addCommand(add_command)

            self.text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.text.setZValue(0)
            self.text.setPos(pos)

    def on_scale_start(self, event):
        try:
            self.initialScale = None

            if event.buttons() == Qt.LeftButton:
                self.startPos = self.mapToScene(event.pos())

                for item in self.canvas.selectedItems():
                    self.initialScale = item.scale()

        except Exception:
            pass

    def on_scale(self, event):
        try:
            self.setDragMode(QGraphicsView.NoDrag)

            if event.buttons() == Qt.LeftButton:
                delta = self.mapToScene(event.pos()) - self.startPos
                scale = 1 + delta.y() / 100.0

                for item in self.canvas.selectedItems():
                    if self.initialScale is not None:
                        if isinstance(item, CanvasItem):
                            pass

                        else:
                            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                            item.setTransformOriginPoint(item.boundingRect().center())
                            command = ScaleCommand(item, self.initialScale, self.initialScale * scale)
                            self.canvas.addCommand(command)

        except Exception:
            pass

    def on_scale_end(self, event):
        self.setDragMode(QGraphicsView.RubberBandDrag)

        for item in self.canvas.selectedItems():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def on_add_canvas(self, event):
        if self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    for items in item.childItems():
                        items.setVisible(True)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

        elif not self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    for items in item.childItems():
                        items.setVisible(False)
                        items.parentItem().setSelected(False)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

    def on_add_canvas_start(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            self.setDragMode(QGraphicsView.NoDrag)

            self.clicked_canvas_point = self.mapToScene(event.pos())
            self.added_click = event.pos()
            self.canvas_item = CanvasItem(self.clicked_canvas_point.x(), self.clicked_canvas_point.y(), 0,
                                          0)  # Initialize with zero width and height
            self.canvas_item_text = CanvasTextItem('Canvas', self.canvas_item)

            self.scene().addItem(self.canvas_item)  # Add canvas item to the scene
            self.scene().addItem(self.canvas_item_text)  # Add canvas text item to the scene

    def on_add_canvas_drag(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            if self.canvas_item is not None:
                if not hasattr(self, 'canvas_item'):
                    self.clicked_canvas_point = self.mapToScene(event.pos())
                    self.canvas_item = CanvasItem(self.clicked_canvas_point.x(), self.clicked_canvas_point.y(), 0,
                                                  0)  # Initialize with zero width and height
                    self.canvas_item_text = CanvasTextItem('Canvas', self.canvas_item)

                current_pos = self.mapToScene(event.pos())
                self.canvas_item.setRect(0,
                                         0,
                                         current_pos.x() - self.clicked_canvas_point.x(),
                                         current_pos.y() - self.clicked_canvas_point.y())

    def on_add_canvas_end(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            if self.canvas_item is not None:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                current_pos = self.mapToScene(event.pos())
                self.canvas_item.setRect(0, 0,
                                         current_pos.x() - self.clicked_canvas_point.x(),
                                         current_pos.y() - self.clicked_canvas_point.y())

                command = AddItemCommand(self.scene(), self.canvas_item)  # Assuming AddItemCommand is defined elsewhere
                self.canvas.addCommand(command)

                self.canvas_item.setPos(self.clicked_canvas_point)
                self.canvas_item_text.setPos(self.canvas_item.boundingRect().x(), self.canvas_item.boundingRect().y())
                self.canvas_item.setToolTip('Canvas')
                self.canvas_item.setZValue(-1)

                if self.canvas_item.rect().isEmpty():
                    self.scene().removeItem(self.canvas_item)

                self.clicked_canvas_point = None

                self.canvas.update()

        else:
            if self.canvas_item is not None:
                if self.canvas_item.rect().isEmpty():
                    self.scene().removeItem(self.canvas_item)

class CustomGraphicsScene(QGraphicsScene):
    itemMoved = pyqtSignal(QGraphicsItem, QPointF)

    def __init__(self, undoStack):
        super().__init__()
        self.undo_stack = undoStack
        self.scale_btn = None

        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

        self.movingItem = None
        self.oldPos = QPointF()
        self.itemMoved.connect(self.on_move_item)

    def set_widget(self, w):
        self.scale_btn = w

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:
            mousePos = event.buttonDownScenePos(Qt.RightButton)
            list = self.items(mousePos)
            for item in list:
                item.setSelected(True)

        else:
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

    def redo(self):
        self.undo_stack.redo()

    def addCommand(self, command):
        self.undo_stack.push(command)

    def selectedItemsBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        return bounding_rect

    def update(self, rect=None):
        super().update()

        for item in self.items():
            item.update()







