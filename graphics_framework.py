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

    def add_curve_to_point(self, endPoint):
        if self.lastPoint is not None:
            # Calculate control points
            controlPoint1 = self.last_point
            controlPoint2 = endPoint
            # Add curve to QPainterPath
            self.path.quadTo(controlPoint1, (self.lastPoint + controlPoint2) / 2)

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

            self.canvas.addItem(self.label_text)
            self.canvas.addItem(self.text_box_rect)

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
            path_item.stackBefore(circle)
            path_item.setParentItem(circle)
            self.text_box_rect.setParentItem(circle)
            self.label_text.setParentItem(circle)

            # Add items (no need to add rect, circle, and label because parent is path_item)
            self.canvas.addItem(circle)

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

        self.canvas.addItem(text)

        text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        text.setZValue(0)
        text.setPos(pos)

        text = None
