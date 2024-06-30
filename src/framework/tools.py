from src.scripts.imports import *
from src.framework.undo_commands import *
from src.framework.custom_classes import *

class MouseScalingTool:
    def __init__(self, canvas: QGraphicsScene, view: QGraphicsView):
        self.canvas = canvas
        self.view = view
        self.scaling_item = None
        self.scaling_item_initial_scale = None
        self.scaling_command = None
        self.start_pos = None

        self.view.setMouseTracking(True)

    def on_scale_start(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.canvas.itemAt(pos.toPoint(), self.view.transform())
        if item and not isinstance(item, CanvasItem):
            self.scaling_item = item
            self.scaling_item_initial_scale = item.scale()
            self.start_pos = pos


    def on_scale(self, event):
        if self.scaling_item and self.start_pos:
            current_pos = self.view.mapToScene(event.pos())
            delta = current_pos - self.start_pos
            scale_factor = 1 + delta.y() / 100.0  # Adjust the scale sensitivity here

            # Scale around the center of the item
            self.scaling_item.setTransformOriginPoint(self.scaling_item.boundingRect().center())

            new_scale = self.scaling_item.scale() * scale_factor
            self.scaling_item.setScale(new_scale)

            self.scaling_command = ScaleCommand(self.scaling_item, self.scaling_item_initial_scale, new_scale)

            self.start_pos = current_pos

            if (isinstance(self.scaling_item, CustomTextItem) and
                    isinstance(self.scaling_item.parentItem(), LeaderLineItem)):
                self.scaling_item.parentItem().updatePathEndPoint()

    def on_scale_end(self, event):
        if self.scaling_command:
            self.canvas.addCommand(self.scaling_command)

        self.scaling_item = None
        self.scaling_item_initial_scale = None
        self.start_pos = None
        self.scaling_command = None

class PathSculptingTool:
    def __init__(self, canvas, view):
        self.canvas = canvas
        self.view = view

        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.sculpting_item_offset = QPointF()
        self.sculpt_shape = QGraphicsEllipseItem(0, 0, 100, 100)
        self.sculpt_shape.setZValue(10000)
        self.sculpting_initial_path = None
        self.sculpt_radius = 100

    def on_sculpt_start(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.view.scene().itemAt(pos, self.view.transform())

        if isinstance(item, CustomPathItem):
            pos_in_item_coords = item.mapFromScene(pos)
            self.sculpting_item = item
            self.sculpting_item_point_index, self.sculpting_item_offset = self.find_closest_point(pos_in_item_coords,
                                                                                                  item)
            self.sculpting_initial_path = QPainterPath(item.path())  # Make a deep copy of the path

            print(f"Sculpt Start: Item ID {id(item)}, Point Index {self.sculpting_item_point_index}")

        self.canvas.addItem(self.sculpt_shape)
        self.sculpt_shape.setPos(pos - self.sculpt_shape.boundingRect().center())

    def on_sculpt(self, event):
        if self.sculpting_item is not None and self.sculpting_item_point_index != -1:
            pos = self.view.mapToScene(event.pos())
            pos_in_item_coords = self.sculpting_item.mapFromScene(pos) - self.sculpting_item_offset
            self.update_path_point(self.sculpting_item, self.sculpting_item_point_index, pos_in_item_coords)
            print(f"Sculpt: Item ID {id(self.sculpting_item)}, Point Index {self.sculpting_item_point_index}")

        self.sculpt_shape.setPos(self.view.mapToScene(event.pos()) - self.sculpt_shape.boundingRect().center())

    def on_sculpt_end(self, event):
        if self.sculpting_item is not None:
            new_path = self.sculpting_item.path()
            if new_path != self.sculpting_initial_path:
                command = EditPathCommand(self.sculpting_item, self.sculpting_initial_path, new_path)
                self.canvas.addCommand(command)
                print(f"Sculpt End: Item ID {id(self.sculpting_item)}")

        self.reset_sculpting_state()

    def on_sculpt_double_click(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.view.scene().itemAt(pos, self.view.transform())

        if isinstance(item, CustomPathItem):
            pos_in_item_coords = item.mapFromScene(pos)
            point_index, offset = self.find_closest_point(pos_in_item_coords, item)
            if point_index != -1:
                self.smooth_path_point(item, point_index)

    def find_closest_point(self, pos, item):
        path = item.path()
        min_dist = float('inf')
        closest_point_index = -1
        closest_offset = QPointF()

        for i in range(path.elementCount()):
            point = path.elementAt(i)
            point_pos = QPointF(point.x, point.y)
            dist = QLineF(point_pos, pos).length()

            if dist < min_dist:
                min_dist = dist
                closest_point_index = i
                closest_offset = pos - point_pos

        return closest_point_index, closest_offset

    def update_path_point(self, item, index, new_pos):
        path = item.path()
        elements = [path.elementAt(i) for i in range(path.elementCount())]

        if index < 0 or index >= len(elements):
            return  # Ensure the index is within bounds

        old_pos = QPointF(elements[index].x, elements[index].y)
        delta_pos = new_pos - old_pos

        def calculate_influence(dist, radius):
            return math.exp(-(dist ** 2) / (2 * (radius / 2.0) ** 2))

        for i in range(len(elements)):
            point = elements[i]
            point_pos = QPointF(point.x, point.y)
            dist = QLineF(point_pos, old_pos).length()

            if dist <= self.sculpt_radius:
                influence = calculate_influence(dist, self.sculpt_radius)
                elements[i].x += delta_pos.x() * influence
                elements[i].y += delta_pos.y() * influence

        new_path = QPainterPath()
        new_path.setFillRule(Qt.WindingFill)
        new_path.moveTo(elements[0].x, elements[0].y)

        i = 1
        while i < len(elements):
            if i + 2 < len(elements):
                new_path.cubicTo(elements[i].x, elements[i].y,
                                 elements[i + 1].x, elements[i + 1].y,
                                 elements[i + 2].x, elements[i + 2].y)
                i += 3
            else:
                new_path.lineTo(elements[i].x, elements[i].y)
                i += 1

        item.setPath(new_path)
        item.smooth = False

    def smooth_path_point(self, item, point_index):
        path = item.path()
        elements = [path.elementAt(i) for i in range(path.elementCount())]

        if point_index > 0 and point_index + 1 < len(elements):
            smoothed_x = (elements[point_index - 1].x + elements[point_index + 1].x) / 2
            smoothed_y = (elements[point_index - 1].y + elements[point_index + 1].y) / 2

            path.setElementPositionAt(point_index, smoothed_x, smoothed_y)

            command = EditPathCommand(item, item.path(), path)
            self.canvas.addCommand(command)
            item.smooth = False

    def reset_sculpting_state(self):
        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.sculpting_initial_path = None
        self.sculpting_item_offset = QPointF()
        self.canvas.removeItem(self.sculpt_shape)

    def set_sculpt_radius(self, value):
        self.sculpt_radius = value
        self.sculpt_shape.setRect(0, 0, value, value)
