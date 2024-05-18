import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from graphics_framework import *

    def drawTicker(self, painter):
        width, height = (self.rect().width(), self.rect().height()) if self.m_direction == Qt.Horizontal else (self.rect().height(), self.rect().width())
        if (self.m_upper - self.m_lower) == 0:
            return

        increment = width / (self.m_upper - self.m_lower)
        scale = next((scale for scale in ruler_metric_general.ruler_scale if scale * abs(increment) > 2 * self.fontMetrics().height()), ruler_metric_general.ruler_scale[-1])
        length = 0

        for subdiv in ruler_metric_general.subdivide[::-1]:
            subd_incr = scale / subdiv
            if subd_incr * abs(increment) <= MINIMUM_INCR:
                continue

            ideal_length = height / (subdiv + 1) - 1
            if ideal_length > length:
                length = ideal_length

            start = (self.m_lower // subd_incr) * subd_incr
            end = (self.m_upper // subd_incr + 1) * subd_incr

            for cur in range(int(start), int(end), int(subd_incr)):
                pos = round((cur - self.m_lower) * increment)
                if self.m_direction == Qt.Horizontal:
                    painter.drawLine(pos, height - length, pos, height)
                else:
                    painter.drawLine(height - length, pos, height, pos)

                label_spacing_px = abs(increment * scale / subdiv)
                if label_spacing_px > 6 * self.fontMetrics().height() or cur == 0:
                    unit_str = f"{cur}" if abs(cur) < 2000 else f"{cur // 1000}k"
                    if self.m_direction == Qt.Horizontal:
                        painter.drawText(pos + 2, 0, unit_str)
                    else:
                        painter.save()
                        painter.translate(4, pos + self.fontMetrics().width(unit_str) / 2 + 2)
                        painter.rotate(90)
                        painter.drawText(-self.fontMetrics().width(unit_str) / 2, 0, unit_str)
                        painter.restore()

    def drawPos(self, painter):
        width, height = (self.rect().width(), self.rect().height()) if self.m_direction == Qt.Horizontal else (self.rect().height(), self.rect().width())
        bs_width, bs_height = (height // 2 + 2, (height // 2 + 2) // 2 + 1)
        position = self.m_lower + (self.m_upper - self.m_lower) * (self.m_lastPos.x() if self.m_direction == Qt.Horizontal else self.m_lastPos.y()) / width

        if self.m_direction == Qt.Horizontal:
            x = round((position - self.m_lower) * width / (self.m_upper - self.m_lower)) + bs_width // 2 - 1
            painter.drawLine(self.m_lastPos.x(), 0, self.m_lastPos.x(), height)
        else:
            y = round((position - self.m_lower) * height / (self.m_upper - self.m_lower)) + bs_height // 2 - 1
            painter.drawLine(0, self.m_lastPos.y(), width, self.m_lastPos.y())

class QtCornerBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0xFF, 0xFF, 0xFF))

        painter.setPen(Qt.DashLine)
        center = self.rect().center()
        painter.drawLine(center.x(), self.rect().top(), center.x(), self.rect().bottom())
        painter.drawLine(self.rect().left(), center.y(), self.rect().right(), center.y())
        painter.drawLine(self.rect().topRight(), self.rect().bottomRight())
        painter.drawLine(self.rect().bottomLeft(), self.rect().bottomRight())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = QWidget()
    mainWin.setGeometry(100, 100, 800, 600)
    view = QGraphicsView(mainWin)
    view.setGeometry(50, 50, 700, 500)

    h_rulebar = QtRuleBar(Qt.Horizontal, view, mainWin)
    h_rulebar.setGeometry(50, 10, 700, 30)
    h_rulebar.setRange(0, 1000, 1000)

    v_rulebar = QtRuleBar(Qt.Vertical, view, mainWin)
    v_rulebar.setGeometry(10, 50, 30, 500)
    v_rulebar.setRange(0, 1000, 1000)

    corner_box = QtCornerBox(mainWin)
    corner_box.setGeometry(10, 10, 30, 30)

    mainWin.show()
    sys.exit(app.exec_())
