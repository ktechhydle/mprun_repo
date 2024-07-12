from src.scripts.imports import *
from src.framework.undo_commands import *
from src.framework.custom_classes import *

class PathDrawerTool:
    def __init__(self, canvas, view):
        self.canvas = canvas
        self.view = view
        self.temp_path_item = None
        self.path = None
        self.last_point = None

    def show_tooltip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path:
            QToolTip.showText(p, f'path length: {int(self.path.length())} pt')

    def on_path_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.view.mapToScene(event.pos()))
            self.last_point = self.view.mapToScene(event.pos())

            # Set drag mode
            self.view.setDragMode(QGraphicsView.NoDrag)

    def on_path_draw(self, event):
        # Check the buttons
        if event.buttons() == Qt.LeftButton:
            self.path.lineTo(self.view.mapToScene(event.pos()))
            self.last_point = self.view.mapToScene(event.pos())

            # Remove temporary path if it exists
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            # Load temporary path as QGraphicsItem to view it while drawing
            self.temp_path_item = CustomPathItem(self.path)
            self.temp_path_item.setPen(self.view.pen)
            self.temp_path_item.setBrush(self.view.stroke_fill)
            self.temp_path_item.setZValue(0)
            self.canvas.addItem(self.temp_path_item)

            self.canvas.update()

    def on_path_draw_end(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            self.path.lineTo(self.view.mapToScene(event.pos()))
            self.last_point = self.view.mapToScene(event.pos())

            # Check if there is a temporary path (if so, remove it now)
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            self.canvas.update()

            # Load main path as QGraphicsItem
            path_item = CustomPathItem(self.path)
            path_item.setPen(self.view.pen)
            path_item.setZValue(1)
            path_item.setBrush(self.view.stroke_fill)
            path_item.setFlag(QGraphicsItem.ItemIsSelectable)
            path_item.setFlag(QGraphicsItem.ItemIsMovable)
            path_item.setToolTip('Path')

            # Add item
            if path_item.path().isEmpty():
                self.canvas.removeItem(path_item)

            else:
                add_command = AddItemCommand(self.canvas, path_item)
                self.canvas.addCommand(add_command)

            self.temp_path_item = None
            self.path = None
            self.last_point = None

class PenDrawerTool:
    def __init__(self, canvas, view):
        self.canvas = canvas
        self.view = view
        self.path = None
        self.temp_path_item = None
        self.last_point = None

    def show_tooltip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path:
            QToolTip.showText(p, f'path length: {int(self.path.length())} pt')

    def on_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.view.mapToScene(event.pos()))
            self.last_point = self.view.mapToScene(event.pos())

            # Set drag mode
            self.view.setDragMode(QGraphicsView.NoDrag)

    def on_draw(self, event):
        if self.path is not None:
            # Check the buttons
            if event.buttons() == Qt.LeftButton:
                self.path.lineTo(self.view.mapToScene(event.pos()))

                # Remove temporary path if it exists
                if self.temp_path_item is not None:
                    self.canvas.removeItem(self.temp_path_item)

                # Load temporary path as QGraphicsItem to view it while drawing
                self.path.setFillRule(Qt.WindingFill)
                self.temp_path_item = CustomPathItem(self.path)
                self.temp_path_item.path().setFillRule(Qt.WindingFill)
                self.temp_path_item.setPen(self.view.pen)
                self.temp_path_item.setBrush(self.view.stroke_fill)
                self.temp_path_item.setZValue(1)
                self.canvas.addItem(self.temp_path_item)

                try:
                    if event.modifiers() & Qt.ShiftModifier:
                        self.temp_path_item.simplify(self.last_point, self.view.mapToScene(event.pos()))
                        self.path = self.temp_path_item.path()
                    else:
                        self.temp_path_item.setPath(self.temp_path_item.smooth_path(self.temp_path_item.path(), 0.75))

                except Exception:
                    pass

                self.canvas.update()

    def on_draw_end(self, event):
        if self.path is not None:
            if self.path.isEmpty():
                return

            else:
                # Check the buttons
                if event.button() == Qt.LeftButton:
                    self.path.lineTo(self.view.mapToScene(event.pos()))

                    # Check if there is a temporary path (if so, remove it now)
                    if self.temp_path_item is not None:
                        self.canvas.removeItem(self.temp_path_item)

                    self.canvas.update()

                    # Load main path as QGraphicsItem
                    path_item = CustomPathItem(self.path)
                    path_item.path().setFillRule(Qt.WindingFill)
                    path_item.setPen(self.view.pen)
                    path_item.setZValue(0)
                    path_item.setBrush(self.view.stroke_fill)
                    path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                    path_item.setFlag(QGraphicsItem.ItemIsMovable)
                    path_item.setToolTip('Path')

                    try:
                        if event.modifiers() & Qt.ShiftModifier:
                            path_item.simplify(self.last_point, self.view.mapToScene(event.pos()))
                            self.path = self.temp_path_item.path()
                        else:
                            path_item.setPath(path_item.smooth_path(path_item.path(), 0.1))

                    except Exception:
                        pass

                    # Add item
                    if path_item.path().isEmpty():
                        self.canvas.removeItem(path_item)

                    else:
                        add_command = AddItemCommand(self.canvas, path_item)
                        self.canvas.addCommand(add_command)

                    self.path = None
                    self.temp_path_item = None
                    self.last_point = None

class LineAndLabelTool:
    def __init__(self, canvas, view):
        self.canvas = canvas
        self.view = view
        self.label_drawing = False
        self.start_point = None

    def on_label_start(self, event):
        if event.button() == Qt.LeftButton:
            self.label_drawing = True
            self.start_point = self.view.mapToScene(event.pos())
            self.leader_line = QPainterPath()
            self.leader_line.moveTo(self.start_point)
            self.view.setDragMode(QGraphicsView.NoDrag)
            self.clicked_label_point = self.start_point

            self.pathg_item = LeaderLineItem(self.leader_line, 'Lorem Ipsum')
            self.pathg_item.setPen(self.view.pen)
            self.pathg_item.setBrush(self.view.stroke_fill)
            self.pathg_item.text_element.setFont(self.view.font)
            self.pathg_item.text_element.setPos(self.start_point - QPointF(0, self.pathg_item.text_element.boundingRect().height()))

            self.canvas.addItem(self.pathg_item)
            self.canvas.update()

    def on_label(self, event):
        if self.label_drawing:
            current_point = self.view.mapToScene(event.pos())
            temp_line = QPainterPath()
            temp_line.moveTo(self.start_point)
            temp_line.lineTo(current_point)
            self.pathg_item.setPath(temp_line)
            self.pathg_item.updatePathEndPoint()
            self.pathg_item.update()
            self.canvas.update()

    def on_label_end(self, event):
        if event.button() == Qt.LeftButton and self.label_drawing:
            self.label_drawing = False
            end_point = self.view.mapToScene(event.pos())
            self.leader_line.lineTo(end_point)
            self.pathg_item.setPath(self.leader_line)
            self.canvas.update()

            self.pathg_item.setZValue(2)
            self.pathg_item.text_element.select_text_and_set_cursor()

            if self.leader_line.isEmpty():
                self.view.scene().removeItem(self.pathg_item)

            else:
                command = AddItemCommand(self.canvas, self.pathg_item)
                self.canvas.addCommand(command)

            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

            self.pathg_item.setToolTip('Leader Line')
            self.pathg_item.updatePathEndPoint()

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
        self.view.setDragMode(QGraphicsView.NoDrag)
        pos = self.view.mapToScene(event.pos())
        item = self.canvas.itemAt(pos.toPoint(), self.view.transform())
        if item and not isinstance(item, CanvasItem):
            if isinstance(item, CustomTextItem):
                item.clearFocus()

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

    def on_scale_double_click(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.canvas.itemAt(pos.toPoint(), self.view.transform())
        if item and not isinstance(item, CanvasItem):
            if isinstance(item, CustomTextItem):
                item.clearFocus()

            if item.scale() == 1:
                pass
            else:
                self.canvas.addCommand(ScaleCommand(item, item.scale(), 1))

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

class AddCanvasTool:
    def __init__(self, canvas, view):
        self.canvas = canvas
        self.view = view
        self.temp_canvas = None
        self.canvas_item = None

    def on_add_canvas_start(self, event):
        if event.button() == Qt.LeftButton:
            item_under_mouse = self.view.itemAt(event.pos())

            if item_under_mouse is None:  # No item under mouse, create new CanvasItem
                self.view.setDragMode(QGraphicsView.NoDrag)

                self.clicked_canvas_point = self.view.mapToScene(event.pos())
                self.canvas_item = CanvasItem(QRectF(0, 0, 1, 1), f'Canvas {self.view.scene().canvas_count}')
                self.canvas_item.setPos(self.clicked_canvas_point)

                self.canvas.addItem(self.canvas_item)
            else:
                pass

    def on_add_canvas_drag(self, event):
        if self.canvas_item is not None and event.buttons() & Qt.LeftButton and self.clicked_canvas_point is not None:
            current_pos = self.view.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & Qt.ShiftModifier:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.canvas_item.setRect(0, 0, width, height)

            point = event.pos()
            p = self.view.mapToGlobal(point)
            p.setY(p.y())
            p.setX(p.x() + 10)
            QToolTip.showText(p, f'''width: {int(self.canvas_item.rect().width())} 
height: {int(self.canvas_item.rect().height())}''')

    def on_add_canvas_end(self, event):
        if self.canvas_item is not None and event.button() == Qt.LeftButton:
            current_pos = self.view.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & Qt.ShiftModifier:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.canvas_item.setRect(0, 0, width, height)
            self.canvas_item.setPos(self.clicked_canvas_point)
            self.canvas_item.setToolTip(f'Canvas {self.view.scene().canvas_count}')
            self.canvas_item.setZValue(-1)
            self.canvas_item.setCanvasActive(True)
            self.view.scene().addItem(self.canvas_item.text)

            if self.canvas_item.rect().isEmpty():
                self.view.scene().removeItem(self.canvas_item)
                self.view.scene().removeItem(self.canvas_item.text)

            else:
                command = AddItemCommand(self.view.scene(), self.canvas_item)
                self.canvas.addCommand(command)

            self.canvas_item = None
            self.clicked_canvas_point = None

            self.canvas.update()



