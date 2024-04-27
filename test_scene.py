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
        self.path = QPainterPath()
        self.points.append(self.mapToScene(event.pos()))

        if len(self.points) > 1:
            self.path = QPainterPath()
            self.path.moveTo(self.points[0])
            for point in self.points[1:]:
                self.path.lineTo(point)

            self.scene().addItem(QGraphicsPathItem(self.path))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):


        super().mouseMoveEvent(event)
        
if __name__ == '__main__':
    win = QApplication([])
    app = MainWin()
    app.show()
    win.exec_()