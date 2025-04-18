from src.scripts.imports import *
from src.framework.items import *


class SceneDeserializer:
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

        if metadata.get('system_type', 'unknown') != sys.platform:
            QMessageBox.information(self.scene.parentWindow, 'Open File', 'This MPRUN file was saved on a different'
                                                                          ' platform, replacing fonts and styles with '
                                                                          'ones that match your platform.')

        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)
            elif item_data['type'] == 'CustomTextItem':
                item = self.deserialize_custom_text_item(item_data)
            elif item_data['type'] == 'CustomPathItem':
                item = self.deserialize_custom_path_item(item_data)
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

        # Mapping string values back to QPen styles
        style_mapping = {
            'SolidLine': Qt.PenStyle.SolidLine,
            'DashLine': Qt.PenStyle.DashLine,
            'DotLine': Qt.PenStyle.DotLine,
            'DashDotLine': Qt.PenStyle.DashDotLine,
            'DashDotDotLine': Qt.PenStyle.DashDotDotLine,
        }

        capstyle_mapping = {
            'FlatCap': Qt.PenCapStyle.FlatCap,
            'SquareCap': Qt.PenCapStyle.SquareCap,
            'RoundCap': Qt.PenCapStyle.RoundCap
        }

        joinstyle_mapping = {
            'MiterJoin': Qt.PenJoinStyle.MiterJoin,
            'BevelJoin': Qt.PenJoinStyle.BevelJoin,
            'RoundJoin': Qt.PenJoinStyle.RoundJoin
        }

        pen.setStyle(style_mapping.get(data['style'], Qt.PenStyle.SolidLine))
        pen.setCapStyle(capstyle_mapping.get(data['capstyle'], Qt.PenCapStyle.FlatCap))
        pen.setJoinStyle(joinstyle_mapping.get(data['joinstyle'], Qt.PenJoinStyle.MiterJoin))

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

    def deserialize_alignment(self, data: str):
        if data == 'left':
            return Qt.AlignmentFlag.AlignLeft
        elif data == 'middle':
            return Qt.AlignmentFlag.AlignCenter
        elif data == 'right':
            return Qt.AlignmentFlag.AlignRight
        else:
            raise ValueError(f"Unknown alignment value: {data}")

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
        text_item.setTextWidth(data['width'])
        text_item.setTextAlignment(self.deserialize_alignment(data['alignment']))
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
        path_item.text_element.setDefaultTextColor(self.deserialize_color(data['textcolor']))
        path_item.text_element.setTextWidth(data['textwidth'])
        path_item.text_element.setTextAlignment(self.deserialize_alignment(data['textalignment']))
        path_item.text_element.setFont(self.deserialize_font(data['textfont']))

        self.process_attributes(path_item, data['attr'])
        self.process_attributes(path_item.text_element, data['textattr'])

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
            item.setOpacity(_data['opacity'])
            item.setVisible(_data['visible'])
