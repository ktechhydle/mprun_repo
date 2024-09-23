from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsItem, QGraphicsScene
from src.framework.items import CustomSvgItem, CustomTextItem, CustomPixmapItem
from src.framework.undo_commands import AddItemCommand


class ImportManager:
    def __init__(self, scene: QGraphicsScene):
        self.canvas = scene

    def importFile(self):
        # Deactivate the add canvas tool
        self.canvas.parentWindow.use_exit_add_canvas()

        file_path, _ = QFileDialog().getOpenFileName(self.canvas.parentWindow,
                                                     "Insert Element",
                                                     "",
                                                     'Supported types (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.tiff *.tif *.xbm *.xpm *.svg *.txt *.csv)')

        if file_path:
            if file_path.endswith('.svg'):
                svg_item = CustomSvgItem(file_path)
                svg_item.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, svg_item)
                self.canvas.addCommand(add_command)
                svg_item.setToolTip('Imported SVG')

                self.create_item_attributes(svg_item)

            elif file_path.endswith(('.txt', '.csv')):
                with open(file_path, 'r') as f:
                    item = CustomTextItem(f.read())

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)

                    self.create_item_attributes(item)

            else:
                image1 = QPixmap(file_path)
                image2 = CustomPixmapItem(image1)
                image2.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, image2)
                self.canvas.addCommand(add_command)
                image2.setToolTip('Imported Pixmap')

                self.create_item_attributes(image2)

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)
