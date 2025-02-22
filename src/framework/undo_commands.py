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


class MultiAddItemCommand(QUndoCommand):
    def __init__(self, scene, items):
        super().__init__()
        self.scene = scene
        self.items = items

    def redo(self):
        for item in self.items:
            self.scene.addItem(item)

    def undo(self):
        for item in self.items:
            self.scene.removeItem(item)


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

    def undo(self):
        for item, old_pos in zip(self.items, self.old_positions):
            item.setPos(old_pos)


class PositionChangeCommand(QUndoCommand):
    def __init__(self, parent, item, old, new):
        super().__init__()
        self.item = item
        self.old = old
        self.new = new
        self.parent = parent

    def redo(self):
        self.item.setPos(self.new)

    def undo(self):
        self.item.setPos(self.old)


class AlignMultipleItemsCommand(QUndoCommand):
    def __init__(self, parent, items, old_positions, new_positions):
        super().__init__()
        self.items = items
        self.old_positions = old_positions
        self.new_positions = new_positions
        self.parent = parent

    def redo(self):
        for item, new_pos in zip(self.items, self.new_positions):
            item.moveBy(new_pos.x(), new_pos.y())

    def undo(self):
        for item, old_pos in zip(self.items, self.old_positions):
            item.setPos(old_pos)


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


class MouseRotationCommand(QUndoCommand):
    def __init__(self, item, old, new):
        super().__init__()
        self.item = item
        self.old = old
        self.new = new

    def redo(self):
        self.item.setRotation(self.new)

    def undo(self):
        self.item.setRotation(self.old)


class TransformCommand(QUndoCommand):
    def __init__(self, items, old_transforms, new_transforms):
        super().__init__()
        self.items = items
        self.old_transforms = old_transforms
        self.new_transforms = new_transforms

    def redo(self):
        for item, new_transform in zip(self.items, self.new_transforms):
            item.setTransform(new_transform)

    def undo(self):
        for item, old_transform in zip(self.items, self.old_transforms):
            item.setTransform(old_transform)


class OrbTransformCommand(QUndoCommand):
    def __init__(self, item, old_values: list, new_values: list):
        super().__init__()
        self.item = item
        self.old_scale = old_values[0]
        self.old_rotation = old_values[1]
        self.new_scale = new_values[0]
        self.new_rotation = new_values[1]

    def redo(self):
        self.item.setScale(self.new_scale)
        self.item.setRotation(self.new_rotation)

    def undo(self):
        self.item.setScale(self.old_scale)
        self.item.setRotation(self.old_rotation)


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

    def undo(self):
        for item, old_rotation in zip(self.items, self.old_rotations):
            item.setRotation(old_rotation)


class ScaleMultipleCommand(QUndoCommand):
    def __init__(self, items, old_scales, new_scale):
        super().__init__()
        self.items = items
        self.old_scales = old_scales
        self.new_scale = new_scale

    def redo(self):
        for item in self.items:
            item.setScale(self.new_scale)

    def undo(self):
        for item, old_rotation in zip(self.items, self.old_scales):
            item.setScale(old_rotation)


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

    def undo(self):
        for item, old_rotation in zip(self.items, self.old_rotations):
            item.setRotation(old_rotation)


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
    def __init__(self, items, old_fonts, new_font, old_colors, new_color, old_aligns, new_align):
        super().__init__()

        self.items = items
        self.old_fonts = old_fonts
        self.new_font = new_font
        self.old_colors = old_colors
        self.new_color = new_color
        self.old_aligns = old_aligns
        self.new_align = new_align

    def redo(self):
        for item in self.items:
            item.setFont(self.new_font)
            item.setDefaultTextColor(self.new_color)
            item.setTextAlignment(self.new_align)

            item.update()

    def undo(self):
        for item, old_font, old_color, old_align in zip(self.items, self.old_fonts, self.old_colors,
                                                                   self.old_aligns):
            item.setFont(old_font)
            item.setDefaultTextColor(old_color)
            item.setTextAlignment(old_align)

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
    def __init__(self, items):
        super().__init__()

        self.items = items
        self.old_states = [
            {
                'transform': item.transform(),
                'rotation': item.rotation(),
                'scale': item.scale(),
                'opacity': item.opacity()
            }
            for item in items
        ]

    def redo(self):
        for item in self.items:
            item.resetTransform()
            item.setScale(1)
            item.setRotation(0)
            item.setOpacity(1.0)  # Opacity should be between 0.0 and 1.0

    def undo(self):
        for item, state in zip(self.items, self.old_states):
            item.setTransform(state['transform'])
            item.setScale(state['scale'])
            item.setRotation(state['rotation'])
            item.setOpacity(state['opacity'])


class CanvasSizeEditCommand(QUndoCommand):
    def __init__(self, items, old_sizes, new_width, new_height):
        super().__init__()

        self.items = items
        self.old_sizes = old_sizes
        self.new_width = new_width
        self.new_height = new_height

    def redo(self):
        for item in self.items:
            item.setRect(0, 0, self.new_width, self.new_height)

    def undo(self):
        for item, (old_width, old_height) in zip(self.items, self.old_sizes):
            item.setRect(0, 0, old_width, old_height)


class CanvasNameEditCommand(QUndoCommand):
    def __init__(self, items, old_names, new_name):
        super().__init__()

        self.items = items
        self.old_names = old_names
        self.new_name = new_name

    def redo(self):
        for item in self.items:
            item.setName(self.new_name)
            item.setToolTip(self.new_name)

    def undo(self):
        for item, old_name in zip(self.items, self.old_names):
            item.setName(old_name)
            item.setToolTip(old_name)


class MultiCanvasNameEditCommand(QUndoCommand):
    def __init__(self, items: list[QGraphicsItem], old_names: list[str], new_names: list[str]):
        super().__init__()

        self.items = items
        self.old_names = old_names
        self.new_names = new_names

    def redo(self):
        for item, name in zip(self.items, self.new_names):
            item.setName(name)

    def undo(self):
        for item, old_name in zip(self.items, self.old_names):
            item.setName(old_name)


class LayerChangeCommand(QUndoCommand):
    def __init__(self, items, old_z_values, new_z_values):
        super().__init__()

        self.items = items
        self.old_z_values = old_z_values
        self.new_z_values = new_z_values

    def redo(self):
        for item, new_z in zip(self.items, self.new_z_values):
            item.setZValue(new_z)

    def undo(self):
        for item, old_z in zip(self.items, self.old_z_values):
            item.setZValue(old_z)
