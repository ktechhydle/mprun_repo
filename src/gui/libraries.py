from src.framework.graphics_framework import *
from src.gui.custom_widgets import *
from src.scripts.imports import *


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.all_items = []

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(item.data(Qt.UserRole))])
            drag.setMimeData(mime_data)

            # Optional: set a drag image
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def filter_items(self, text):
        for item in self.all_items:
            item.setHidden(True)

            if text.lower() in item.text().lower():
               item.setHidden(False)

class LibraryWidget(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.current_folder_path = ""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.canvas = canvas

        # List widget for the library
        self.library_list_widget = DragDropListWidget()
        self.library_list_widget.setStyleSheet('border: none')
        self.library_list_widget.setIconSize(QSize(80, 80))

        # Library button
        self.open_library_button = QPushButton("Open Library")
        self.open_library_button.setToolTip('Open library from local directory')
        self.reload_library_button = QPushButton("")
        self.reload_library_button.setFixedWidth(28)
        self.reload_library_button.setStyleSheet('border: none')
        self.reload_library_button.setIcon(QIcon('ui/UI Icons/refresh_icon.svg'))
        self.reload_library_button.setToolTip('Reload the current library')

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_library)

        library_btn_hlayout = QHBoxLayout()
        library_btn_hlayout.addWidget(self.open_library_button)
        library_btn_hlayout.addWidget(self.reload_library_button)

        self.layout.addLayout(library_btn_hlayout)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.library_list_widget)

        # Connect button to the method
        self.open_library_button.clicked.connect(self.open_library)
        self.reload_library_button.clicked.connect(self.reload_library)

    def open_library(self):
        # Open file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Library Folder")

        if folder_path:
            self.current_folder_path = folder_path
            self.load_svg_library(folder_path)

    def reload_library(self):
        if self.current_folder_path:
            self.load_svg_library(self.current_folder_path)

    def load_svg_library(self, folder_path):
        # Clear existing items in the list widget
        self.library_list_widget.clear()
        self.library_list_widget.all_items = []

        # List all SVG files in the selected folder
        svg_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

        # Check if no SVG files are found
        if not svg_files:
            self.library_list_widget.setDragEnabled(False)
            list_item = QListWidgetItem('No files found')
            list_item.setIcon(QIcon('ui/UI Icons/folder_failed_icon.svg'))
            self.library_list_widget.setIconSize(QSize(40, 40))
            self.library_list_widget.addItem(list_item)

        else:
            self.library_list_widget.setDragEnabled(True)
            # Add each SVG file to the list widget
            for svg_file in svg_files:
                list_item = QListWidgetItem(svg_file)
                list_item.setData(Qt.UserRole, os.path.join(folder_path, svg_file))
                list_item.setIcon(QIcon(os.path.join(folder_path, svg_file)))
                self.library_list_widget.setIconSize(QSize(80, 80))
                self.library_list_widget.addItem(list_item)
                self.library_list_widget.all_items.append(list_item)

    def filter_library(self, text):
        try:
            self.library_list_widget.filter_items(text)

        except Exception as e:
            print(e)
