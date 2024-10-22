from src.scripts.imports import *
from src.framework.undo_commands import *


class BaseTool(object):
    def __init__(self, scene, view):
        self.scene = scene
        self.view = view

    def specialToolTip(self, event):
        pass

    def mousePress(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseRelease(self, event):
        pass


class LipTool(BaseTool):
    def __init__(self, scene, view):
        super().__init__(scene, view)

    def mousePress(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseRelease(self, event):
        pass
