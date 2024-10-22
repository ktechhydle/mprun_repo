from src.scripts.imports import *


class LipItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF()):
        super().__init__(rect)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(QBrush(QColor(Qt.GlobalColor.transparent)))
        painter.drawLine(QLineF(self.rect().topLeft(), self.rect().topRight()))
        painter.drawLine(QLineF(self.rect().topLeft(), self.rect().bottomLeft()))
        painter.drawLine(QLineF(self.rect().bottomLeft(), self.rect().bottomRight()))
