from src.scripts.imports import *


class LipItem(QGraphicsPathItem):
    def __init__(self, rect: QRectF):
        super().__init__()
        self.setToolTip('Path')
        self.rect = rect

        self.draw()

    def draw(self):
        path = QPainterPath()
        path.moveTo(self.rect.topRight())
        path.lineTo(self.rect.topLeft())
        path.lineTo(self.rect.bottomLeft())
        path.lineTo(self.rect.bottomRight())

        self.setPath(path)
        self.setPen(self.pen())

    def setRect(self, rect: QRectF):
        self.rect = rect
        self.update()

    def rectBox(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        self.draw()

    def copy(self):
        item = LipItem(self.rectBox())
        item.setPos(self.pos())
        item.setFlags(self.flags())
        item.setToolTip(self.toolTip())
        item.setOpacity(self.opacity())
        item.setPath(self.path())
        item.setPen(self.pen())
        item.setBrush(self.brush())

        return item


class RectItem(QGraphicsPathItem):
    def __init__(self, rect: QRectF):
        super().__init__()
        self.setToolTip('Path')
        self.rect = rect

        self.draw()

    def draw(self):
        path = QPainterPath()
        path.moveTo(self.rect.topLeft())
        path.lineTo(self.rect.topRight())
        path.lineTo(self.rect.bottomRight())
        path.lineTo(self.rect.bottomLeft())
        path.lineTo(self.rect.topLeft())

        self.setPath(path)
        self.setPen(self.pen())

    def setRect(self, rect: QRectF):
        self.rect = rect
        self.update()

    def rectBox(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        self.draw()

    def copy(self):
        item = RectItem(self.rectBox())
        item.setPos(self.pos())
        item.setFlags(self.flags())
        item.setToolTip(self.toolTip())
        item.setOpacity(self.opacity())
        item.setPath(self.path())
        item.setPen(self.pen())
        item.setBrush(self.brush())

        return item


class LineItem(QGraphicsPathItem):
    def __init__(self, line: QLineF):
        super().__init__()
        self.setToolTip('Path')
        self.line = line

        self.draw()

    def draw(self):
        path = QPainterPath()
        path.moveTo(self.line.p1())
        path.lineTo(self.line.p2())

        self.setPath(path)
        self.setPen(self.pen())

    def setLine(self, line: QLineF):
        self.line = line
        self.update()

    def lineBox(self):
        return self.line

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        self.draw()

    def copy(self):
        item = LineItem(self.lineBox())
        item.setPos(self.pos())
        item.setFlags(self.flags())
        item.setToolTip(self.toolTip())
        item.setOpacity(self.opacity())
        item.setPath(self.path())
        item.setPen(self.pen())
        item.setBrush(self.brush())

        return item


class ArcItem(QGraphicsPathItem):
    def __init__(self, line: QLineF, arc_point: QPointF):
        super().__init__()
        self.setToolTip('Path')
        self.line = line
        self.arc_point = arc_point

        self.draw()

    def draw(self):
        path = QPainterPath()
        path.moveTo(self.line.p1())
        path.quadTo(self.arc_point, self.line.p2())

        self.setPath(path)
        self.setPen(self.pen())

    def setLine(self, line: QLineF):
        self.line = line
        self.update()

    def lineBox(self):
        return self.line

    def setArcPoint(self, arc_point: QPointF):
        self.arc_point = arc_point
        self.update()

    def arcPoint(self):
        return self.arc_point

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        self.draw()

    def copy(self):
        item = ArcItem(self.lineBox(), self.arcPoint())
        item.setPos(self.pos())
        item.setFlags(self.flags())
        item.setToolTip(self.toolTip())
        item.setOpacity(self.opacity())
        item.setPath(self.path())
        item.setPen(self.pen())
        item.setBrush(self.brush())

        return item
