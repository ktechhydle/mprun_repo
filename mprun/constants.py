from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsItem

TIP_WINDOW_Y_PADDING = -5
TIP_WINDOW_X_PADDING = 10
DEFAULT_PANEL_WIDTH = 280
DEFAULT_LINE_EDIT_WIDTH = 200
ITEM_SELECTABLE, ITEM_MOVABLE = (QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                                 QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
WINDOW_TYPE_TOOL = Qt.WindowType.Tool
WINDOW_TYPE_POPUP = Qt.WindowType.Popup
WINDOW_TYPE_TOOLTIP = Qt.WindowType.ToolTip
WINDOW_TYPE_FRAMELESS = Qt.WindowType.FramelessWindowHint
WINDOW_MODAL = Qt.WindowModality.ApplicationModal
APPLICATION_ATTRIBUTE = Qt.ApplicationAttribute
LEFT_BUTTON = Qt.MouseButton.LeftButton
RIGHT_BUTTON = Qt.MouseButton.RightButton
MIDDLE_BUTTON = Qt.MouseButton.MiddleButton
SHIFT_MODIFIER = Qt.KeyboardModifier.ShiftModifier
CONTROL_MODIFIER = Qt.KeyboardModifier.ControlModifier