from src.scripts.imports import *
from src.framework.undo_commands import *
from src.framework.items import *


class Tool(object):
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        self.scene = scene
        self.view = view

    def specialToolTip(self, event):
        pass

    def mousePress(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseRelease(self, event):
        pass

    def mouseDoublePress(self, event):
        pass


class DrawingTool(Tool):
    """Base class to handle common functionality for drawing tools."""

    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.path = None
        self.temp_path_item = None
        self.last_point = None

    def createNewPath(self, event):
        """Initializes a new path at the event position."""
        self.path = QPainterPath()
        self.path.setFillRule(Qt.FillRule.WindingFill)
        self.path.moveTo(self.view.mapToScene(event.pos()))
        self.last_point = self.view.mapToScene(event.pos())

    def addPathToScene(self, path_item):
        """Adds the given path item to the scene and sets necessary properties."""
        path_item.setPen(self.scene.parentWindow.properties_tab.getPen())
        path_item.setBrush(self.scene.parentWindow.properties_tab.getBrush())
        path_item.setZValue(1)
        path_item.setFlag(ITEM_SELECTABLE)
        path_item.setFlag(ITEM_MOVABLE)
        self.scene.addItem(path_item)

    def removeTemporaryPath(self):
        """Removes the temporary path item from the scene, if it exists."""
        if self.temp_path_item:
            self.scene.removeItem(self.temp_path_item)
        self.temp_path_item = None

    def showPathLengthToolTip(self, event):
        """Displays the length of the current path in a tooltip."""
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path:
            QToolTip.showText(p, f'path length: {int(self.path.length())} pt')
        else:
            self.view.show_tooltip(event)


class PathDrawerTool(Tool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.path_item = None

    def specialToolTip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path_item:
            QToolTip.showText(p, f'path length: {int(self.path_item.path().length())} pt')
        else:
            self.view.show_tooltip(event)

    def mousePress(self, event):
        if event.button() == LEFT_BUTTON:
            path = QPainterPath()
            path.moveTo(self.view.mapToScene(event.pos()))

            self.path_item = CustomPathItem(path)
            self.path_item.setPath(path)
            self.path_item.setPen(self.scene.parentWindow.properties_tab.getPen())
            self.path_item.setBrush(self.scene.parentWindow.properties_tab.getBrush())
            self.path_item.setZValue(1)

            self.scene.addItem(self.path_item)
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

    def mouseMove(self, event):
        if event.buttons() == LEFT_BUTTON and self.path_item:
            path = self.path_item.path()
            path.lineTo(self.view.mapToScene(event.pos()))

            self.path_item.setPath(path)

    def mouseRelease(self, event):
        if event.button() == LEFT_BUTTON and self.path_item:
            self.path_item.path().lineTo(self.view.mapToScene(event.pos()))
            self.path_item.setFlag(ITEM_SELECTABLE)
            self.path_item.setFlag(ITEM_MOVABLE)

            if not self.path_item.path().isEmpty():
                add_command = AddItemCommand(self.scene, self.path_item)
                self.scene.addCommand(add_command)

            self.path_item = None


class LineAndLabelTool(Tool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.label_drawing = False
        self.start_point = None

    def mousePress(self, event):
        if event.button() == LEFT_BUTTON:
            self.label_drawing = True
            self.start_point = self.view.mapToScene(event.pos())
            self.leader_line = QPainterPath()
            self.leader_line.moveTo(self.start_point)

            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.pathg_item = LeaderLineItem(self.leader_line, 'Lorem Ipsum')
            self.addLabelToScene()

    def mouseMove(self, event):
        if self.label_drawing:
            current_point = self.view.mapToScene(event.pos())
            temp_line = QPainterPath()
            temp_line.moveTo(self.start_point)
            temp_line.lineTo(current_point)
            self.pathg_item.setPath(temp_line)
            self.view.update()

    def mouseRelease(self, event):
        if event.button() == LEFT_BUTTON and self.label_drawing:
            self.label_drawing = False
            end_point = self.view.mapToScene(event.pos())
            self.leader_line.lineTo(end_point)
            self.pathg_item.setPath(self.leader_line)
            self.scene.update()
            self.finalizeLabel()

    def addLabelToScene(self):
        self.pathg_item.setZValue(2)
        self.pathg_item.setPos(self.pathg_item.pos().x() - self.pathg_item.boundingRect().width(),
                               self.pathg_item.pos().y())
        self.pathg_item.setPen(self.scene.parentWindow.properties_tab.getPen())
        self.pathg_item.setBrush(self.scene.parentWindow.properties_tab.getBrush())
        self.pathg_item.text_element.setFont(self.scene.parentWindow.characters_tab.getFont())
        self.pathg_item.text_element.setDefaultTextColor(self.scene.parentWindow.characters_tab.getFontColor())
        self.pathg_item.text_element.setTextAlignment(self.scene.parentWindow.characters_tab.getFontAlignment())
        self.pathg_item.text_element.setPos(
            self.start_point - QPointF(0, self.pathg_item.text_element.boundingRect().height()))
        self.scene.addItem(self.pathg_item)

    def finalizeLabel(self):
        self.pathg_item.text_element.selectTextAndSetCursor()
        if not self.leader_line.isEmpty():
            command = AddItemCommand(self.scene, self.pathg_item)
            self.scene.addCommand(command)
            self.pathg_item.setFlag(ITEM_SELECTABLE)
            self.pathg_item.setFlag(ITEM_MOVABLE)
            self.pathg_item.setToolTip('Leader Line')
        else:
            self.scene.removeItem(self.pathg_item)


class PathSculptingTool(Tool):
    def __init__(self, scene, view):
        super().__init__(scene, view)

        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.sculpting_item_offset = QPointF()
        self.sculpt_shape = QGraphicsEllipseItem(0, 0, 100, 100)
        self.sculpt_shape.setZValue(10000)
        self.sculpting_initial_path = None
        self.sculpt_radius = 100

    def mousePress(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.view.scene().itemAt(pos, self.view.transform())

        if isinstance(item, CustomPathItem):
            pos_in_item_coords = item.mapFromScene(pos)
            self.sculpting_item = item
            self.sculpting_item_point_index, self.sculpting_item_offset = self.findClosestPoint(pos_in_item_coords,
                                                                                                item)
            self.sculpting_initial_path = QPainterPath(item.path())  # Make a deep copy of the path

            print(f"Sculpt Start: Item ID {id(item)}, Point Index {self.sculpting_item_point_index}")

        self.scene.addItem(self.sculpt_shape)
        self.sculpt_shape.setPos(pos - self.sculpt_shape.boundingRect().center())

    def mouseMove(self, event):
        if self.sculpting_item is not None and self.sculpting_item_point_index != -1:
            pos = self.view.mapToScene(event.pos())
            pos_in_item_coords = self.sculpting_item.mapFromScene(pos) - self.sculpting_item_offset
            self.updatePathPoint(self.sculpting_item, self.sculpting_item_point_index, pos_in_item_coords)
            print(f"Sculpt: Item ID {id(self.sculpting_item)}, Point Index {self.sculpting_item_point_index}")

        self.sculpt_shape.setPos(self.view.mapToScene(event.pos()) - self.sculpt_shape.boundingRect().center())

    def mouseRelease(self, event):
        if self.sculpting_item is not None:
            new_path = self.sculpting_item.path()
            if new_path != self.sculpting_initial_path:
                command = EditPathCommand(self.sculpting_item, self.sculpting_initial_path, new_path)
                self.scene.addCommand(command)
                print(f"Sculpt End: Item ID {id(self.sculpting_item)}")

        self.resetSculptingState()

    def mouseDoublePress(self, event):
        pos = self.view.mapToScene(event.pos())
        item = self.view.scene().itemAt(pos, self.view.transform())

        if isinstance(item, CustomPathItem):
            pos_in_item_coords = item.mapFromScene(pos)
            point_index, offset = self.findClosestPoint(pos_in_item_coords, item)
            if point_index != -1:
                self.smoothPathPoint(item, point_index)

    def findClosestPoint(self, pos, item):
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

    def updatePathPoint(self, item, index, new_pos):
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
        new_path.setFillRule(Qt.FillRule.WindingFill)
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

    def smoothPathPoint(self, item, point_index):
        path = item.path()
        elements = [path.elementAt(i) for i in range(path.elementCount())]

        if point_index > 0 and point_index + 1 < len(elements):
            smoothed_x = (elements[point_index - 1].x + elements[point_index + 1].x) / 2
            smoothed_y = (elements[point_index - 1].y + elements[point_index + 1].y) / 2

            path.setElementPositionAt(point_index, smoothed_x, smoothed_y)

            command = EditPathCommand(item, item.path(), path)
            self.scene.addCommand(command)
            item.smooth = False

    def resetSculptingState(self):
        self.sculpting_item = None
        self.sculpting_item_point_index = -1
        self.sculpting_initial_path = None
        self.sculpting_item_offset = QPointF()
        self.scene.removeItem(self.sculpt_shape)

    def setSculptRadius(self, value):
        self.sculpt_radius = value
        self.sculpt_shape.setRect(0, 0, value, value)


class AddCanvasTool(Tool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.temp_canvas = None
        self.scene_item = None

    def specialToolTip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.scene_item:
            QToolTip.showText(p, f'''width: {int(self.scene_item.rect().width())} 
height: {int(self.scene_item.rect().height())}''')

        else:
            self.view.show_tooltip(event)

    def mousePress(self, event):
        if event.button() == LEFT_BUTTON:
            item_under_mouse = self.view.itemAt(event.pos())

            if item_under_mouse is None:  # No item under mouse, create new CanvasItem
                self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

                self.clicked_canvas_point = self.view.mapToScene(event.pos())
                self.scene_item = CanvasItem(QRectF(0, 0, 1, 1), f'Canvas {self.view.scene().canvas_count}')
                self.scene_item.setPos(self.clicked_canvas_point)

                self.scene.addItem(self.scene_item)
            else:
                pass

    def mouseMove(self, event):
        if self.scene_item is not None and event.buttons() & LEFT_BUTTON and self.clicked_canvas_point is not None:
            current_pos = self.view.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & SHIFT_MODIFIER:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.scene_item.setRect(0, 0, width, height)

    def mouseRelease(self, event):
        if self.scene_item is not None and event.button() == LEFT_BUTTON:
            current_pos = self.view.mapToScene(event.pos())
            width = current_pos.x() - self.clicked_canvas_point.x()
            height = current_pos.y() - self.clicked_canvas_point.y()

            if QApplication.keyboardModifiers() & SHIFT_MODIFIER:  # Check if 'C' key is pressed
                # Constrain the size to maintain aspect ratio (assuming 1:1 for simplicity)
                size = min(abs(width), abs(height))
                width = size if width >= 0 else -size
                height = size if height >= 0 else -size

            self.scene_item.setRect(0, 0, width, height)
            self.scene_item.setPos(self.clicked_canvas_point)
            self.scene_item.setToolTip(f'Canvas {self.view.scene().canvas_count}')
            self.scene_item.setZValue(-1)
            self.scene_item.setCanvasActive(True)
            self.view.scene().addItem(self.scene_item.text)

            if self.scene_item.rect().isEmpty():
                self.view.scene().removeItem(self.scene_item)
                self.view.scene().removeItem(self.scene_item.text)

            else:
                command = AddItemCommand(self.view.scene(), self.scene_item)
                self.scene.addCommand(command)

            self.scene_item = None
            self.clicked_canvas_point = None

            self.scene.update()
