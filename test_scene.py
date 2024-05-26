import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from PyQt5.QtCore import *


class DraggableSvgItem(QGraphicsSvgItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)


class SvgViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def load_svg(self, file_path):
        renderer = QSvgRenderer(file_path)
        if not renderer.isValid():
            print("Error: Unable to load Combobox Images file.")
            return

        # Here we parse the Combobox Images and create individual items for each element.
        item = DraggableSvgItem()
        item.setSharedRenderer(renderer)
        self.scene.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = SvgViewer()
    viewer.load_svg("Course Element/halfpipe 1 (22').svg")  # Replace with your Combobox Images file path
    viewer.show()
    sys.exit(app.exec_())
