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
