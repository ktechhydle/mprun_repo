import json
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene
from src.framework.items import CanvasItem


class TemplateManager:
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene

    def load_template(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow,
                                                      'Open Template',
                                                      '',
                                                      'MPRUN template files (*.mpt)')

            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)

                    self.deserialize_items(data)

        except Exception as e:
            print(e)

    def save_template(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self.scene.parentWindow,
                                                      'Save Document As Template',
                                                      '',
                                                      'MPRUN template files (*.mpt)')

            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.serialize_items(), f, indent=4)

        except Exception as e:
            print(e)

    def serialize_items(self):
        data = []

        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                data.append(self.serialize_canvas(item))

        return data

    def serialize_canvas(self, canvas: CanvasItem):
        return {
            'type': 'CanvasItem',
            'rect': [0, 0, canvas.rect().width(), canvas.rect().height()],
            'name': canvas.name(),
            'x': canvas.pos().x(),
            'y': canvas.pos().y(),
        }

    def deserialize_items(self, items_data):
        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)

            if item is not None:
                self.scene.addItem(item)

        self.scene.parentWindow.use_exit_add_canvas()

    def deserialize_canvas(self, data):
        rect = QRectF(*data['rect'])
        canvas = CanvasItem(rect, data['name'])
        canvas.setPos(data['x'], data['y'])

        return canvas
