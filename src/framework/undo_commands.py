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

class MultiItemPositionChangeCommand(QUndoCommand):
    def __init__(self, parent, items, old_positions, new_positions):
        super().__init__()
        self.items = items
        self.old_positions = old_positions
        self.new_positions = new_positions
        self.parent = parent

    def redo(self):
        for item, new_pos in zip(self.items, self.new_positions):
            item.setPos(new_pos)
        self.parent.update_transform_ui()

    def undo(self):
        for item, old_pos in zip(self.items, self.old_positions):
            item.setPos(old_pos)
        self.parent.update_transform_ui()

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

class SmoothPathCommand(QUndoCommand):
    def __init__(self, scene, items, new_paths, old_paths):
        super().__init__()
        self.scene = scene
        self.items = items
        self.new_paths = new_paths
        self.old_paths = old_paths

    def redo(self):
        for item, new_path in zip(self.items, self.new_paths):
            item.setPath(new_path)

    def undo(self):
        for item, old_path in zip(self.items, self.old_paths):
            item.setPath(old_path)

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
    def __init__(self, parent, items, old_rotations, new_rotation):
        super().__init__()
        self.parent = parent
        self.items = items
        self.old_rotations = old_rotations
        self.new_rotation = new_rotation

    def redo(self):
        for item in self.items:
            item.setRotation(self.new_rotation)
        self.parent.update_transform_ui()

    def undo(self):
        for item, old_rotation in zip(self.items, self.old_rotations):
            item.setRotation(old_rotation)
        self.parent.update_transform_ui()

class RotateDirectionCommand(QUndoCommand):
    def __init__(self, parent, items, old_rotations, new_rotations):
        super().__init__()
        self.parent = parent
        self.items = items
        self.old_rotations = old_rotations
        self.new_rotations = new_rotations

    def redo(self):
        for item, new_rotation in zip(self.items, self.new_rotations):
            item.setRotation(new_rotation)
        self.parent.update_transform_ui()

    def undo(self):
        for item, old_rotation in zip(self.items, self.old_rotations):
            item.setRotation(old_rotation)
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
    def __init__(self, items, old_opacities, new_opacity):
        super().__init__()
        self.items = items
        self.old_opacities = old_opacities
        self.new_opacity = new_opacity

    def redo(self):
        for item in self.items:
            item.setOpacity(self.new_opacity)

    def undo(self):
        for item, old_opacity in zip(self.items, self.old_opacities):
            item.setOpacity(old_opacity)

class HideCommand(QUndoCommand):
    def __init__(self, items, old_visibilities, new_visibility):
        super().__init__()
        self.items = items
        self.old_visibilities = old_visibilities
        self.new_visibility = new_visibility

    def redo(self):
        for item in self.items:
            item.setVisible(self.new_visibility)

    def undo(self):
        for item, old_visibility in zip(self.items, self.old_visibilities):
            item.setVisible(old_visibility)

class CloseSubpathCommand(QUndoCommand):
    def __init__(self, items, scene):
        super().__init__()
        self.items = items
        self.scene = scene
        self.old_paths = [item.path() for item in items]
        self.new_paths = [QPainterPath(path) for path in self.old_paths]

    def redo(self):
        for path in self.new_paths:
            if path.elementCount() > 0:
                path.closeSubpath()

        for item, new_path in zip(self.items, self.new_paths):
            item.setPath(new_path)

    def undo(self):
        for item, old_path in zip(self.items, self.old_paths):
            item.setPath(old_path)

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
    def __init__(self, items, old_fonts, new_font, old_colors, new_color):
        super().__init__()

        self.items = items
        self.old_fonts = old_fonts
        self.new_font = new_font
        self.old_colors = old_colors
        self.new_color = new_color

    def redo(self):
        for item in self.items:
            item.setFont(self.new_font)
            item.setDefaultTextColor(self.new_color)
            item.update()

    def undo(self):
        for item, old_font, old_color in zip(self.items, self.old_fonts, self.old_colors):
            item.setFont(old_font)
            item.setDefaultTextColor(old_color)
            item.update()

class PenChangeCommand(QUndoCommand):
    def __init__(self, items, old_pens, new_pen):
        super().__init__()

        self.items = items
        self.old_pens = old_pens
        self.new_pen = new_pen

    def redo(self):
        for item in self.items:
            item.setPen(self.new_pen)
            item.update()

    def undo(self):
        for item, old_pen in zip(self.items, self.old_pens):
            item.setPen(old_pen)
            item.update()

class BrushChangeCommand(QUndoCommand):
    def __init__(self, items, old_brushes, new_brush):
        super().__init__()

        self.items = items
        self.old_brushes = old_brushes
        self.new_brush = new_brush

    def redo(self):
        for item in self.items:
            item.setBrush(self.new_brush)
            item.update()

    def undo(self):
        for item, old_brush in zip(self.items, self.old_brushes):
            item.setBrush(old_brush)
            item.update()

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
