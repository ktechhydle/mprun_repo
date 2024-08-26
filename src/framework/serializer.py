from src.scripts.imports import *
from src.framework.custom_classes import *
from src.scripts.app_internal import copyright_message


class MPSerializer:
    def __init__(self, scene):
        self.scene = scene

    def serialize_items(self):
        items_data = []

        items_data.append({
            'mpversion': self.scene.mpversion,
            'copyright': copyright_message,
        })

        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                items_data.append(self.serialize_canvas(item))

            elif isinstance(item, CustomTextItem):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomTextItem',
                        'markdown': True if item.markdownEnabled else False,
                        'text': item.old_text if item.markdownEnabled else item.toPlainText(),
                        'font': self.serialize_font(item.font()),
                        'color': self.serialize_color(item.defaultTextColor()),
                        'attr': self.serialize_item_attributes(item),
                        'locked': True if item.markdownEnabled else False,
                    })

            elif isinstance(item, CustomPathItem):
                if item.parentItem():
                    pass

                else:
                    path_data = {
                        'type': 'CustomPathItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'attr': self.serialize_item_attributes(item),
                        'elements': self.serialize_path(item.path()),
                        'smooth': True if item.smooth else False,
                        'addtext': True if item.add_text else False,
                        'textalongpath': item.text_along_path if item.add_text else '',
                        'textfont': self.serialize_font(
                            item.text_along_path_font) if item.add_text else self.serialize_font(QFont('Arial', 20)),
                        'textcolor': self.serialize_color(
                            item.text_along_path_color) if item.add_text else self.serialize_color(QColor('black')),
                        'textspacing': item.text_along_path_spacing if item.add_text else 3,
                        'starttextfrombeginning': item.start_text_from_beginning if item.add_text else False,
                    }

                    items_data.append(path_data)

            elif isinstance(item, CustomGraphicsItemGroup):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomGraphicsItemGroup',
                        'attr': self.serialize_item_attributes(item),
                        'children': self.serialize_group(item)
                    })

            elif isinstance(item, LeaderLineItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'LeaderLineItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'attr': self.serialize_item_attributes(item),
                        'elements': self.serialize_path(item.path()),
                        'text': item.text_element.toPlainText(),
                        'textcolor': self.serialize_color(item.text_element.defaultTextColor()),
                        'textfont': self.serialize_font(item.text_element.font()),
                        'textposx': item.text_element.pos().x(),
                        'textposy': item.text_element.pos().y(),
                        'textzval': item.text_element.zValue(),
                        'texttransform': self.serialize_transform(item.text_element.transform()),
                        'textscale': item.text_element.scale(),
                        'texttransformorigin': self.serialize_point(item.transformOriginPoint()),
                        'textrotation': item.text_element.rotation(),
                        'textvisible': item.text_element.isVisible(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomSvgItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'CustomSvgItem',
                        'attr': self.serialize_item_attributes(item),
                        'filename': item.source() if
                        os.path.exists(item.source() if item.source() is not None else '') else None,
                        'raw_svg_data': self.serialize_file(item.source()) if
                        os.path.exists(item.source() if item.source() is not None else '') else item.svgData(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomPixmapItem):
                if item.parentItem():
                    pass

                else:
                    pixmap = item.pixmap()
                    buffer = QBuffer()
                    buffer.open(QIODevice.WriteOnly)
                    pixmap.save(buffer, "PNG")
                    pixmap_data = buffer.data().data()

                    data = {
                        'type': 'CustomPixmapItem',
                        'attr': self.serialize_item_attributes(item),
                        'filename': item.return_filename() if
                        os.path.exists(item.return_filename() if item.return_filename() is not None else '') else None,
                        'data': pixmap_data,
                    }

                    items_data.append(data)

        return items_data

    def serialize_item_attributes(self, item):
        return [{
            'rotation': item.rotation(),
            'transform': self.serialize_transform(item.transform()),
            'scale': item.scale(),
            'transformorigin': self.serialize_point(item.transformOriginPoint()),
            'x': item.pos().x(),
            'y': item.pos().y(),
            'name': item.toolTip(),
            'zval': item.zValue(),
            'visible': item.isVisible(),
        }]

    def serialize_color(self, color: QColor):
        return {
            'red': color.red(),
            'green': color.green(),
            'blue': color.blue(),
            'alpha': color.alpha(),
        }

    def serialize_pen(self, pen: QPen):
        return {
            'width': pen.width(),
            'color': self.serialize_color(pen.color()),
            'style': pen.style(),
            'capstyle': pen.capStyle(),
            'joinstyle': pen.joinStyle()
        }

    def serialize_brush(self, brush: QBrush):
        return {
            'color': self.serialize_color(brush.color()),
            'style': brush.style()
        }

    def serialize_font(self, font: QFont):
        return {
            'family': font.family(),
            'pointsize': font.pixelSize(),
            'letterspacing': font.letterSpacing(),
            'bold': font.bold(),
            'italic': font.italic(),
            'underline': font.underline(),
        }

    def serialize_transform(self, transform: QTransform):
        return {
            'm11': transform.m11(),
            'm12': transform.m12(),
            'm13': transform.m13(),
            'm21': transform.m21(),
            'm22': transform.m22(),
            'm23': transform.m23(),
            'm31': transform.m31(),
            'm32': transform.m32(),
            'm33': transform.m33()
        }

    def serialize_point(self, point: QPointF):
        return {'x': point.x(), 'y': point.y()}

    def serialize_canvas(self, canvas: CanvasItem):
        return {
            'type': 'CanvasItem',
            'rect': [0, 0, canvas.rect().width(), canvas.rect().height()],
            'name': canvas.name(),
            'x': canvas.pos().x(),
            'y': canvas.pos().y(),
        }

    def serialize_path(self, path: QPainterPath):
        elements = []
        for i in range(path.elementCount()):
            element = path.elementAt(i)
            if element.isMoveTo():
                elements.append({'type': 'moveTo', 'x': element.x, 'y': element.y})
            elif element.isLineTo():
                elements.append({'type': 'lineTo', 'x': element.x, 'y': element.y})
            elif element.isCurveTo():
                elements.append({'type': 'curveTo', 'x': element.x, 'y': element.y})
        return elements

    def serialize_group(self, group: CustomGraphicsItemGroup):
        children = []
        for child in group.childItems():
            if isinstance(child, CustomTextItem):
                children.append({
                    'type': 'CustomTextItem',
                    'markdown': True if child.markdownEnabled else False,
                    'text': child.toPlainText(),
                    'font': self.serialize_font(child.font()),
                    'color': self.serialize_color(child.defaultTextColor()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'locked': True if child.markdownEnabled else False,
                    'visible': child.isVisible(),
                })
            elif isinstance(child, CustomPathItem):
                path_data = {
                    'type': 'CustomPathItem',
                    'pen': self.serialize_pen(child.pen()),
                    'brush': self.serialize_brush(child.brush()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'elements': self.serialize_path(child.path()),
                    'visible': child.isVisible(),
                }

                if child.add_text:
                    path_data.update({
                        'addtext': child.add_text,
                        'text': child.text_along_path,
                        'textfont': self.serialize_font(child.text_along_path_font),
                        'textcolor': self.serialize_color(child.text_along_path_color),
                        'textspacing': child.text_along_path_spacing,
                        'starttextfrombeginning': child.start_text_from_beginning,
                    })

                children.append(path_data)
            elif isinstance(child, CustomSvgItem):
                data = {
                    'type': 'CustomSvgItem',
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'filename': child.source(),
                    'visible': child.isVisible(),
                }

                children.append(data)
            elif isinstance(child, CustomPixmapItem):
                data = {
                    'type': 'CustomPixmapItem',
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'filename': child.return_filename(),
                    'visible': child.isVisible(),
                }

                children.append(data)

        return children

    def serialize_file(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()


class MPDeserializer:
    def __init__(self, scene):
        self.scene = scene

    def deserialize_items(self, items_data):
        # Handle metadata
        metadata = items_data.pop(0)
        if metadata.get('mpversion', 'unknown') != self.scene.mpversion:
            QMessageBox.warning(self.scene.parentWindow, 'Open', 'You are attempting to open a file saved in an '
                                                                 'different version of MPRUN, are you sure you want '
                                                                 'to do this?')

        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)
            elif item_data['type'] == 'CustomTextItem':
                item = self.deserialize_custom_text_item(item_data)
            elif item_data['type'] == 'CustomPathItem':
                item = self.deserialize_custom_path_item(item_data)
            elif item_data['type'] == 'CustomGraphicsItemGroup':
                item = self.deserialize_custom_group_item(item_data)
            elif item_data['type'] == 'LeaderLineItem':
                item = self.deserialize_leader_line_item(item_data)
            elif item_data['type'] == 'CustomSvgItem':
                item = self.deserialize_custom_svg_item(item_data)
            elif item_data['type'] == 'CustomPixmapItem':
                item = self.deserialize_custom_pixmap_item(item_data)

            if item is not None:
                self.scene.addItem(item)

        self.scene.parentWindow.use_exit_add_canvas()

    def deserialize_color(self, color):
        return QColor(color['red'], color['green'], color['blue'], color['alpha'])

    def deserialize_pen(self, data):
        pen = QPen()
        pen.setWidth(data['width'])
        pen.setColor(self.deserialize_color(data['color']))
        pen.setStyle(data['style'])
        pen.setCapStyle(data['capstyle'])
        pen.setJoinStyle(data['joinstyle'])
        return pen

    def deserialize_brush(self, data):
        brush = QBrush()
        brush.setColor(self.deserialize_color(data['color']))
        brush.setStyle(data['style'])
        return brush

    def deserialize_font(self, data):
        font = QFont()
        font.setFamily(data['family'])
        font.setPixelSize(data['pointsize'])
        font.setLetterSpacing(QFont.AbsoluteSpacing, data['letterspacing'])
        font.setBold(data['bold'])
        font.setItalic(data['italic'])
        font.setUnderline(data['underline'])
        return font

    def deserialize_transform(self, data):
        transform = QTransform(
            data['m11'], data['m12'], data['m13'],
            data['m21'], data['m22'], data['m23'],
            data['m31'], data['m32'], data['m33']
        )
        return transform

    def deserialize_point(self, data):
        return QPointF(data['x'], data['y'])

    def deserialize_canvas(self, data):
        rect = QRectF(*data['rect'])
        canvas = CanvasItem(rect, data['name'])
        canvas.setPos(data['x'], data['y'])
        return canvas

    def deserialize_custom_text_item(self, data):
        text_item = CustomTextItem(data['text'])
        text_item.setFont(self.deserialize_font(data['font']))
        text_item.setDefaultTextColor(self.deserialize_color(data['color']))
        text_item.locked = data['locked']

        for attr in data['attr']:
            text_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            text_item.setRotation(attr['rotation'])
            text_item.setTransform(self.deserialize_transform(attr['transform']))
            text_item.setScale(attr['scale'])
            text_item.setPos(attr['x'], attr['y'])
            text_item.setToolTip(attr['name'])
            text_item.setZValue(attr['zval'])
            text_item.setVisible(attr['visible'])

        if data.get('markdown', True):
            text_item.toMarkdown()

        return text_item

    def deserialize_custom_path_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = CustomPathItem(sub_path)
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))

        for attr in data['attr']:
            path_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            path_item.setRotation(attr['rotation'])
            path_item.setTransform(self.deserialize_transform(attr['transform']))
            path_item.setScale(attr['scale'])
            path_item.setPos(attr['x'], attr['y'])
            path_item.setToolTip(attr['name'])
            path_item.setZValue(attr['zval'])
            path_item.setVisible(attr['visible'])

        if data.get('smooth', True):
            path_item.smooth = True

        else:
            path_item.smooth = False

        if data.get('addtext', True):
            path_item.add_text = True
            path_item.setTextAlongPath(data['textalongpath'])
            path_item.setTextAlongPathColor(self.deserialize_color(data['textcolor']))
            path_item.setTextAlongPathFont(self.deserialize_font(data['textfont']))
            path_item.setTextAlongPathSpacingFromPath(data['textspacing'])
            path_item.setTextAlongPathFromBeginning(data['starttextfrombeginning'])

        else:
            path_item.add_text = False

        return path_item

    def deserialize_custom_group_item(self, data):
        group_item = CustomGraphicsItemGroup()

        for attr in data['attr']:
            group_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            group_item.setRotation(attr['rotation'])
            group_item.setTransform(self.deserialize_transform(attr['transform']))
            group_item.setScale(attr['scale'])
            group_item.setPos(attr['x'], attr['y'])
            group_item.setToolTip(attr['name'])
            group_item.setZValue(attr['zval'])
            group_item.setVisible(attr['visible'])

        for child_data in data['children']:
            if child_data['type'] == 'CustomTextItem':
                child = self.deserialize_custom_text_item(child_data)
            elif child_data['type'] == 'CustomPathItem':
                child = self.deserialize_custom_path_item(child_data)
            elif child_data['type'] == 'CustomPixmapItem':
                child = self.deserialize_custom_pixmap_item(child_data)
            elif child_data['type'] == 'CustomSvgItem':
                child = self.deserialize_custom_svg_item(child_data)

            group_item.addToGroup(child)

        return group_item

    def deserialize_leader_line_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = LeaderLineItem(sub_path, data['text'])
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))
        path_item.text_element.setZValue(data['textzval'])
        path_item.text_element.setDefaultTextColor(self.deserialize_color(data['textcolor']))
        path_item.text_element.setFont(self.deserialize_font(data['textfont']))
        path_item.text_element.setTransformOriginPoint(self.deserialize_point(data['texttransformorigin']))
        path_item.text_element.setTransform(self.deserialize_transform(data['texttransform']))
        path_item.text_element.setScale(data['textscale'])
        path_item.text_element.setPos(data['textposx'], data['textposy'])
        path_item.text_element.setRotation(data['textrotation'])
        path_item.text_element.setVisible(data['textvisible'])

        for attr in data['attr']:
            path_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            path_item.setRotation(attr['rotation'])
            path_item.setTransform(self.deserialize_transform(attr['transform']))
            path_item.setScale(attr['scale'])
            path_item.setPos(attr['x'], attr['y'])
            path_item.setToolTip(attr['name'])
            path_item.setZValue(attr['zval'])
            path_item.setVisible(attr['visible'])

        path_item.updatePathEndPoint()

        return path_item

    def deserialize_custom_svg_item(self, data):
        try:
            svg_item = CustomSvgItem()
            svg_item.store_filename(data['filename'])
            svg_item.loadFromData(data['raw_svg_data'])

            for attr in data['attr']:
                svg_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
                svg_item.setRotation(attr['rotation'])
                svg_item.setTransform(self.deserialize_transform(attr['transform']))
                svg_item.setScale(attr['scale'])
                svg_item.setPos(attr['x'], attr['y'])
                svg_item.setToolTip(attr['name'])
                svg_item.setZValue(attr['zval'])
                svg_item.setVisible(attr['visible'])

            return svg_item

        except Exception as e:
            print(e)

    def deserialize_custom_pixmap_item(self, data):
        pixmap = QPixmap(data['filename'])
        pixmap_item = CustomPixmapItem(pixmap)
        pixmap_item.store_filename(data['filename'])
        pixmap_item.loadFromData(data['data'])

        for attr in data['attr']:
            pixmap_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            pixmap_item.setRotation(attr['rotation'])
            pixmap_item.setTransform(self.deserialize_transform(attr['transform']))
            pixmap_item.setScale(attr['scale'])
            pixmap_item.setPos(attr['x'], attr['y'])
            pixmap_item.setToolTip(attr['name'])
            pixmap_item.setZValue(attr['zval'])
            pixmap_item.setVisible(attr['visible'])

        pixmap = pixmap_item.pixmap()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        pixmap_data = buffer.data().data()
        pixmap_item.loadFromData(pixmap_data)

        return pixmap_item
