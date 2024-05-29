from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from custom_widgets import *
from undo_commands import *

class CanvasItemSelector(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Canvas")
        self.setWindowIcon(QIcon('logos and icons/Main Logos/MPRUN_logoV3.png'))
        self.setFixedWidth(750)
        self.setFixedHeight(500)

        self.canvas = canvas
        self.watermark_item = None

        # Create the layout
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)

        self.createUI()

    def createUI(self):
        # Scene and View
        self.view = ViewWidget()
        self.view.setFixedWidth(500)
        self.view.setScene(self.canvas)
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.fitInView(self.canvas.itemsBoundingRect())

        # Labels
        selected_canvas_label = QLabel('Selected Canvas:')
        export_options_label = QLabel('Export Options:')

        # Canvas selector
        self.canvas_chooser_combo = QComboBox()
        self.canvas_chooser_combo.setToolTip('Select a canvas to export')
        self.canvas_chooser_combo.currentIndexChanged.connect(self.canvas_changed)

        # Transparent option checkbox
        self.transparent_check_btn = QCheckBox()
        self.transparent_check_btn.setText('Transparent Background')
        self.transparent_check_btn.setToolTip('Export the selected canvas with a transparent background')

        # Watermark option checkbox
        self.watermark_check_btn = QCheckBox()
        self.watermark_check_btn.setText('Add Watermark')
        self.watermark_check_btn.setToolTip('Help support us by adding an MPRUN watermark')
        self.watermark_check_btn.clicked.connect(self.add_watermark)

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip('Export the selected canvas')

        # Add widgets
        self.layout.addWidget(HorizontalSeparator())
        self.hlayout.addWidget(self.view)
        self.layout.addWidget(selected_canvas_label)
        self.layout.addWidget(self.canvas_chooser_combo)
        self.layout.addWidget(export_options_label)
        self.layout.addWidget(self.transparent_check_btn)
        self.layout.addWidget(self.watermark_check_btn)
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.export_btn)
        self.hlayout.addLayout(self.layout)

    def add_canvas_item(self, itemName, itemKey):
        if isinstance(itemKey, CanvasItem):
            values = {itemName: itemKey}
            for name, key in values.items():
                self.canvas_chooser_combo.addItem(name, key)

        else:
            pass

    def add_watermark(self):
        try:
            if self.watermark_check_btn.isChecked():
                if self.watermark_item is not None:
                    self.canvas.removeItem(self.watermark_item)

                self.watermark_item = WaterMarkItem(QPixmap('logos and icons/Main Logos/MPRUN_logoV3.png'))
                self.canvas.addItem(self.watermark_item)

                selected_item = self.canvas_chooser_combo.itemData(self.canvas_chooser_combo.currentIndex())

                self.watermark_item.setScale(0.1)
                self.watermark_item.setZValue(10000)
                self.watermark_item.setToolTip('MPRUN Watermark')
                self.watermark_item.setPos(selected_item.sceneBoundingRect().bottomRight().x() - 65, selected_item.sceneBoundingRect().bottomRight().y() - 65)

            else:
                for item in self.canvas.items():
                    if isinstance(item, WaterMarkItem):
                        self.canvas.removeItem(item)
                        self.watermark_item = None

        except Exception:
            pass

    def canvas_changed(self):
        selected_item = self.canvas_chooser_combo.itemData(self.canvas_chooser_combo.currentIndex())

        if self.watermark_item is not None:
            self.watermark_item.setPos(selected_item.sceneBoundingRect().bottomRight().x() - 65,
                                       selected_item.sceneBoundingRect().bottomRight().y() - 65)

        self.view.fitInView(selected_item.sceneBoundingRect(), Qt.KeepAspectRatio)

    def closeEvent(self, e):
        self.parent().use_exit_add_canvas()

        for item in self.canvas.items():
            if isinstance(item, WaterMarkItem):
                self.canvas.removeItem(item)
                self.watermark_item = None

class MultiCanvasItemSelector(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export All")
        self.setWindowIcon(QIcon('logos and icons/Main Logos/MPRUN_logoV3.png'))
        self.setFixedWidth(750)
        self.setFixedHeight(500)

        self.parent().use_exit_add_canvas()
        self.canvas = canvas
        self.watermark_item = None

        # Create the layout
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)

        self.createUI()

    def createUI(self):
        # Scene and View
        self.view = ViewWidget()
        self.view.setFixedWidth(500)
        self.view.setScene(self.canvas)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.fitInView(self.canvas.itemsBoundingRect(), Qt.KeepAspectRatio)

        # Labels
        file_type_label = QLabel('File Type:')
        folder_name_label = QLabel('Folder Name:')
        export_options_label = QLabel('Export Options:')

        # Canvas selector
        self.file_type_combo = QComboBox()
        self.file_type_combo.setToolTip('Select a file type')
        file_types = {
                'SVG files (*.svg)': '.svg',
                'PNG files (*.png)': '.png',
                'JPG files (*.jpg)': '.jpg',
                'JPEG files (*.jpeg)': '.jpeg',
                'TIFF files (*.tiff)': '.tiff',
                'WEBP files (*.webp)': '.webp',
                'ICO files (*.ico)': '.ico',
                'HEIC files (*.heic)': '.heic'
            }
        for value, key in file_types.items():
            self.file_type_combo.addItem(value, key)

        # Folder name entry
        self.folder_name_entry = QLineEdit()
        self.folder_name_entry.setPlaceholderText('Canvas Assets')
        self.folder_name_entry.setObjectName('modernLineEdit')
        self.folder_name_entry.setToolTip('Change the name of the folder that canvases are exported to')

        # Watermark option checkbox
        self.watermark_check_btn = QCheckBox()
        self.watermark_check_btn.setText('Add Watermark')
        self.watermark_check_btn.setToolTip('Help support us by adding an MPRUN watermark')
        self.watermark_check_btn.clicked.connect(self.add_watermark)

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip('Export all canvases with the chosen options')
        self.export_btn.clicked.connect(self.export)

        # Add widgets
        self.layout.addWidget(HorizontalSeparator())
        self.hlayout.addWidget(self.view)
        self.layout.addWidget(file_type_label)
        self.layout.addWidget(self.file_type_combo)
        self.layout.addWidget(folder_name_label)
        self.layout.addWidget(self.folder_name_entry)
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.watermark_check_btn)
        self.layout.addWidget(self.export_btn)
        self.hlayout.addLayout(self.layout)

    def add_watermark(self):
        try:
            if self.watermark_check_btn.isChecked():
                for item in self.canvas.items():
                    if isinstance(item, CanvasItem):
                        self.watermark_item = WaterMarkItem(QPixmap('logos and icons/Main Logos/MPRUN_logoV3.png'))
                        self.canvas.addItem(self.watermark_item)
        
                        self.watermark_item.setScale(0.1)
                        self.watermark_item.setZValue(10000)
                        self.watermark_item.setToolTip('MPRUN Watermark')
                        self.watermark_item.setPos(item.sceneBoundingRect().bottomRight().x() - 65, item.sceneBoundingRect().bottomRight().y() - 65)

            else:
                for item in self.canvas.items():
                    if isinstance(item, WaterMarkItem):
                        self.canvas.removeItem(item)
                        self.watermark_item = None

        except Exception:
            pass

    def export(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, 'Export Directory')

            if directory:
                # Create a subdirectory within the chosen directory
                subdirectory = os.path.join(directory, self.folder_name_entry.text() if self.folder_name_entry.text() != '' else 'Canvas Assets')
                os.makedirs(subdirectory, exist_ok=True)

                file_extension = self.file_type_combo.itemData(self.file_type_combo.currentIndex())
                for item in self.canvas.items():
                    if isinstance(item, CanvasItem):
                        filename = os.path.join(subdirectory, item.toolTip() + file_extension)
                        if file_extension == '.svg':
                            self.export_canvases_as_svg(filename, item)
                        else:
                            self.export_canvases_as_bitmap(filename, item)

                # If saving was successful, show a notification
                QMessageBox.information(self, "Export Finished", f"Export to {subdirectory} completed successfully.")

                # Open the folder on the computer
                QDesktopServices.openUrl(QUrl.fromLocalFile(subdirectory))

        except Exception as e:
            print(e)

    def export_canvases_as_svg(self, file_path, selected_item):
        try:
            # Get the bounding rect
            rect = selected_item.sceneBoundingRect()

            # Export as SVG
            svg_generator = QSvgGenerator()
            svg_generator.setFileName(file_path)
            svg_generator.setSize(rect.size().toSize())
            svg_generator.setViewBox(rect)
            svg_generator.setTitle('MPRUN SVG Document (Powered by QSvgGenerator)')

            # Clear selection
            self.canvas.clearSelection()

            # Create a QPainter to paint onto the QSvgGenerator
            painter = QPainter()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.begin(svg_generator)

            # Render the scene onto the QPainter
            self.canvas.render(painter, target=rect, source=rect)

            # End painting
            painter.end()

        except Exception as e:
            # Show export error notification
            QMessageBox.information(self, 'Export Failed', f'Export failed: {e}',
                                    QMessageBox.Ok)

    def export_canvases_as_bitmap(self, filename, selected_item):
        # Create a QImage with the size of the selected item (QGraphicsRectItem)
        rect = selected_item.sceneBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        try:
            image.save(filename)

        except Exception as e:
            # If saving failed, show an error notification
            QMessageBox.critical(self, "Export Error", f"Failed to export canvas to file: {e}")

    def closeEvent(self, e):
        self.parent().use_exit_add_canvas()

        for item in self.canvas.items():
            if isinstance(item, WaterMarkItem):
                self.canvas.removeItem(item)
                self.watermark_item = None

class CanvasEditorPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.setMaximumHeight(225)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.canvas = canvas
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_ui()

    def create_ui(self):
        canvas_label = QLabel('Canvas')
        canvas_label.setStyleSheet('font-size: 12px;')
        canvas_x_size_label = QLabel('W:')
        canvas_y_size_label = QLabel('H:')
        canvas_preset_label = QLabel('Preset:')
        canvas_name_label = QLabel('Name:')
        self.canvas_x_entry = QSpinBox(self)
        self.canvas_x_entry.setMaximum(5000)
        self.canvas_x_entry.setAlignment(Qt.AlignLeft)
        self.canvas_x_entry.setToolTip('Change the width of the canvas')
        self.canvas_x_entry.valueChanged.connect(self.update_canvas)
        self.canvas_y_entry = QSpinBox(self)
        self.canvas_y_entry.setMaximum(5000)
        self.canvas_y_entry.setAlignment(Qt.AlignLeft)
        self.canvas_y_entry.setToolTip('Change the height of the canvas')
        self.canvas_y_entry.valueChanged.connect(self.update_canvas)

        self.canvas_preset_dropdown = QComboBox(self)
        self.canvas_preset_dropdown.setFixedWidth(200)
        self.canvas_preset_dropdown.setToolTip('Change the preset of the canvas')
        self.canvas_presets = {
            'MPRUN Standard (1000 x 700)': 1,
            'Web (1920 x 1080)': 2,
            'Letter (797 x 612)': 3,
            'Legal (1008 x 612)': 4,
            'A4 (595 x 842)': 5,
            'A6 (828 x 1169)': 6,
            'Phone (1080 x 1920)': 7,
            'Custom': 'c',

        }
        for canvas, key in self.canvas_presets.items():
            self.canvas_preset_dropdown.addItem(canvas, key)
        self.canvas_preset_dropdown.setCurrentText('Custom')
        self.canvas_preset_dropdown.currentIndexChanged.connect(self.update_canvas)

        self.canvas_name_entry = QLineEdit(self)
        self.canvas_name_entry.setFixedWidth(200)
        self.canvas_name_entry.setPlaceholderText('Canvas Name')
        self.canvas_name_entry.setToolTip('Change the name of the canvas')
        self.canvas_name_entry.textChanged.connect(self.update_canvas)

        widget1 = ToolbarHorizontalLayout()
        widget1.layout.addWidget(canvas_x_size_label)
        widget1.layout.addWidget(self.canvas_x_entry)
        widget1.layout.addWidget(canvas_y_size_label)
        widget1.layout.addWidget(self.canvas_y_entry)

        widget2 = ToolbarHorizontalLayout()
        widget2.layout.addWidget(canvas_preset_label)
        widget2.layout.addWidget(self.canvas_preset_dropdown)

        widget3 = ToolbarHorizontalLayout()
        widget3.layout.addWidget(canvas_name_label)
        widget3.layout.addWidget(self.canvas_name_entry)

        self.layout.addWidget(HorizontalSeparator())
        self.layout.addWidget(canvas_label)
        self.layout.addWidget(widget1)
        self.layout.addWidget(widget2)
        self.layout.addWidget(widget3)

    def update_canvas(self):
        choice = self.canvas_preset_dropdown.itemData(self.canvas_preset_dropdown.currentIndex())

        if choice == 'c':
            pass

        elif choice == 1:
            self.canvas_x_entry.setValue(1000)
            self.canvas_y_entry.setValue(700)

        elif choice == 2:
            self.canvas_x_entry.setValue(1920)
            self.canvas_y_entry.setValue(1080)

        elif choice == 3:
            self.canvas_x_entry.setValue(792)
            self.canvas_y_entry.setValue(612)

        elif choice == 4:
            self.canvas_x_entry.setValue(1008)
            self.canvas_y_entry.setValue(792)

        elif choice == 5:
            self.canvas_x_entry.setValue(595)
            self.canvas_y_entry.setValue(842)

        elif choice == 6:
            self.canvas_x_entry.setValue(828)
            self.canvas_y_entry.setValue(1169)

        elif choice == 7:
            self.canvas_x_entry.setValue(1080)
            self.canvas_y_entry.setValue(1920)

        for item in self.canvas.selectedItems():
            if isinstance(item, CanvasItem):
                for self.child in item.childItems():
                    if isinstance(self.child, CanvasTextItem):
                        self.child.setText(self.canvas_name_entry.text())

                item.setToolTip(self.canvas_name_entry.text())

                try:
                    item.setRect(0, 0, self.canvas_x_entry.value(), self.canvas_y_entry.value())
                    self.child.setPos(item.boundingRect().x(), item.boundingRect().y())

                except Exception:
                    pass

class TextAlongPathPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.canvas = canvas

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(225)

        self.createUi()

    def createUi(self):
        main_label = QLabel('Text Along Path')
        main_label.setStyleSheet("QLabel { font-size: 12px; }")
        spacing_label = QLabel('Spacing From Path:')
        spacing_label.setStyleSheet("QLabel { font-size: 12px; }")

        self.text_along_path_check_btn = QCheckBox(self)
        self.text_along_path_check_btn.setToolTip('Add text along the path')
        self.text_along_path_check_btn.setText('Add Text Along Path')

        self.distrubute_evenly_check_btn = QCheckBox(self)
        self.distrubute_evenly_check_btn.setToolTip('Distribute the text along the path evenly')
        self.distrubute_evenly_check_btn.setText('Distribute Text Evenly')

        self.spacing_spin = QSpinBox(self)
        self.spacing_spin.setRange(-1000, 10000)
        self.spacing_spin.setSuffix(' pt')
        self.spacing_spin.setToolTip('Text spacing from path')

        self.text_entry = QLineEdit(self)
        self.text_entry.setPlaceholderText('Enter Text')
        self.text_entry.setToolTip('Enter text along the path')

        self.layout.addWidget(HorizontalSeparator())
        self.layout.addWidget(main_label)
        self.layout.addWidget(self.text_along_path_check_btn)
        self.layout.addWidget(self.distrubute_evenly_check_btn)
        self.layout.addWidget(spacing_label)
        self.layout.addWidget(self.spacing_spin)
        self.layout.addWidget(self.text_entry)

        self.text_along_path_check_btn.clicked.connect(self.update_path)
        self.distrubute_evenly_check_btn.clicked.connect(self.update_path)
        self.spacing_spin.valueChanged.connect(self.update_path)
        self.text_entry.textChanged.connect(self.update_path)

    def update_path(self):
        for item in self.canvas.selectedItems():
            if isinstance(item, CustomPathItem):
                if self.text_along_path_check_btn.isChecked():
                    command = AddTextToPathCommand(item, self.text_along_path_check_btn, False, True)
                    self.canvas.addCommand(command)
                    command2 = PathTextChangedCommand(item, item.text_along_path, self.text_entry.text())
                    self.canvas.addCommand(command2)
                    command3 = PathTextSpacingChangedCommand(item, item.text_along_path_spacing, self.spacing_spin.value())
                    self.canvas.addCommand(command3)

                    if self.distrubute_evenly_check_btn.isChecked():
                        item.setTextAlongPathFromBeginning(False)

                    else:
                        item.setTextAlongPathFromBeginning(True)

                    item.update()

                else:
                    command = AddTextToPathCommand(item, self.text_along_path_check_btn, True, False)
                    self.canvas.addCommand(command)
                    item.update()
