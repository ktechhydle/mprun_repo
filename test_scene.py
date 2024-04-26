from graphics_framework import *
from scipy.interpolate import *
import numpy as np

class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('MPRUN Beta Test Scene')
        self.setGeometry(100, 100, 600, 600)
        
        self.create_ui()
        self.create_test_object()
        
    def create_ui(self):
        self.canvas = QGraphicsScene()
        self.canvas_view = GraphicsView()
        
        self.canvas_view.setScene(self.canvas)
        
        self.setCentralWidget(self.canvas_view)

    def create_test_object(self):
        path = QPainterPath()
        path.moveTo(100, 100)

        p = QGraphicsPathItem(path.simplified())

        self.canvas.addItem(p)

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.path = QPainterPath()
        self.points = []

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        self.points.append(QPointF(50, 50))

        self.path.moveTo(self.points[0])

        self.path.quadTo(QPointF(100, 100), QPointF(200, 200))
        self.path.quadTo(QPointF(300, 300), QPointF(400, 400))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            self.points.append(self.mapToScene(event.pos()))

            if len(self.path) > 2:
                x = [p.x() for p in self.path]
                y = [p.y() for p in self.path]
                f = interp1d(x, y, kind='cubic')
                smooth_x = np.linspace(min(x), max(x), 1000)
                smooth_y = f(smooth_x)
                for i in range(len(smooth_x) - 1):
                    line = QGraphicsLineItem(QPoint(int(smooth_x[i]), int(smooth_y[i])), QPoint(int(smooth_x[i + 1]), int(smooth_y[i + 1])))

                    self.scene().addItem(line)

            self.scene().addItem(QGraphicsPathItem(self.path))

            super().mouseMoveEvent(event)
        
if __name__ == '__main__':
    win = QApplication([])
    app = MainWin()
    app.show()
    win.exec_()