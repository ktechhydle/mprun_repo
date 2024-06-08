import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from PyQt5.QtCore import *
import numpy as np

class LiquifyGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self._lastPos = None
        self._pixmapItem = None

    def setPixmapItem(self, pixmapItem):
        self._pixmapItem = pixmapItem

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._lastPos = event.pos()
            self._liquify(event.pos())

    def mouseMoveEvent(self, event):
        if self._lastPos is not None:
            self._liquify(event.pos())
            self._lastPos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._lastPos = None

    def _liquify(self, currentPos):
        if self._pixmapItem is not None:
            # Compute the offset
            offset = currentPos - self._lastPos

            # Get the current image from the pixmap
            pixmap = self._pixmapItem.pixmap()
            image = pixmap.toImage()

            # Convert QImage to numpy array
            width = image.width()
            height = image.height()
            ptr = image.bits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)

            # Apply a simple liquify effect (moving pixels)
            x, y = currentPos.x(), currentPos.y()
            if 0 <= x < width and 0 <= y < height:
                arr[max(0, y - 10):min(height, y + 10), max(0, x - 10):min(width, x + 10), :] = arr[max(0, y - 10 + offset.y()):min(height, y + 10 + offset.y()), max(0, x - 10 + offset.x()):min(width, x + 10 + offset.x()), :]

            # Convert numpy array back to QImage
            image = QImage(arr.data, width, height, QImage.Format_ARGB32)

            # Update the pixmap item
            self._pixmapItem.setPixmap(QPixmap.fromImage(image))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Liquify Tool')

        # Create scene and view
        self.scene = QGraphicsScene(self)
        self.view = LiquifyGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Load image
        pixmap = QPixmap('UI/Main Logos/mprun_splash_screen2.png')
        self.pixmapItem = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmapItem)

        # Set pixmap item in view
        self.view.setPixmapItem(self.pixmapItem)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
