from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import math

class PathEditorGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.sculpting_item_offset = QPointF()
        self.undo_stack = QUndoStack(self)
        self.initial_path = None
        self.sculpt_radius = 10  # Radius for sculpting tool
        self.setRenderHint(QPainter.Antialiasing)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_sculpt_start(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.on_sculpt(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_sculpt_end(event)
        super().mouseReleaseEvent(event)

    def on_sculpt_start(self, event):
        pos = self.mapToScene(event.pos())
        item, point_index, offset = self.find_closest_point(pos)
        if item is not None:
            self.sculpting_item = item
            self.sculpting_item_point_index = point_index
            self.sculpting_item_offset = offset
            self.initial_path = item.path()  # Store the initial path before editing

    def on_sculpt(self, event):
        if self.sculpting_item is not None and self.sculpting_item_point_index != -1:
            pos = self.mapToScene(event.pos()) - self.sculpting_item_offset
            self.update_path_points_in_radius(self.sculpting_item, self.sculpting_item_point_index, pos, self.sculpt_radius)

    def on_sculpt_end(self, event):
        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.initial_path = None

    def find_closest_point(self, pos):
        min_dist = float('inf')
        closest_item = None
        closest_point_index = -1
        closest_offset = QPointF()

        for item in self.scene().items():
            if isinstance(item, QGraphicsPathItem):
                path = item.path()
                for i in range(path.elementCount()):
                    point = path.elementAt(i)
                    point_pos = QPointF(point.x, point.y)
                    dist = dist = ((pos.x() - point_pos.x())**2 + (pos.y() - point_pos.y())**2)**.5
                    if dist < min_dist and dist < 50:  # threshold for selection
                        min_dist = dist
                        closest_item = item
                        closest_point_index = i
                        closest_offset = pos - point_pos

        return closest_item, closest_point_index, closest_offset

    def update_path_points_in_radius(self, item, index, new_pos, radius):
        path = item.path()
        elements = [path.elementAt(i) for i in range(path.elementCount())]

        # Update the central point
        if index < 0 or index >= len(elements):
            return

        elements[index].x = new_pos.x()
        elements[index].y = new_pos.y()

        # Update points within the radius
        for i in range(len(elements)):
            if math.sqrt((elements[i].x - elements[index].x) ** 2 + (elements[i].y - elements[index].y) ** 2) <= radius:
                elements[i].x = new_pos.x() + (elements[i].x - elements[index].x)
                elements[i].y = new_pos.y() + (elements[i].y - elements[index].y)

        new_path = QPainterPath()
        new_path.moveTo(elements[0].x, elements[0].y)

        i = 1
        while i < len(elements):
            if i + 2 < len(elements):
                new_path.cubicTo(elements[i].x, elements[i].y,
                                 elements[i+1].x, elements[i+1].y,
                                 elements[i+2].x, elements[i+2].y)
                i += 3
            else:
                new_path.lineTo(elements[i].x, elements[i].y)
                i += 1

        item.setPath(new_path)

app = QApplication(sys.argv)
scene = QGraphicsScene()
view = PathEditorGraphicsView()
view.setScene(scene)

# Example path item
path = QPainterPath()
path.moveTo(50, 50)
path.cubicTo(70, 100, 130, 0, 150, 50)
path.cubicTo(70, 100, 130, 0, 150, 50)
path.cubicTo(170, 100, 230, 0, 250, 50)
path.cubicTo(270, 100, 330, 0, 350, 50)
path.cubicTo(370, 100, 430, 0, 450, 50)
path.cubicTo(470, 100, 530, 0, 550, 50)
path.cubicTo(570, 100, 630, 0, 650, 50)
path.cubicTo(670, 100, 730, 0, 750, 50)
path_item = QGraphicsPathItem(path)
scene.addItem(path_item)

# if we move the position of the path at all, the tool no longer works
path_item.setPos(100, 100)

view.show()
sys.exit(app.exec_())