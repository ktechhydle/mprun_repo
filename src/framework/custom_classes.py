from src.scripts.imports import *
from src.framework.undo_commands import *

class item_stack:
    def __init__(self, initial_value=""):
        self._value = initial_value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

class CustomGraphicsItemGroup(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()
        self.mouse_offset = QPoint(0, 0)
        self.block_size = 10

        self.locked = False
        self.stored_items = None

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def store_items(self, items):
        self.stored_items = items

    def duplicate(self):
        # Create a new instance of CustomGraphicsItemGroup
        group = CustomGraphicsItemGroup()

        # Set position, scale, and rotation
        group.setPos(self.pos() + QPointF(10, 10))
        group.setScale(self.scale())
        group.setRotation(self.rotation())
        group.setZValue(self.zValue())
        group.setTransform(self.transform())
        group.setTransformOriginPoint(self.transformOriginPoint())

        # Set flags and tooltip
        group.setFlag(QGraphicsItem.ItemIsSelectable)
        group.setFlag(QGraphicsItem.ItemIsMovable)
        group.setToolTip('Group')

        # Add the new item to the scene
        add_command = AddItemCommand(self.scene(), group)
        self.scene().addCommand(add_command)

        for items in self.childItems():
            copy = items.duplicate()

            # Add items to group
            group.addToGroup(copy)

        return group

class CustomRectangleItem(QGraphicsRectItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def duplicate(self):
        rect = self.rect()

        item = CustomRectangleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Rectangle')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CustomCircleItem(QGraphicsEllipseItem):
    def __init__(self, *coords):
        super().__init__(*coords)

    def duplicate(self):
        rect = self.rect()

        item = CustomCircleItem(rect)
        item.setPen(self.pen())
        item.setPos(self.pos())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(0)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Ellipse')

        if self.childItems():
            for child in self.childItems():
                copy = child.duplicate()

                if isinstance(copy, CustomTextItem):
                    pass

                else:
                    copy.setFlag(QGraphicsItem.ItemIsMovable, False)
                    copy.setFlag(QGraphicsItem.ItemIsSelectable, False)

                copy.setParentItem(item)

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CustomPathItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

        path.setFillRule(Qt.WindingFill)

        self.smooth = False

        self.text_items = []
        self.add_text = False
        self.text_along_path = ''
        self.text_along_path_font = QFont('Arial', 20)
        self.text_along_path_color = QColor('black')
        self.text_along_path_spacing = 3
        self.start_text_from_beginning = False

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())
            self.setPos(x, y)
        else:
            super().mouseMoveEvent(event)

    def duplicate(self):
        path = self.path()
        item = CustomPathItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos() + QPointF(10, 10))
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setTransformOriginPoint(self.transformOriginPoint())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Path')

        if self.add_text:
            item.add_text = True
            item.setTextAlongPathFromBeginning(self.start_text_from_beginning)
            item.setTextAlongPath(self.text_along_path)
            item.setTextAlongPathSpacingFromPath(self.text_along_path_spacing)
            item.setTextAlongPathFont(self.text_along_path_font)
            item.setTextAlongPathColor(self.text_along_path_color)

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def smooth_path(self, path, tolerance: float):
        vertices = [(point.x(), point.y()) for point in path.toSubpathPolygons()[0]]
        x, y = zip(*vertices)

        wl = 21
        po = 3

        # Apply Savitzky-Golay filter for smoothing
        smooth_x = savgol_filter(x, window_length=wl, polyorder=po)
        smooth_y = savgol_filter(y, window_length=wl, polyorder=po)

        smoothed_vertices = np.column_stack((smooth_x, smooth_y))
        simplified_vertices = approximate_polygon(smoothed_vertices, tolerance=tolerance)

        smooth_path = QPainterPath()
        smooth_path.setFillRule(Qt.WindingFill)
        smooth_path.moveTo(simplified_vertices[0][0], simplified_vertices[0][1])

        for i in range(1, len(simplified_vertices) - 2, 3):
            smooth_path.cubicTo(
                simplified_vertices[i][0], simplified_vertices[i][1],
                simplified_vertices[i + 1][0], simplified_vertices[i + 1][1],
                simplified_vertices[i + 2][0], simplified_vertices[i + 2][1]
            )

        self.smooth = True

        return smooth_path

    def setTextAlongPathFromBeginning(self, a0):
        self.start_text_from_beginning = a0

    def setTextAlongPath(self, text):
        self.text_along_path = text
        self.update()

    def setTextAlongPathFont(self, font):
        self.text_along_path_font = font
        self.update()

    def setTextAlongPathColor(self, color):
        self.text_along_path_color = color
        self.update()

    def setTextAlongPathSpacingFromPath(self, spacing):
        self.text_along_path_spacing = spacing
        self.update()

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        if self.add_text:
            path = self.path()
            text = self.text_along_path
            pen = painter.pen()
            pen.setWidth(self.text_along_path_spacing)
            pen.setColor(self.text_along_path_color)
            painter.setPen(pen)
            font = self.text_along_path_font
            painter.setFont(font)

            font_metrics = QFontMetricsF(font)
            total_length = path.length()
            current_length = 0

            if self.start_text_from_beginning:
                for char in text:
                    char_width = font_metrics.width(char)
                    if current_length + char_width > total_length:
                        break  # Stop adding more text if the current length exceeds the path length

                    percent = current_length / total_length
                    point = path.pointAtPercent(percent)
                    angle = path.angleAtPercent(percent)

                    painter.save()
                    painter.translate(point)
                    painter.rotate(-angle)
                    painter.drawText(QPointF(0, -pen.width()), char)
                    painter.restore()

                    current_length += char_width
            else:
                percent_increase = 1 / (len(text) + 1)
                percent = 0

                for char in text:
                    percent += percent_increase
                    point = path.pointAtPercent(percent)
                    angle = path.angleAtPercent(percent)

                    painter.save()
                    painter.translate(point)
                    painter.rotate(-angle)
                    painter.drawText(QPointF(0, -pen.width()), char)
                    painter.restore()

class CustomPixmapItem(QGraphicsPixmapItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return self.filename

    def duplicate(self):
        pixmap = QPixmap(self.return_filename())

        item = CustomPixmapItem(pixmap)
        item.setPos(self.pos() + QPointF(10, 10))
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.store_filename(self.return_filename())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Imported Pixmap')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.return_filename()))

class CustomSvgItem(QGraphicsSvgItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None
        self.render = QSvgRenderer(file)

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def store_filename(self, file):
        self.filename = file

    def source(self):
        return self.filename

    def duplicate(self):
        svg = self.source()

        item = CustomSvgItem(svg)
        item.setPos(self.pos() + QPointF(10, 10))
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.store_filename(svg)

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Imported SVG')

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.return_filename()))

class CustomTextItem(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setToolTip('Text')
        self.locked = False
        self.setAcceptHoverEvents(True)
        self.gridEnabled = False
        self.old_text = self.toPlainText()
        self.markdownEnabled = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_offset = event.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            if self.hasFocus():
                super().mouseMoveEvent(event)

            else:
                # Calculate the position relative to the scene's coordinate system
                scene_pos = event.scenePos()
                x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
                y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

                # Set the position relative to the scene's coordinate system
                self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.locked == False:
            if event.button() == Qt.LeftButton:
                self.setTextInteractionFlags(Qt.TextEditorInteraction)
                self.setFocus(Qt.MouseFocusReason)
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)

        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() == Qt.Key_Escape:
            self.clearFocus()

        if isinstance(self.parentItem(), LeaderLineItem):
            self.parentItem().updatePathEndPoint()

    def focusOutEvent(self, event):
        new_text = self.toPlainText()
        if self.old_text != new_text:
            edit_command = EditTextCommand(self, self.old_text, new_text)
            self.scene().addCommand(edit_command)
            self.old_text = new_text

            if isinstance(self.parentItem(), LeaderLineItem):
                self.parentItem().updatePathEndPoint()

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def set_locked(self):
        self.locked = True

    def duplicate(self):
        item = CustomTextItem()
        item.setFont(self.font())
        item.setDefaultTextColor(self.defaultTextColor())
        item.setPos(self.pos() + QPointF(10, 10))
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setTransformOriginPoint(self.transformOriginPoint())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Text')

        if self.markdownEnabled:
            item.markdownEnabled = True
            item.setPlainText(self.old_text)
            item.old_text = item.toPlainText()
            item.toMarkdown()

        else:
            item.setPlainText(self.toPlainText())

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

    def select_text_and_set_cursor(self):
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.SelectionType.Document)
        self.setTextCursor(cursor)

    def set_active(self):
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.MouseFocusReason)

    def toMarkdown(self):
        html_text = markdown.markdown(self.toPlainText())

        self.setHtml(html_text)
        self.markdownEnabled = True
        self.set_locked()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and isinstance(self.parentItem(), LeaderLineItem):
            self.parentItem().updatePathEndPoint()
        return super().itemChange(change, value)

class LeaderLineItem(QGraphicsPathItem):
    def __init__(self, path, text: str):
        super().__init__(path)

        self.gridEnabled = False
        self.text_element = CustomTextItem(text)
        self.text_element.setParentItem(self)
        self.text_element.setToolTip("Text")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        painter.setPen(self.pen())
        painter.setBrush(self.brush())

        mapped_rect = self.mapRectFromItem(self.text_element, self.text_element.boundingRect())
        painter.drawRect(mapped_rect)

        try:
            painter.setPen(self.pen())
            painter.setBrush(QBrush(QColor(self.pen().color().name())))

            path = self.path()
            if path.elementCount() > 1:
                # Get the last two points of the path
                last_element = path.elementAt(path.elementCount() - 1)
                second_last_element = path.elementAt(path.elementCount() - 2)
                last_point = QPointF(last_element.x, last_element.y)
                second_last_point = QPointF(second_last_element.x, second_last_element.y)

                # Calculate the angle of the line segment at the end of the path
                dx = last_point.x() - second_last_point.x()
                dy = last_point.y() - second_last_point.y()
                angle = math.atan2(dy, dx)

                # Calculate the new endpoint slightly beyond the last point
                arrow_offset = 10  # Distance to extend the arrowhead beyond the last point
                end_point = QPointF(last_point.x() + arrow_offset * math.cos(angle),
                                    last_point.y() + arrow_offset * math.sin(angle))

                # Define the arrowhead points
                arrow_size = 12
                p1 = QPointF(end_point.x() - arrow_size * math.cos(angle - math.pi / 6),
                             end_point.y() - arrow_size * math.sin(angle - math.pi / 6))
                p2 = QPointF(end_point.x() - arrow_size * math.cos(angle + math.pi / 6),
                             end_point.y() - arrow_size * math.sin(angle + math.pi / 6))

                # Create a polygon for the arrowhead
                arrow_head = QPolygonF([end_point, p1, p2])

                # Draw the arrowhead
                painter.drawPolygon(arrow_head)

        except Exception as e:
            print(e)

    def updatePathEndPoint(self):
        path = self.path()
        if path.elementCount() > 0:
            last_element_index = path.elementCount() - 1
            end_point = QPointF(path.elementAt(last_element_index).x, path.elementAt(last_element_index).y)
            text_rect = self.text_element.boundingRect()

            # Determine the closest corner of the text bounding rect to the end_point
            top_left = self.mapFromItem(self.text_element, text_rect.topLeft())
            top_right = self.mapFromItem(self.text_element, text_rect.topRight())
            bottom_left = self.mapFromItem(self.text_element, text_rect.bottomLeft())
            bottom_right = self.mapFromItem(self.text_element, text_rect.bottomRight())

            corners = {
                'top_left': top_left,
                'top_right': top_right,
                'bottom_left': bottom_left,
                'bottom_right': bottom_right
            }

            closest_corner = min(corners, key=lambda corner: (corners[corner] - end_point).manhattanLength())
            new_start_point = corners[closest_corner]

            path.setElementPositionAt(0, new_start_point.x(), new_start_point.y())
            self.setPath(path)

    def duplicate(self):
        path = self.path()

        item = LeaderLineItem(path, self.text_element.toPlainText())
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos() + QPointF(10, 10))
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setTransformOriginPoint(self.transformOriginPoint())

        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setToolTip('Leader Line')

        item.text_element.setFont(self.text_element.font())
        item.text_element.setDefaultTextColor(self.text_element.defaultTextColor())
        item.text_element.setTransform(self.text_element.transform())
        item.text_element.setRotation(self.text_element.rotation())
        item.text_element.setPos(self.text_element.pos())

        item.updatePathEndPoint()

        add_command = AddItemCommand(self.scene(), item)
        self.scene().addCommand(add_command)

        return item

class CanvasItem(QGraphicsRectItem):
    def __init__(self, coords: QRectF, name):
        super().__init__(coords)

        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, Qt.SolidLine)
        pen.setWidthF(0)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setBrush(brush)
        self.setPen(pen)
        self.setToolTip(name)
        self.text = CanvasTextItem(name, self)
        self.text.setVisible(False)
        self.text.setZValue(10000)
        self.active = False
        self.setAcceptHoverEvents(True)

        self.gridEnabled = False
        self.setZValue(-1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)

    def setName(self, name):
        self.text.setPlainText(name)
        self.update()

    def name(self):
        return self.text.toPlainText()

    def canvasActive(self):
        return self.active

    def setCanvasActive(self, enabled: bool):
        self.scene().setBackgroundBrush(QBrush(QColor('#737373')))
        self.setFlag(QGraphicsItem.ItemIsMovable, enabled)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled)
        self.text.setVisible(enabled)
        self.active = enabled
        self.setCursor(Qt.SizeAllCursor)
        if enabled is False:
            self.scene().setBackgroundBrush(QBrush(QColor('#606060')))
            self.setCursor(Qt.CursorShape.ArrowCursor)
            brush = QBrush(QColor('white'))
            pen = QPen(QColor('white'), 2, Qt.SolidLine)
            pen.setWidthF(0)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            self.setBrush(brush)
            self.setPen(pen)

        for item in self.scene().items():
            if isinstance(item, CanvasItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsSelectable, not enabled)
                item.setFlag(QGraphicsItem.ItemIsMovable, not enabled)

    def setTransparentMode(self):
        b = self.brush()
        p = self.pen()
        b.setColor(QColor(Qt.transparent))
        p.setColor(QColor(Qt.transparent))

        self.setBrush(b)
        self.setPen(p)

    def restore(self):
        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, Qt.SolidLine)
        pen.setWidthF(0)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setBrush(brush)
        self.setPen(pen)

class CanvasTextItem(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__()

        self.setPos(parent.boundingRect().x(), parent.boundingRect().y())
        self.setParentItem(parent)
        self.setPlainText(text)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.setZValue(10000)

        font = QFont()
        font.setFamily('Helvetica')
        font.setPixelSize(20)

        self.setFont(font)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor('#dcdcdc')))
        painter.setPen(QPen(QColor('black')))
        painter.drawRect(self.boundingRect())

        super().paint(painter, option, widget)

class ControlPoint(QGraphicsEllipseItem):
    positionChanged = pyqtSignal()

    def __init__(self, x, y, parent=None):
        super().__init__(-5, -5, 10, 10, parent)
        self.setBrush(QBrush(Qt.blue))
        self.setPen(QPen(Qt.black))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.positionChanged.emit()
        return super().itemChange(change, value)

class WaterMarkItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.gridEnabled:
            # Calculate the position relative to the scene's coordinate system
            scene_pos = event.scenePos()
            x = (int(scene_pos.x() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.x())
            y = (int(scene_pos.y() / self.scene().gridSize) * self.scene().gridSize - self.mouse_offset.y())

            # Set the position relative to the scene's coordinate system
            self.setPos(x, y)

        else:
            super().mouseMoveEvent(event)


