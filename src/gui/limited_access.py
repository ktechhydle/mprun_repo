class LimitedAccess:
    def __init__(self, toolbox, item_toolbar, toolbar, menu_bar, canvas, canvas_view):
        self.panel_container = toolbox
        self.top_toolbar = item_toolbar
        self.left_toolbar = toolbar
        self.menubar = menu_bar
        self.scene = canvas
        self.view = canvas_view

    def __getattr__(self, name):
        # Define what attributes the user is allowed to access
        allowed_attributes = ['panel_container', 'top_toolbar', 'left_toolbar', 'menubar', 'scene', 'view']
        if name in allowed_attributes:
            return object.__getattribute__(self, name)
        else:
            raise AttributeError(f"Access to '{name}' is not allowed.")
