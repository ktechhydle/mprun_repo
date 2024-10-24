from src.scripts.imports import *
from src.framework.undo_commands import *
from src.framework.course_element_builder.course_element_builder_items import *


class BaseTool(object):
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


class LipTool(BaseTool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.start_pos = None
        self.path_item = None

    def specialToolTip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path_item:
            QToolTip.showText(p, f'''width: {int(self.path_item.rectBox().width())}\nheight: {int(
                self.path_item.rectBox().height())}''')

    def mousePress(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.start_pos is None:
                # First click: Set start position and create a rectangle item
                self.start_pos = self.view.mapToScene(event.pos())
                self.path_item = LipItem(QRectF(self.start_pos, self.start_pos))
                self.path_item.setPen(self.view.parent().properties_tab.getPen())
                self.path_item.setBrush(self.view.parent().properties_tab.getBrush())
                self.scene.addItem(self.path_item)
            else:
                # Second click: Finalize the rectangle
                self.updateRect(event)  # Final update on second click
                command = AddItemCommand(self.scene, self.path_item)
                self.scene.addCommand(command)
                self.start_pos = None
                self.path_item = None

    def mouseMove(self, event):
        if self.start_pos is not None and self.path_item is not None:
            # If start_pos is set, update the preview rectangle as the mouse moves
            self.updateRect(event)

    def updateRect(self, event):
        # Calculate the new rectangle based on start_pos and current mouse position
        current_pos = self.view.mapToScene(event.pos())
        rect = QRectF(self.start_pos, current_pos).normalized()  # Ensure the rectangle has positive width/height
        self.path_item.setRect(rect)

    def mouseRelease(self, event):
        pass

    def cancel(self):
        """Cancels the current tool operation and removes the rectangle."""
        if self.path_item:
            # Remove the rectangle from the scene
            self.scene.removeItem(self.path_item)
            self.path_item = None
            self.start_pos = None

        QToolTip.hideText()


class LineTool(BaseTool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.start_pos = None
        self.path_item = None

    def specialToolTip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path_item:
            QToolTip.showText(p,
                              f'x: {int(self.path_item.lineBox().p2().x())}\ny: {int(self.path_item.lineBox().p2().y())}')

    def mousePress(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.start_pos is None:
                # First click: Set start position and create a rectangle item
                self.start_pos = self.view.mapToScene(event.pos())
                self.path_item = LineItem(QLineF(self.start_pos, self.start_pos))
                self.path_item.setPen(self.view.parent().properties_tab.getPen())
                self.path_item.setBrush(self.view.parent().properties_tab.getBrush())
                self.scene.addItem(self.path_item)
            else:
                # Second click: Finalize the rectangle
                self.updateLine(event)  # Final update on second click
                command = AddItemCommand(self.scene, self.path_item)
                self.scene.addCommand(command)
                self.start_pos = None
                self.path_item = None

    def mouseMove(self, event):
        if self.start_pos is not None and self.path_item is not None:
            # If start_pos is set, update the preview rectangle as the mouse moves
            self.updateLine(event)

    def updateLine(self, event):
        # Calculate the new line based on start_pos and current mouse position
        current_pos = self.view.mapToScene(event.pos())
        line = QLineF(self.start_pos, current_pos)

        # Check if Shift is pressed for snapping
        if event.modifiers() & Qt.ShiftModifier:
            # Calculate angle in radians
            dx = current_pos.x() - self.start_pos.x()
            dy = current_pos.y() - self.start_pos.y()
            angle = math.atan2(dy, dx)

            # Snap to the nearest 45 degrees (pi/4 radians)
            snap_angle = round(angle / (math.pi / 4)) * (math.pi / 4)

            # Recalculate end point based on the snapped angle and original line length
            length = line.length()
            new_dx = math.cos(snap_angle) * length
            new_dy = math.sin(snap_angle) * length
            snapped_pos = self.start_pos + QPointF(new_dx, new_dy)

            # Update the line with the snapped position
            line.setP2(snapped_pos)

        # Update the path_item with the new line
        self.path_item.setLine(line)

    def mouseRelease(self, event):
        pass

    def cancel(self):
        """Cancels the current tool operation and removes the rectangle."""
        if self.path_item:
            # Remove the rectangle from the scene
            self.scene.removeItem(self.path_item)
            self.path_item = None
            self.start_pos = None

        QToolTip.hideText()


class ArcTool(BaseTool):
    def __init__(self, scene, view):
        super().__init__(scene, view)
        self.start_pos = None
        self.end_pos = None
        self.arc_point = None
        self.path_item = None
        self.click_count = 0  # To track which click (1st, 2nd, 3rd)

    def specialToolTip(self, event):
        point = event.pos()
        p = self.view.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)

        if self.path_item:
            QToolTip.showText(p,
                              f'x: {int(self.path_item.lineBox().p2().x())}\ny: {int(self.path_item.lineBox().p2().y())}')

    def mousePress(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.click_count == 0:
                # First click: Set start position
                self.start_pos = self.view.mapToScene(event.pos())
                self.path_item = ArcItem(QLineF(self.start_pos, self.start_pos), self.start_pos)
                self.path_item.setPen(self.view.parent().properties_tab.getPen())
                self.path_item.setBrush(self.view.parent().properties_tab.getBrush())
                self.scene.addItem(self.path_item)
                self.click_count += 1
            elif self.click_count == 1:
                # Second click: Set end position
                self.end_pos = self.view.mapToScene(event.pos())
                self.path_item.setLine(QLineF(self.start_pos, self.end_pos))
                self.click_count += 1
            elif self.click_count == 2:
                # Third click: Set arc control point and finalize the arc
                self.arc_point = self.view.mapToScene(event.pos())
                self.path_item.setArcPoint(self.arc_point)

                # Finalize the arc by adding a command
                command = AddItemCommand(self.scene, self.path_item)
                self.scene.addCommand(command)

                # Reset everything for the next arc
                self.start_pos = None
                self.end_pos = None
                self.arc_point = None
                self.path_item = None
                self.click_count = 0

    def mouseMove(self, event):
        if self.click_count == 1 and self.start_pos is not None:
            # After the first click, update the end point (second click) as the mouse moves
            current_pos = self.view.mapToScene(event.pos())
            self.path_item.setLine(QLineF(self.start_pos, current_pos))
        elif self.click_count == 2 and self.end_pos is not None:
            # After the second click, update the control point (third click) as the mouse moves
            current_pos = self.view.mapToScene(event.pos())
            self.path_item.setArcPoint(current_pos)

    def mouseRelease(self, event):
        pass

    def cancel(self):
        """Cancels the current tool operation and removes the arc."""
        if self.path_item:
            # Remove the arc from the scene
            self.scene.removeItem(self.path_item)
            self.path_item = None
            self.start_pos = None
            self.end_pos = None
            self.arc_point = None
            self.click_count = 0
        QToolTip.hideText()

