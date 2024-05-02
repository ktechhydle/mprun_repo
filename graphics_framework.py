from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
import time

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas, button, button2, button3, button4):
        super().__init__()
        self.points = []

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Set widgets
        self.button = button
        self.button2 = button2
        self.button3 = button3
        self.text_btn = button4
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None
        self.stroke_fill_color = None
        self.font = None
        self.font = None
        self.layer_height = None

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [0, 100]

    def update_pen(self, pen):
        self.pen = pen

    def update_stroke_fill_color(self, color):
        self.stroke_fill_color = color

    def update_font(self, font, color):
        self.font = font
        self.font_color = color

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.button.isChecked():

            self.on_path_draw_start(event)

        # Check if the Line and Label tool is turned on
        elif self.button2.isChecked():
            self.on_label_start(event)

        elif self.text_btn.isChecked():
            self.on_add_text(event)

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
        if self.button.isChecked():
            self.on_path_draw(event)

        # Check if the line and label tool is enabled
        elif self.button2.isChecked():
            self.on_label(event)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Check if path tool is enabled
        if self.button.isChecked():
            self.on_path_draw_end(event)

        # Check if the line and label tool is enabled
        elif self.button2.isChecked():
            self.on_label_end(event)

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
            if self.button3.isChecked():
                self.temp_path_item.setBrush(QBrush(QColor(self.stroke_fill_color)))
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

            # If stroke fill button is checked, set the brush
            if self.button3.isChecked():
                path_item.setBrush(QBrush(QColor(self.stroke_fill_color)))

            # Add item
            add_command = AddItemCommand(self.canvas, path_item)
            self.canvas.addCommand(add_command)

            # Set Flags
            path_item.setFlag(QGraphicsItem.ItemIsSelectable)
            path_item.setFlag(QGraphicsItem.ItemIsMovable)

            # Set Tooltop
            path_item.setToolTip('MPRUN Path Element')

            # Check if item is selected or moved so we can turn tool off
            if self.canvas.selectedItems():
                self.button.setChecked(False)
                self.setDragMode(QGraphicsView.RubberBandDrag)

    def on_label_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create the leader line
            self.leader_line = QPainterPath()  # Create a new QPainterPath
            self.leader_line.moveTo(self.mapToScene(event.pos()))
            self.setDragMode(QGraphicsView.NoDrag)

            # Create the label text
            self.label_text = EditableTextBlock('An Editable Text Block')
            self.label_text.setFont(self.font)
            self.label_text.setPos(self.mapToScene(event.pos()))
            self.label_text.setDefaultTextColor(QColor('black'))
            self.label_text.setToolTip(
                "Partially locked text block (This item's position is determined by the position of another element)")

            # Create the bounding rectangle around the text (for style)
            self.text_box_rect = CustomRectangleItem(self.label_text.boundingRect())
            self.text_box_rect.setPen(self.pen)
            self.text_box_rect.setPos(self.mapToScene(event.pos()))

            # Set z values
            self.text_box_rect.stackBefore(self.label_text)

            add_command = AddItemCommand(self.canvas, self.text_box_rect)
            self.canvas.addCommand(add_command)
            add_command2 = AddItemCommand(self.canvas, self.label_text)
            self.canvas.addCommand(add_command2)

            self.canvas.update()

    def on_label(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            # Move line to current coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))

            self.canvas.update()

    def on_label_end(self, event):
        # Check buttons
        if event.button() == Qt.LeftButton:
            # Move line to current mouse coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))
            self.canvas.update()

            # Draw circle at the end of path
            scene_pos = self.mapToScene(event.pos())
            circle = CustomCircleItem(scene_pos.x() - 3, scene_pos.y() - 3, 6, 6)
            circle.setZValue(0)
            circle.setPen(self.pen)

            self.canvas.update()

            # Load path as QGraphicsItem, set parent items
            path_item = CustomPathItem(self.leader_line)
            path_item.setPen(self.pen)
            path_item.setZValue(0)
            path_item.setFlag(QGraphicsItem.ItemIsSelectable)
            path_item.stackBefore(circle)
            path_item.setParentItem(circle)
            self.text_box_rect.setParentItem(circle)
            self.label_text.setParentItem(circle)

            # Add items (no need to add rect, circle, and label because parent is path_item)
            add_command = AddItemCommand(self.canvas, circle)
            self.canvas.addCommand(add_command)

            # Set flags
            circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            path_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent)
            self.label_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

            # Set Tooltips for elements
            path_item.setToolTip('Leader Line Element')
            circle.setToolTip('Leader Line End Element')

            # Check if item is selected or moved so we can turn tool off
            if self.canvas.selectedItems():
                self.button2.setChecked(False)
                self.setDragMode(QGraphicsView.RubberBandDrag)

    def on_add_text(self, event):
        pos = self.mapToScene(event.pos())

        text = EditableTextBlock('Lorem Ipsum')
        text.setFont(self.font)
        text.setDefaultTextColor(self.font_color)

        add_command = AddItemCommand(self.canvas, text)
        self.canvas.addCommand(add_command)

        text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        text.setZValue(0)
        text.setPos(pos)

        text = None

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, undoStack):
        super().__init__()
        self.undo_stack = undoStack

        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    def addCommand(self, command):
        self.undo_stack.push(command)

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class SmoothPathCommand(QUndoCommand):
    def __init__(self, scene, item, new_path, old_path):
        super().__init__()
        self.scene = scene
        self.item = item
        self.new_path = new_path
        self.old_path = old_path

    def redo(self):
        self.item.setPath(self.new_path)

    def undo(self):
        self.item.setPath(self.old_path)

class EditTextCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text):
        super().__init__()
        self.item = item
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        self.item.setText(self.new_text)

    def undo(self):
        self.item.setText(self.old_text)

class ScaleCommand(QUndoCommand):
    def __init__(self, item, old_scale, new_scale):
        super().__init__()
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def redo(self):
        self.item.setScale(self.new_scale)

    def undo(self):
        self.item.setScale(self.old_scale)

class TransformXScaleCommand(QUndoCommand):
    def __init__(self, item, old_scale, new_scale):
        super().__init__()
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def redo(self):
        transform = QTransform()
        transform.scale(self.new_scale, 1.0)
        self.item.setTransform(transform)

    def undo(self):
        transform = QTransform()
        transform.scale(self.old_scale, 1.0)
        self.item.setTransform(transform)

class TransformYScaleCommand(QUndoCommand):
    def __init__(self, item, old_scale, new_scale):
        super().__init__()
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def redo(self):
        transform = QTransform()
        transform.scale(1.0, self.new_scale)
        self.item.setTransform(transform)

    def undo(self):
        transform = QTransform()
        transform.scale(1.0, self.old_scale)
        self.item.setTransform(transform)

class RotateCommand(QUndoCommand):
    def __init__(self, item, old_rotation, new_rotation):
        super().__init__()
        self.item = item
        self.old_value = old_rotation
        self.new_value = new_rotation

    def redo(self):
        self.item.setRotation(self.new_value)

    def undo(self):
        self.item.setRotation(self.old_value)

class OpacityCommand(QUndoCommand):
    def __init__(self, item, old_opacity, new_opacity):
        super().__init__()
        self.item = item
        self.old_value = old_opacity
        self.new_value = new_opacity

    def redo(self):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(self.new_value)
        self.item.setGraphicsEffect(effect)

    def undo(self):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(self.old_value)
        self.item.setGraphicsEffect(effect)

class HideCommand(QUndoCommand):
    def __init__(self, item, old_visible, new_visible):
        super().__init__()
        self.item = item
        self.old_value = old_visible
        self.new_value = new_visible

    def redo(self):
        self.item.setVisible(self.new_value)

    def undo(self):
        self.item.setVisible(self.old_value)

class NameCommand(QUndoCommand):
    def __init__(self, item, old_name, new_name):
        super().__init__()
        self.item = item
        self.old_value = old_name
        self.new_value = new_name

    def redo(self):
        self.item.setToolTip(self.new_value)

    def undo(self):
        self.item.setToolTip(self.old_value)






