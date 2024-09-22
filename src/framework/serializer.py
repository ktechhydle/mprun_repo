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
            'item_count': len(self.scene.items()),
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
                        'text': item.toPlainText(),
                        'font': self.serialize_font(item.font()),
                        'color': self.serialize_color(item.defaultTextColor()),
                        'attr': self.serialize_item_attributes(item),
                        'locked': item.locked,
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
            QMessageBox.warning(self.scene.parentWindow, 'Open File', 'You are attempting to open a file saved in an '
                                                                      'different version of MPRUN, this may cause '
                                                                      'errors.')

        if metadata.get('item_count', 'unknown') >= 500:
            QMessageBox.warning(self.scene.parentWindow, 'Open File', 'You are attempting to open a file with a large '
                                                                      'amount of items, this can cause your computer '
                                                                      'to slow down.')

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

        self.process_attributes(text_item, data['attr'])

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

        self.process_attributes(path_item, data['attr'])

        if data.get('smooth', True):
            path_item.smooth = True

        else:
            path_item.smooth = False

        return path_item

    def deserialize_custom_group_item(self, data):
        group_item = CustomGraphicsItemGroup()

        self.process_attributes(group_item, data['attr'])

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

        self.process_attributes(path_item, data['attr'])

        path_item.updatePathEndPoint()

        return path_item

    def deserialize_custom_svg_item(self, data):
        try:
            svg_item = CustomSvgItem()
            svg_item.store_filename(data['filename'])
            svg_item.loadFromData(data['raw_svg_data'])

            self.process_attributes(svg_item, data['attr'])

            return svg_item

        except Exception as e:
            print(e)

    def deserialize_custom_pixmap_item(self, data):
        pixmap = QPixmap(data['filename'])
        pixmap_item = CustomPixmapItem(pixmap)
        pixmap_item.store_filename(data['filename'])
        pixmap_item.loadFromData(data['data'])

        self.process_attributes(pixmap_item, data['attr'])

        pixmap = pixmap_item.pixmap()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        pixmap_data = buffer.data().data()
        pixmap_item.loadFromData(pixmap_data)

        return pixmap_item

    def process_attributes(self, item, data):
        for _data in data:
            item.setTransformOriginPoint(self.deserialize_point(_data['transformorigin']))
            item.setRotation(_data['rotation'])
            item.setTransform(self.deserialize_transform(_data['transform']))
            item.setScale(_data['scale'])
            item.setPos(_data['x'], _data['y'])
            item.setToolTip(_data['name'])
            item.setZValue(_data['zval'])
            item.setVisible(_data['visible'])


class MPDataRepairer:
    def __init__(self, parent: QMainWindow, filename=None):
        self.parent = parent
        self.filename = None

        if filename is None:
            file, _ = QFileDialog.getOpenFileName(parent, 'Choose File', '', 'MPRUN files (*.mp)')

            if file:
                self.filename = file
        else:
            self.filename = filename

        self.repair()

    def repair(self):
        if self.filename is not None:
            try:
                with open(self.filename, 'rb') as f:
                    data = self.repair_file(pickle.load(f))

                with open(self.filename, 'wb') as nf:
                    pickle.dump(data, nf)

            except Exception as e:
                print(f"Error loading file: {e}")

            QMessageBox.information(self.parent, 'Process Complete', 'File repair completed successfully.')

    def repair_file(self, serialized_data):
        is_valid, message = self.validate_serialized_data(serialized_data)
        if not is_valid:
            print(f'File is corrupted: {message}')
            self.repair_data(serialized_data)  # attempt to repair
        else:
            print('File is valid.')
        return serialized_data

    def repair_data(self, data):
        """If we update file serialization, we will add repair methods here to fix any errors"""
        pass

    def validate_serialized_data(self, data):
        required_fields = ['mpversion', 'item_count']
        for field in required_fields:
            if field not in data:
                return False, f'Missing field: {field}'

        if data['item_count'] != len(data) - 1:  # account for metadata
            return False, 'Item count mismatch'

        return True, 'Data is valid'


