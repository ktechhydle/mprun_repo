import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class EditablePathItem(QGraphicsPathItem):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPath(path)
        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPathItem.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)
        self.selected_point = None

    def mousePressEvent(self, event):
        point = self.closest_point(event.pos())
        if point is not None:
            self.selected_point = point
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selected_point is not None:
            path = self.path()
            new_path = QPainterPath()
            for i in range(path.elementCount()):
                element = path.elementAt(i)
                if i == self.selected_point:
                    new_path.lineTo(event.pos())
                else:
                    new_path.lineTo(QPointF(element.x, element.y))
            self.setPath(new_path)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.selected_point = None
        super().mouseReleaseEvent(event)

    def closest_point(self, pos):
        threshold = 10.0  # pixels
        path = self.path()
        closest_point_index = None
        min_distance = float('inf')

        for i in range(path.elementCount()):
            element = path.elementAt(i)
            point = QPointF(element.x, element.y)
            distance = (pos - point).manhattanLength()
            if distance < min_distance and distance < threshold:
                min_distance = distance
                closest_point_index = i

        return closest_point_index


app = QApplication(sys.argv)
scene = QGraphicsScene()
view = QGraphicsView(scene)
view.setRenderHint(QPainter.Antialiasing)

path = QPainterPath()
path.moveTo(50, 50)
path.lineTo(150, 50)
path.lineTo(150, 150)
path.lineTo(50, 150)
path.closeSubpath()

path_item = EditablePathItem(path)
path_item.setPen(QPen(Qt.black, 2))
scene.addItem(path_item)

view.show()
sys.exit(app.exec_())
