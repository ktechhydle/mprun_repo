import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from graphics_framework import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a QGraphicsView
        view = QGraphicsView(self)
        layout.addWidget(view)
        view.setScene(QGraphicsScene(self))

        ruler = QtRuleBar(Qt.Horizontal, view, self)

        # Create QtCornerBox
        corner_box = QtCornerBox()
        layout.addWidget(corner_box)
        layout.addWidget(ruler)

        self.setWindowTitle('Ruler Example')
        self.show()

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_hruler = QtRuleBar(Qt.Horizontal, self, self)
        self.m_vruler = QtRuleBar(Qt.Vertical, self, self)
        self.box = QtCornerBox(self)
        self.setViewport(QWidget())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
