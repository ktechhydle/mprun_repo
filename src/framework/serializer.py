from src.framework.items import *
from src.scripts.app_internal import copyright_message


class SceneSerializer:
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

    def serialize_file(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()