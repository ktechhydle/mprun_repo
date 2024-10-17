class LimitedAccess:
    def __init__(self, toolbox, document_toolbar, item_toolbar, toolbar, menu_bar, canvas, canvas_view, std_types: list):
        self.panel_container = toolbox
        self.document_toolbar = document_toolbar
        self.item_toolbar = item_toolbar
        self.left_toolbar = toolbar
        self.menubar = menu_bar
        self.scene = canvas
        self.view = canvas_view
        self.std_types = std_types

    def __getattr__(self, name):
        # Define what attributes the user is allowed to access
        allowed_attributes = ['panel_container', 'document_toolbar', 'item_toolbar', 'left_toolbar', 'menubar', 'scene',
                              'view']

        for standard_type in self.std_types:
            setattr(self, standard_type.__name__, standard_type)
            allowed_attributes.append(standard_type.__name__)

        if name in allowed_attributes:
            return object.__getattribute__(self, name)
        else:
            raise AttributeError(f"Access to '{name}' is not allowed.")
