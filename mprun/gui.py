from src.gui.custom_widgets import *


class base_window(QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)


class base_widget(QWidget):
    def __init__(self, *args):
        super().__init__(*args)


class base_dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class panel_container(CustomToolbox):
    def __init__(self, *args):
        super().__init__(*args)


class toolbar(CustomToolbar):
    def __init__(self, *args):
        super().__init__(*args)


class toolbutton(CustomToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__()


class icon_label(CustomIconWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class horizontal_splitter(HorizontalSeparator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class color_picking_button(CustomColorDisplayButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class color_picker(CustomColorPicker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class dockable(CustomDockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class spinbox(CustomSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class library_list(CustomListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class horizontal_layout(base_widget):
    def __init__(self):
        super().__init__()

        self._layout = QHBoxLayout()
        self.setLayout(self._layout)


class searchable(CustomSearchBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class standard_viewer(CustomViewWidget):
    def __init__(self):
        super().__init__()


class linked_label(CustomExternalLinkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class menubar(CustomMenuBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class menu(CustomMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class more_or_less_label(CustomMoreOrLessLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
