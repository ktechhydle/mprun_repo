import os
from scipy.signal import savgol_filter
from mprun.constants import *
from src.scripts.imports import *
from src.framework.undo_commands import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class ResizeOrb(QGraphicsEllipseItem):
    handleTopMiddle = 2
    handleMiddleRight = 5

    handleSize = 8

    handleCursors = {
        handleTopMiddle: Qt.CursorShape.OpenHandCursor,
        handleMiddleRight: Qt.CursorShape.SizeAllCursor,
    }

    def __init__(self, parent):
        super().__init__()
        self.setParentItem(parent)
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(QColor('#000000'), 3))

        self.updateOrb()

        # Item resizing
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.ogTransform = []
        self.updateHandlesPos()

    def setParentItem(self, parent):
        self.parent_item = parent

    def parentItem(self):
        return self.parent_item

    def shape(self):
        # Create a path for the ellipse
        path = QPainterPath()
        path.addEllipse(self.rect())

        # Use QPainterPathStroker to create the outline
        stroker = QPainterPathStroker()
        stroker.setWidth(2)

        path = stroker.createStroke(path)

        if hasattr(self, 'handles'):
            for rect in self.handles.values():
                path.addRect(rect)

        return path

    def boundingRect(self):
        return self.rect()

    def setFlag(self, flag, enabled=True):
        pass

    def setFlags(self, flags):
        pass

    def mousePressEvent(self, event):
        self.handleSelected = self.handleAt(event.pos())
        if self.handleSelected:
            self.mousePressPos = event.pos()
            self.mousePressRect = self.parentItem().boundingRect()
            self.ogTransform = [self.parentItem().scale(), self.parentItem().rotation()]

    def mouseMoveEvent(self, event):
        if self.handleSelected is not None:
            self.interactiveResize(event.pos())

    def mouseReleaseEvent(self, mouseEvent):
        super().mouseReleaseEvent(mouseEvent)

        if self.ogTransform:
            self.scene().addCommand(OrbTransformCommand(self.parentItem(),
                                                        self.ogTransform,
                                                        [self.parentItem().scale(),
                                                         self.parentItem().rotation()]
                                                        ))

        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None

        self.updateOrb()

    def mouseDoubleClickEvent(self, event):
        self.handleSelected = self.handleAt(event.pos())

        if self.handleSelected:
            if self.handleSelected == self.handleTopMiddle:
                if self.parentItem().rotation() != 0:
                    self.scene().addCommand(RotateCommand(None,
                                                          [self.parentItem()],
                                                          [self.parentItem().rotation()],
                                                          0))
            elif self.handleSelected == self.handleMiddleRight:
                if self.parentItem().scale() != 0:
                    self.scene().addCommand(ScaleCommand(self.parentItem(), self.parentItem().scale(), 1))

    def hoverMoveEvent(self, moveEvent):
        handle = self.handleAt(moveEvent.pos())
        cursor = Qt.CursorShape.ArrowCursor if handle is None else self.handleCursors[handle]
        self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        self.unsetCursor()
        super().hoverLeaveEvent(moveEvent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        grip_color = QColor('#4f7fff')
        grip_pen = QPen(QColor('#4f7fff'), 1)
        grip_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(grip_pen)
        painter.setBrush(grip_color)

        for handle, rect in self.handles.items():
            painter.drawRect(rect)

            self.updateHandlesPos()

        if self.handleSelected:
            painter.setPen(QColor('#000000'))

            rotate_handle_text = f'{int(self.parentItem().rotation())}°'
            scale_handle_text = f'{int(self.parentItem().scale() * 100)}%'

            if self.handleSelected == self.handleTopMiddle:
                painter.drawText(QPointF(self.currentHandle().x() - len(rotate_handle_text),
                                         self.currentHandle().y() - 5), rotate_handle_text)

            elif self.handleSelected == self.handleMiddleRight:
                painter.drawText(self.currentHandle().bottomRight() + QPointF(5, 0),
                                 scale_handle_text)

    def interactiveResize(self, mousePos):
        """ Perform shape interactive resize or rotation based on the selected handle. """
        self.parentItem().prepareGeometryChange()

        if not self.parentItem().transformOriginPoint():
            self.parentItem().setTransformOriginPoint(self.parentItem().boundingRect().center())

        if self.handleSelected is not None:
            dx = mousePos.x() - self.mousePressPos.x()
            dy = mousePos.y() - self.mousePressPos.y()

            if self.handleSelected == self.handleTopMiddle:
                # Calculate rotation
                center = self.mousePressRect.center()
                current_angle = math.atan2(mousePos.y() - center.y(), mousePos.x() - center.x())
                start_angle = math.atan2(self.mousePressPos.y() - center.y(), self.mousePressPos.x() - center.x())
                angle_diff = math.degrees(current_angle - start_angle)
                new_rotation = self.parentItem().rotation() + angle_diff

                # Snap to 15-degree increments if Shift is held
                if QApplication.keyboardModifiers() & SHIFT_MODIFIER:
                    new_rotation = round(new_rotation / 15) * 15

                self.parentItem().setRotation(new_rotation)

            elif self.handleSelected == self.handleMiddleRight:
                rect = self.mousePressRect.center()

                # Calculate scale
                start_distance = math.hypot(self.mousePressPos.x() - rect.x(),
                                            self.mousePressPos.y() - rect.y())
                current_distance = math.hypot(mousePos.x() - rect.x(),
                                              mousePos.y() - rect.y())
                scale_factor = current_distance / start_distance
                new_scale = self.parentItem().scale() * scale_factor

                self.parentItem().setScale(new_scale)

        self.updateHandlesPos()

    def currentHandle(self) -> QRectF:
        if self.handleSelected:
            return self.handles[self.handleSelected]

        return None

    def handleAt(self, point):
        for f, v in self.handles.items():
            if v.contains(point):
                return f

        return None

    def updateHandlesPos(self):
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)

    def updateOrb(self):
        self.setTransformOriginPoint(self.parentItem().transformOriginPoint())
        self.setScale(self.parentItem().scale())
        self.setRotation(self.parentItem().rotation())

        # Get the adjusted bounding rect
        rect = self.parentItem().boundingRect().adjusted(-20, -20, 20, 20)

        # Ensure the rectangle is a square
        size = max(rect.width(), rect.height())  # Use the larger dimension to make it a square
        center = rect.center()

        # Create a new square rect centered on the original rect
        square_rect = QRectF(
            center.x() - size / 2,
            center.y() - size / 2,
            size,
            size
        )

        # Set the rect and position
        self.setPos(self.parentItem().pos())
        self.setRect(square_rect.normalized())

        if self.scene():
            if self.parentItem() not in self.scene().items():
                self.setVisible(False)

        # Update the item
        self.update()


class CustomPathItem(QGraphicsPathItem):
    def __init__(self, path):
        super().__init__(path)

        path.setFillRule(Qt.FillRule.WindingFill)

        self.smooth = False

    def duplicate(self):
        item = self.copy()
        item.moveBy(10, 10)

        return item

    def copy(self):
        path = self.path()
        item = CustomPathItem(path)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setAlreadySmooth(self.alreadySmooth())
        item.setOpacity(self.opacity())

        item.setFlag(ITEM_SELECTABLE)
        item.setFlag(ITEM_MOVABLE)
        item.setToolTip('Path')

        return item

    def simplify(self, old_pos, new_pos):
        path = self.path()
        path.clear()
        path.moveTo(old_pos)
        path.lineTo(new_pos)

        self.setPath(path)

    def approximate_polygon(self, coords, tolerance):
        """
        COPIED FROM SKIMAGE ON GITHUB (https://github.com/scikit-image/scikit-image/blob/v0.24.0/skimage/measure/_polygon.py#L5-L91)

        Approximate a polygonal chain with the specified tolerance.

        It is based on the Douglas-Peucker algorithm.

        Note that the approximated polygon is always within the convex hull of the
        original polygon.

        Parameters
        ----------
        coords : (K, 2) array
            Coordinate array.
        tolerance : float
            Maximum distance from original points of polygon to approximated
            polygonal chain. If tolerance is 0, the original coordinate array
            is returned.

        Returns
        -------
        coords : (L, 2) array
            Approximated polygonal chain where L <= K.

        References
        ----------
        .. [1] https://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
        """
        if tolerance <= 0:
            return coords

        chain = np.zeros(coords.shape[0], 'bool')
        # pre-allocate distance array for all points
        dists = np.zeros(coords.shape[0])
        chain[0] = True
        chain[-1] = True
        pos_stack = [(0, chain.shape[0] - 1)]
        end_of_chain = False

        while not end_of_chain:
            start, end = pos_stack.pop()
            # determine properties of current line segment
            r0, c0 = coords[start, :]
            r1, c1 = coords[end, :]
            dr = r1 - r0
            dc = c1 - c0
            segment_angle = -np.arctan2(dr, dc)
            segment_dist = c0 * np.sin(segment_angle) + r0 * np.cos(segment_angle)

            # select points in-between line segment
            segment_coords = coords[start + 1: end, :]
            segment_dists = dists[start + 1: end]

            # check whether to take perpendicular or euclidean distance with
            # inner product of vectors

            # vectors from points -> start and end
            dr0 = segment_coords[:, 0] - r0
            dc0 = segment_coords[:, 1] - c0
            dr1 = segment_coords[:, 0] - r1
            dc1 = segment_coords[:, 1] - c1
            # vectors points -> start and end projected on start -> end vector
            projected_lengths0 = dr0 * dr + dc0 * dc
            projected_lengths1 = -dr1 * dr - dc1 * dc
            perp = np.logical_and(projected_lengths0 > 0, projected_lengths1 > 0)
            eucl = np.logical_not(perp)
            segment_dists[perp] = np.abs(
                segment_coords[perp, 0] * np.cos(segment_angle)
                + segment_coords[perp, 1] * np.sin(segment_angle)
                - segment_dist
            )
            segment_dists[eucl] = np.minimum(
                # distance to start point
                np.sqrt(dc0[eucl] ** 2 + dr0[eucl] ** 2),
                # distance to end point
                np.sqrt(dc1[eucl] ** 2 + dr1[eucl] ** 2),
            )

            if np.any(segment_dists > tolerance):
                # select point with maximum distance to line
                new_end = start + np.argmax(segment_dists) + 1
                pos_stack.append((new_end, end))
                pos_stack.append((start, new_end))
                chain[new_end] = True

            if len(pos_stack) == 0:
                end_of_chain = True

        return coords[chain, :]

    def smooth_path(self, path, tolerance: float):
        vertices = [(point.x(), point.y()) for point in path.toSubpathPolygons()[0]]
        x, y = zip(*vertices)

        wl = 21
        po = 3

        # Apply Savitzky-Golay filter for smoothing
        smooth_x = savgol_filter(x, window_length=wl, polyorder=po)
        smooth_y = savgol_filter(y, window_length=wl, polyorder=po)

        smoothed_vertices = np.column_stack((smooth_x, smooth_y))
        simplified_vertices = self.approximate_polygon(smoothed_vertices, tolerance=tolerance)

        smooth_path = QPainterPath()
        smooth_path.setFillRule(Qt.FillRule.WindingFill)
        smooth_path.moveTo(simplified_vertices[0][0], simplified_vertices[0][1])

        for i in range(1, len(simplified_vertices) - 2, 3):
            smooth_path.cubicTo(
                simplified_vertices[i][0], simplified_vertices[i][1],
                simplified_vertices[i + 1][0], simplified_vertices[i + 1][1],
                simplified_vertices[i + 2][0], simplified_vertices[i + 2][1]
            )

        self.setAlreadySmooth(True)

        return smooth_path

    def setAlreadySmooth(self, smooth: bool):
        self.smooth = smooth

    def alreadySmooth(self):
        return self.smooth


class CustomPixmapItem(QGraphicsPixmapItem):
    def __init__(self, file):
        super().__init__(file)

        self.filename = None

    def loadFromData(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.setPixmap(pixmap)

    def store_filename(self, file):
        self.filename = file

    def return_filename(self):
        return self.filename

    def duplicate(self):
        item = self.copy()
        item.moveBy(10, 10)

        return item

    def copy(self):
        item = CustomPixmapItem(self.pixmap())
        item.setPos(self.pos())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())

        if os.path.exists(self.return_filename()):
            item.store_filename(self.return_filename())
        else:
            item.store_filename(None)

        item.setFlag(ITEM_SELECTABLE)
        item.setFlag(ITEM_MOVABLE)
        item.setOpacity(self.opacity())

        return item


class CustomSvgItem(QGraphicsSvgItem):
    def __init__(self, *file):
        super().__init__(*file)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.filename = ''
        self.svg_data = None
        for f in file:
            self.render = QSvgRenderer(f)

    def loadFromData(self, svg_data) -> None:
        try:
            self.svg_data = svg_data
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            self.setSharedRenderer(renderer)
            self.setElementId("")  # Optional: set specific SVG element ID if needed
        except Exception as e:
            print(f"Error in loadFromData: {e}")

    def svgData(self) -> str:
        if self.svg_data is not None:
            return self.svg_data

    def store_filename(self, file):
        self.filename = file

    def source(self):
        return self.filename

    def duplicate(self):
        item = self.copy()
        item.moveBy(10, 10)

        return item

    def copy(self):
        svg = self.source()

        if os.path.exists(svg):
            item = CustomSvgItem(svg)
            item.setPos(self.pos())
            item.setTransformOriginPoint(self.transformOriginPoint())
            item.setScale(self.scale())
            item.setRotation(self.rotation())
            item.setZValue(self.zValue())
            item.setTransform(self.transform())
            item.setOpacity(self.opacity())
            item.store_filename(svg)

            item.setFlag(ITEM_SELECTABLE)
            item.setFlag(ITEM_MOVABLE)
            item.setToolTip('Imported SVG')

        else:
            item = CustomSvgItem()
            item.loadFromData(self.svgData())
            item.setPos(self.pos())
            item.setTransformOriginPoint(self.transformOriginPoint())
            item.setScale(self.scale())
            item.setRotation(self.rotation())
            item.setZValue(self.zValue())
            item.setTransform(self.transform())
            item.setOpacity(self.opacity())

            item.setFlag(ITEM_SELECTABLE)
            item.setFlag(ITEM_MOVABLE)
            item.setToolTip('Imported SVG')

        return item


class CustomTextItem(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setToolTip('Text')
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.installEventFilter(self)

        # Text editing
        self.locked = False
        self.editing = False
        self.old_text = self.toPlainText()
        self.text_alignment = None

        # Create the suggestion popup
        self.suggestion_popup = QListWidget()
        self.suggestion_popup.setToolTip('<i>Press the up-arrow key to accept suggestions</i>')
        self.suggestion_popup.setObjectName('searchList')
        self.suggestion_popup.setFixedWidth(250)
        self.suggestion_popup.setFixedHeight(100)
        self.suggestion_popup.setWindowFlags(WINDOW_TYPE_POPUP)

        self.trick_types = []

        with open('internal data/_tricks.txt', 'r') as f:
            for line in f.readlines():
                self.trick_types.append(line.strip())

    def mouseDoubleClickEvent(self, event):
        if self.locked == False:
            if self.editing:
                super().mouseDoubleClickEvent(event)

            if event.button() == LEFT_BUTTON:
                self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                self.setFocus(Qt.FocusReason.MouseFocusReason)
                self.editing = True
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)

        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if hasattr(self, 'resize_orb'):
            self.resize_orb.updateOrb()

        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()

        if isinstance(self.parentItem(), LeaderLineItem):
            if event.key() == Qt.Key.Key_Up and self.suggestion_popup.isVisible():
                # Move up in the suggestion list
                current_index = self.suggestion_popup.currentRow()
                next_index = current_index - 1
                if next_index < self.suggestion_popup.count():
                    self.suggestion_popup.setCurrentRow(next_index)
                event.accept()
                return

            elif event.key() == Qt.Key.Key_Down and self.suggestion_popup.isVisible():
                # Move down in the suggestion list
                current_index = self.suggestion_popup.currentRow()
                next_index = current_index + 1
                if next_index < self.suggestion_popup.count():
                    self.suggestion_popup.setCurrentRow(next_index)
                event.accept()
                return

            # Get the current text
            current_text = self.getCurrentWord()

            # Suggest trick types based on current input
            self.suggestTrickTypes(current_text)
            self.setFocus()

            self.parentItem().updatePathEndPoint()

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)

        if hasattr(self, 'resize_orb'):
            self.resize_orb.updateOrb()

        if isinstance(self.parentItem(), LeaderLineItem):
            self.parentItem().updatePathEndPoint()

            if self.suggestion_popup.isVisible():
                if event.key() not in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                    self.suggestTrickTypes(self.getCurrentWord())

    def focusOutEvent(self, event):
        if self.suggestion_popup.isVisible():
            self.suggestion_popup.close()
            return

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
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.suggestion_popup.close()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                print("Tab key pressed")
                if self.suggestion_popup.isVisible():
                    self.completeText(self.suggestion_popup.currentItem())
                return True

        return super().eventFilter(obj, event)

    def itemChange(self, change, value):
        if isinstance(self.parentItem(), LeaderLineItem):
            self.parentItem().updatePathEndPoint()

        return super().itemChange(change, value)

    def setTextAlignment(self, alignment: Qt.AlignmentFlag):
        option = self.document().defaultTextOption()
        option.setAlignment(alignment)
        self.document().setDefaultTextOption(option)

        self.text_alignment = alignment

    def textAlignment(self):
        return self.text_alignment

    def suggestTrickTypes(self, current_word):
        # Filter the suggestions and exclude the current word
        suggestions = [trick for trick in self.trick_types
                       if trick.lower().startswith(current_word.lower()) and trick.lower() != current_word.lower()]

        if suggestions:
            self.updateSuggestionPopup(suggestions)
        else:
            self.suggestion_popup.hide()

    def updateSuggestionPopup(self, suggestions):
        # Clear the previous suggestions
        self.suggestion_popup.clear()

        # Add new suggestions
        for suggestion in suggestions:
            item = QListWidgetItem(suggestion)
            self.suggestion_popup.addItem(item)

        # Position the suggestion popup
        cursor_pos = self.sceneBoundingRect().bottomRight()
        global_pos = self.scene().views()[0].mapFromScene(cursor_pos.toPoint())
        self.suggestion_popup.move(int(global_pos.x()), int(100 + global_pos.y()))

        # Show the popup
        self.suggestion_popup.setCurrentRow(0)
        self.suggestion_popup.setParent(self.scene().parentWindow)
        self.suggestion_popup.show()

    def completeText(self, item):
        if item:
            cursor = self.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(item.text())
            self.setTextCursor(cursor)
            self.moveCursorToEnd()
            self.suggestion_popup.hide()

            if isinstance(self.parentItem(), LeaderLineItem):
                self.parentItem().updatePathEndPoint()

    def setLocked(self):
        self.locked = True

    def duplicate(self):
        item = self.copy()
        item.moveBy(10, 10)

        return item

    def copy(self):
        if isinstance(self.parentItem(), LeaderLineItem):
            return None

        item = CustomTextItem()
        item.setFont(self.font())
        item.setDefaultTextColor(self.defaultTextColor())
        item.setPos(self.pos())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setOpacity(self.opacity())

        item.setFlag(ITEM_SELECTABLE)
        item.setFlag(ITEM_MOVABLE)
        item.setToolTip('Text')
        item.setPlainText(self.toPlainText())
        item.setTextAlignment(self.textAlignment())
        item.setTextWidth(self.textWidth())

        return item

    def selectTextAndSetCursor(self):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.SelectionType.Document)
        self.setTextCursor(cursor)

    def moveCursorToEnd(self):
        cursor = self.textCursor()
        cursor.setPosition(len(self.toPlainText()))
        self.setTextCursor(cursor)

    def getCurrentWord(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def setEditing(self):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.editing = True


class LeaderLineItem(QGraphicsPathItem):
    def __init__(self, path, text: str):
        super().__init__(path)
        self.arrow_head = QPolygonF()

        self.text_element = CustomTextItem(text)
        self.text_element.setParentItem(self)
        self.text_element.setToolTip("Text")

    def shape(self):
        # Call the superclass's shape method to get the original path
        path = super().shape()

        # Create a stroker to modify the path
        stroker = QPainterPathStroker()
        stroker.setWidth(2)

        # Create a wider path
        wider_path = stroker.createStroke(path)

        # Optionally, unite the original path and the wider path
        combined_path = path.united(wider_path)

        return combined_path

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        # Set pen and brush
        painter.setPen(self.pen())
        painter.setBrush(self.brush())

        # Get the bottom-left and bottom-right points of the text element's bounding rect
        bottom_left = self.text_element.mapToParent(self.text_element.boundingRect().bottomLeft())
        bottom_right = self.text_element.mapToParent(self.text_element.boundingRect().bottomRight())

        # Draw the line according to the text element's rotated position
        painter.drawLine(bottom_left, bottom_right)

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

                self.arrow_head = arrow_head

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
            bottom_left = self.mapFromItem(self.text_element, text_rect.bottomLeft())
            bottom_right = self.mapFromItem(self.text_element, text_rect.bottomRight())

            corners = {
                'bottom_left': bottom_left,
                'bottom_right': bottom_right
            }

            closest_corner = min(corners, key=lambda corner: (corners[corner] - end_point).manhattanLength())
            new_start_point = corners[closest_corner]

            path.setElementPositionAt(0, new_start_point.x(), new_start_point.y())
            self.setPath(path)

    def update(self, rect=QRectF()):
        super().update(rect)
        self.updatePathEndPoint()

    def duplicate(self):
        item = self.copy()
        item.moveBy(10, 10)

        return item

    def copy(self):
        path = self.path()

        item = LeaderLineItem(path, self.text_element.toPlainText())
        item.setPen(self.pen())
        item.setBrush(self.brush())
        item.setPos(self.pos())
        item.setTransformOriginPoint(self.transformOriginPoint())
        item.setScale(self.scale())
        item.setRotation(self.rotation())
        item.setZValue(self.zValue())
        item.setTransform(self.transform())
        item.setOpacity(self.opacity())

        item.setFlag(ITEM_SELECTABLE)
        item.setFlag(ITEM_MOVABLE)
        item.setToolTip('Leader Line')

        item.text_element.setFont(self.text_element.font())
        item.text_element.setDefaultTextColor(self.text_element.defaultTextColor())
        item.text_element.setTransformOriginPoint(self.text_element.transformOriginPoint())
        item.text_element.setTransform(self.text_element.transform())
        item.text_element.setScale(self.text_element.scale())
        item.text_element.setRotation(self.text_element.rotation())
        item.text_element.setPos(self.text_element.pos())
        item.text_element.setZValue(self.text_element.zValue())
        item.text_element.setOpacity(self.text_element.opacity())
        item.text_element.setTextAlignment(self.text_element.textAlignment())
        item.text_element.setTextWidth(self.text_element.textWidth())

        item.updatePathEndPoint()

        return item


class CanvasItem(QGraphicsRectItem):
    def __init__(self, coords: QRectF, name):
        super().__init__(coords)

        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, PEN_STYLE.SolidLine)
        pen.setWidthF(0)
        pen.setJoinStyle(PEN_JOIN_STYLE.MiterJoin)
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
        if event.button() == LEFT_BUTTON:
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
        self.setToolTip(name)
        self.update()

    def name(self):
        return self.text.toPlainText()

    def canvasActive(self):
        return self.active

    def setCanvasActive(self, enabled: bool):
        self.scene().setBackgroundBrush(QBrush(QColor('#737373')))
        self.setFlag(ITEM_MOVABLE, enabled)
        self.setFlag(ITEM_SELECTABLE, enabled)
        self.text.setVisible(enabled)
        self.active = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.unsetCursor()
            self.scene().setBackgroundBrush(QBrush(QColor('#606060')))
            brush = QBrush(QColor('white'))
            pen = QPen(QColor('white'), 2, PEN_STYLE.SolidLine)
            pen.setWidthF(0)
            pen.setJoinStyle(PEN_JOIN_STYLE.MiterJoin)
            self.setBrush(brush)
            self.setPen(pen)

        for item in self.scene().items():
            if isinstance(item, CanvasItem):
                pass
            else:
                item.setFlag(ITEM_SELECTABLE, not enabled)
                item.setFlag(ITEM_MOVABLE, not enabled)

    def setTransparentMode(self):
        b = self.brush()
        p = self.pen()
        b.setColor(QColor(TRANSPARENT))
        p.setColor(QColor(TRANSPARENT))

        self.setBrush(b)
        self.setPen(p)

    def restore(self):
        brush = QBrush(QColor('white'))
        pen = QPen(QColor('white'), 2, PEN_STYLE.SolidLine)
        pen.setWidthF(0)
        pen.setJoinStyle(PEN_JOIN_STYLE.MiterJoin)
        self.setBrush(brush)
        self.setPen(pen)

    def duplicate(self):
        item = self.copy()
        item.moveBy(self.boundingRect().width() + 100, 0)

        return item

    def copy(self):
        duplicate = CanvasItem(self.rect(), f'COPY - {self.name()}')
        duplicate.setPos(self.pos())

        return duplicate


class CanvasTextItem(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__()

        self.setPos(parent.boundingRect().x(), parent.boundingRect().y())
        self.setParentItem(parent)
        self.setPlainText(text)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
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


class WaterMarkItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)

        self.gridEnabled = False

    def mousePressEvent(self, event):
        if event.button() == LEFT_BUTTON:
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
