from src.scripts.imports import *

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class PositionChangeCommand(QUndoCommand):
    def __init__(self, parent, item, old, new):
        super().__init__()
        self.item = item
        self.old = old
        self.new = new
        self.parent = parent

    def redo(self):
        self.item.setPos(self.new)
        self.parent.update_transform_ui()

    def undo(self):
        self.item.setPos(self.old)
        self.parent.update_transform_ui()

class AlignItemCommand(QUndoCommand):
    def __init__(self, parent, item, old, new):
        super().__init__()
        self.item = item
        self.old = old
        self.new = new
        self.parent = parent

    def redo(self):
        self.item.moveBy(self.new.x(), self.new.y())
        self.parent.update_transform_ui()

    def undo(self):
        self.item.setPos(self.old)
        self.parent.update_transform_ui()

class EditTextCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text):
        super().__init__()
        self.item = item
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        self.item.setPlainText(self.new_text)

    def undo(self):
        self.item.setPlainText(self.old_text)

class RemoveItemCommand(QUndoCommand):
    def __init__(self, canvas, items):
        super().__init__()
        self.canvas = canvas
        self.items = items

    def redo(self):
        for item in self.items:
            self.canvas.removeItem(item)

    def undo(self):
        for item in self.items:
            self.canvas.addItem(item)

class GraphicsEffectCommand(QUndoCommand):
    def __init__(self, item, amount, og_effect, effect):
        super().__init__()

        self.item = item
        self.amount = amount
        self.og_effect = og_effect
        self.choosenEffect = effect


    def redo(self):
        effect = None

        if self.choosenEffect == 'blur':
            effect = QGraphicsBlurEffect()
            effect.setBlurRadius(self.amount)

        elif self.choosenEffect == 'dropShadow':
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(self.amount)

        self.item.setGraphicsEffect(effect)


    def undo(self):
        self.item.setGraphicsEffect(self.og_effect)

class SmoothPathCommand(QUndoCommand):
    def __init__(self, scene, item, new_path, old_path):
        super().__init__()
        self.scene = scene
        self.item = item
        self.new_path = new_path
        self.old_path = old_path

    def redo(self):
        self.item.setPath(self.new_path)

    def undo(self):
        self.item.setPath(self.old_path)

class ScaleCommand(QUndoCommand):
    def __init__(self, item, old_scale, new_scale):
        super().__init__()
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def redo(self):
        self.item.setScale(self.new_scale)

    def undo(self):
        self.item.setScale(self.old_scale)

class TransformCommand(QUndoCommand):
    def __init__(self, item, old_t, new_t):
        super().__init__()
        self.item = item
        self.old_transform = old_t
        self.new_transform = new_t

    def redo(self):
        self.item.setTransform(self.new_transform)

    def undo(self):
        self.item.setTransform(self.old_transform)

class RotateCommand(QUndoCommand):
    def __init__(self, parent, item, old_rotation, new_rotation):
        super().__init__()
        self.item = item
        self.old_value = old_rotation
        self.new_value = new_rotation
        self.parent = parent

    def redo(self):
        self.item.setRotation(self.new_value)
        self.parent.update_transform_ui()

    def undo(self):
        self.item.setRotation(self.old_value)
        self.parent.update_transform_ui()

class ItemMovedUndoCommand(QUndoCommand):
    def __init__(self, oldPositions, newPositions):
        super().__init__()
        self.oldPositions = oldPositions
        self.newPositions = newPositions

    def redo(self):
        for item, pos in self.newPositions.items():
            item.setPos(pos)

    def undo(self):
        for item, pos in self.oldPositions.items():
            item.setPos(pos)

class OpacityCommand(QUndoCommand):
    def __init__(self, item, old_opacity, new_opacity):
        super().__init__()
        self.item = item
        self.old_value = old_opacity
        self.new_value = new_opacity

    def redo(self):
        self.item.setOpacity(self.new_value)

    def undo(self):
        self.item.setOpacity(self.old_value)

class HideCommand(QUndoCommand):
    def __init__(self, item, old_visible, new_visible):
        super().__init__()
        self.item = item
        self.old_value = old_visible
        self.new_value = new_visible

    def redo(self):
        self.item.setVisible(self.new_value)

    def undo(self):
        self.item.setVisible(self.old_value)

class NameCommand(QUndoCommand):
    def __init__(self, item, old_name, new_name):
        super().__init__()
        self.item = item
        self.old_value = old_name
        self.new_value = new_name

    def redo(self):
        self.item.setToolTip(self.new_value)

    def undo(self):
        self.item.setToolTip(self.old_value)

class CloseSubpathCommand(QUndoCommand):
    def __init__(self, item, scene):
        super().__init__()
        self.item = item
        self.scene = scene
        self.oldPath = self.item.path()
        self.newPath = QPainterPath(self.oldPath)

    def redo(self):
        if self.newPath.elementCount() > 0:
            self.newPath.closeSubpath()
            self.item.setPath(self.newPath)

    def undo(self):
        self.item.setPath(self.oldPath)

class EditPathCommand(QUndoCommand):
    def __init__(self, item, old, new):
        super().__init__()
        self.item = item
        self.oldPath = old
        self.newPath = new

    def redo(self):
        self.item.setPath(self.newPath)

    def undo(self):
        self.item.setPath(self.oldPath)

class FontChangeCommand(QUndoCommand):
    def __init__(self, item, oldf, newf, oldcolor, newcolor):
        super().__init__()

        self.item = item
        self.old = oldf
        self.new = newf
        self.oldc = oldcolor
        self.newc = newcolor

    def redo(self):
        self.item.setFont(self.new)
        self.item.setDefaultTextColor(self.newc)
        self.item.update()

    def undo(self):
        self.item.setFont(self.old)
        self.item.setDefaultTextColor(self.oldc)
        self.item.update()

class PenChangeCommand(QUndoCommand):
    def __init__(self, item, old, new):
        super().__init__()

        self.item = item
        self.old = old
        self.new = new

    def redo(self):
        self.item.setPen(self.new)
        self.item.update()

    def undo(self):
        self.item.setPen(self.old)
        self.item.update()

class BrushChangeCommand(QUndoCommand):
    def __init__(self, item, old, new):
        super().__init__()

        self.item = item
        self.old = old
        self.new = new

    def redo(self):
        self.item.setBrush(self.new)
        self.item.update()

    def undo(self):
        self.item.setBrush(self.old)
        self.item.update()

class ResetItemCommand(QUndoCommand):
    def __init__(self, item):
        super().__init__()

        self.item = item
        self.effect_type, self.effect_params = self._get_effect_params(self.item.graphicsEffect())
        self.rotation = self.item.rotation()
        self.scale = self.item.scale()
        self.x_scale = self.item.transform().m11()
        self.y_scale = self.item.transform().m22()
        self.opacity = self.item.opacity()

    def _get_effect_params(self, effect):
        if isinstance(effect, QGraphicsDropShadowEffect):
            return 'drop_shadow', {
                'offset': effect.offset(),
                'blur_radius': effect.blurRadius(),
                'color': effect.color()
            }
        elif isinstance(effect, QGraphicsBlurEffect):
            return 'blur', {
                'blur_radius': effect.blurRadius()
            }
        return None, None

    def _set_effect(self, effect_type, params):
        if effect_type == 'drop_shadow':
            effect = QGraphicsDropShadowEffect()
            effect.setOffset(params['offset'])
            effect.setBlurRadius(params['blur_radius'])
            effect.setColor(params['color'])
            return effect
        elif effect_type == 'blur':
            effect = QGraphicsBlurEffect()
            effect.setBlurRadius(params['blur_radius'])
            return effect
        return None

    def redo(self):
        self.item.setGraphicsEffect(None)
        self.item.resetTransform()
        self.item.setScale(1)
        self.item.setRotation(0)
        self.item.setOpacity(100)

    def undo(self):
        self.item.resetTransform()
        transform = QTransform()
        transform.scale(self.x_scale, self.y_scale)
        self.item.setTransform(transform)
        self.item.setScale(self.scale)
        self.item.setRotation(self.rotation)
        self.item.setGraphicsEffect(self._set_effect(self.effect_type, self.effect_params))
        self.item.setOpacity(self.opacity)

class CanvasSizeEditCommand(QUndoCommand):
    def __init__(self, item, og_w, og_h, new_w, new_h):
        super().__init__()

        self.item = item
        self.og_w = og_w
        self.og_h = og_h
        self.new_w = new_w
        self.new_h = new_h

    def redo(self):
        self.item.setRect(0, 0, self.new_w, self.new_h)

    def undo(self):
        self.item.setRect(0, 0, self.og_w, self.og_h)

class CanvasNameEditCommand(QUndoCommand):
    def __init__(self, item, og, new):
        super().__init__()

        self.item = item
        self.og = og
        self.new = new

    def redo(self):
        self.item.setName(self.new)
        self.item.setToolTip(self.new)

    def undo(self):
        self.item.setName(self.og)
        self.item.setToolTip(self.og)

class LayerChangeCommand(QUndoCommand):
    def __init__(self, item, old, new):
        super().__init__()

        self.item = item
        self.old = old
        self.new = new

    def redo(self):
        self.item.setZValue(self.new)

    def undo(self):
        self.item.setZValue(self.old)
