import sys

from src.framework.undo_commands import MultiItemPositionChangeCommand
from src.gui.custom_widgets import *
from src.scripts.app_internal import *
from src.scripts.imports import *


class CanvasItemSelector(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Canvas")
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowModality(Qt.ApplicationModal)
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
        self.transparent_check_btn.clicked.connect(self.canvas_changed)
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

                self.watermark_item = WaterMarkItem(QPixmap('ui/Main Logos/MPRUN_icon.png'))
                self.canvas.addItem(self.watermark_item)

                selected_item = self.canvas_chooser_combo.itemData(self.canvas_chooser_combo.currentIndex())

                self.watermark_item.setScale(0.1)
                self.watermark_item.setZValue(10000)
                self.watermark_item.setToolTip('MPRUN Watermark')
                self.watermark_item.setPos(selected_item.sceneBoundingRect().bottomRight().x() - 65,
                                           selected_item.sceneBoundingRect().bottomRight().y() - 65)

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

        if self.transparent_check_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    b = item.brush()
                    p = item.pen()
                    b.setColor(QColor(Qt.transparent))
                    p.setColor(QColor(Qt.transparent))

                    item.setBrush(b)
                    item.setPen(p)

        else:
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.restore()

        self.view.fitInView(selected_item.sceneBoundingRect(), Qt.KeepAspectRatio)

    def closeEvent(self, e):
        self.parent().use_exit_add_canvas()

        for item in self.canvas.items():
            if isinstance(item, WaterMarkItem):
                self.canvas.removeItem(item)
                self.watermark_item = None


class AllCanvasExporter(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export All")
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(750)
        self.setFixedHeight(500)

        self.canvas = canvas
        self.canvas.parentWindow.use_exit_add_canvas()
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
        for value, key in export_all_file_types.items():
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
                        self.watermark_item = WaterMarkItem(QPixmap('ui/Main Logos/MPRUN_icon.png'))
                        self.canvas.addItem(self.watermark_item)

                        self.watermark_item.setScale(0.1)
                        self.watermark_item.setZValue(10000)
                        self.watermark_item.setToolTip('MPRUN Watermark')
                        self.watermark_item.setPos(item.sceneBoundingRect().bottomRight().x() - 65,
                                                   item.sceneBoundingRect().bottomRight().y() - 65)

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
                subdirectory = os.path.join(directory,
                                            self.folder_name_entry.text() if self.folder_name_entry.text() != '' else 'Canvas Assets')
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
                self.canvas.views()[0].showMessage('Export Finished',
                                                   f'Export to {subdirectory} completed successfully.')

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


class ArrangeWin(QDialog):
    def __init__(self, canvas, parent):
        super().__init__(parent)
        self.setWindowTitle("Arrange Canvases")
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(325)
        self.setFixedHeight(250)

        self.canvas = canvas

        self.setLayout(QVBoxLayout())

        self.createUI()

    def createUI(self):
        count = 0

        for i in self.canvas.items():
            if isinstance(i, CanvasItem):
                count += 1

        canvas_count_label = QLabel(f'<b>Canvases: {count}</b>')
        apply_recommended_btn = QPushButton('Apply Recommended Settings')
        apply_recommended_btn.clicked.connect(lambda: self.apply_recommended(count))
        rows_label = QLabel('Rows:')
        columns_label = QLabel('Columns:')
        spacing_label = QLabel('Spacing:')

        self.rows_spin = QSpinBox()
        self.rows_spin.setFixedWidth(100)
        self.rows_spin.setRange(1, 10000)
        self.columns_spin = QSpinBox()
        self.columns_spin.setFixedWidth(100)
        self.columns_spin.setRange(1, 10000)
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setFixedWidth(100)
        self.spacing_spin.setSuffix(' pt')
        self.spacing_spin.setRange(1, 10000)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        # Add canvas count label
        canvas_count_layout = ToolbarHorizontalLayout()
        canvas_count_layout.layout.addWidget(canvas_count_label)
        canvas_count_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(canvas_count_layout)

        # Add recommended solution btn
        recommended_layout = ToolbarHorizontalLayout()
        recommended_layout.layout.addWidget(apply_recommended_btn)
        recommended_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(recommended_layout)
        self.layout().addWidget(HorizontalSeparator())

        # Add rows label and spinbox
        rows_layout = ToolbarHorizontalLayout()
        rows_layout.layout.addWidget(rows_label)
        rows_layout.layout.addWidget(self.rows_spin)
        rows_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(rows_layout)

        # Add columns label and spinbox
        columns_layout = ToolbarHorizontalLayout()
        columns_layout.layout.addWidget(columns_label)
        columns_layout.layout.addWidget(self.columns_spin)
        columns_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(columns_layout)

        # Add spacing label and spinbox
        spacing_layout = ToolbarHorizontalLayout()
        spacing_layout.layout.addWidget(spacing_label)
        spacing_layout.layout.addWidget(self.spacing_spin)
        spacing_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(spacing_layout)

        # Add buttons at the bottom
        self.layout().addWidget(self.button_group)

    def accept(self):
        rows = self.rows_spin.value()
        columns = self.columns_spin.value()
        spacing = self.spacing_spin.value()

        canvas_items = [item for item in self.canvas.items() if isinstance(item, CanvasItem)]
        old_positions = [item.pos() for item in canvas_items]  # Store original positions
        new_positions = []

        current_row = 0
        current_column = 0
        max_height_in_row = 0
        x = 0
        y = 0

        for i, item in enumerate(canvas_items):
            item_width = item.boundingRect().width()
            item_height = item.boundingRect().height()

            if current_column >= columns:
                # Move to the next row
                current_column = 0
                current_row += 1
                x = 0
                y += max_height_in_row + spacing
                max_height_in_row = 0

            # Calculate new position and store it
            new_pos = QPointF(x, y)
            new_positions.append(new_pos)

            # Position the item
            item.setPos(new_pos)

            # Update the x position for the next item
            x += item_width + spacing

            # Track the maximum height in the current row
            max_height_in_row = max(max_height_in_row, item_height)

            current_column += 1

        # Create and push the undo command
        command = MultiItemPositionChangeCommand(self.canvas.parentWindow, canvas_items, old_positions, new_positions)
        self.canvas.addCommand(command)

        self.close()

    def apply_recommended(self, count):
        self.rows_spin.setValue(2)
        self.columns_spin.setValue(int(count / 2))
        self.spacing_spin.setValue(count * 10 if count < 12 else 50)


class AboutWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About MPRUN')
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setFixedWidth(500)
        self.setStyleSheet('border-radius: 5px;')
        self.setWindowModality(Qt.ApplicationModal)

        self.create_ui()

    def create_ui(self):
        # Create main layout
        self.setLayout(QVBoxLayout())

        # Tabs, tab widget
        self.tab_view = QTabWidget(self)
        self.about_tab = QWidget(self)
        self.about_tab.setLayout(QVBoxLayout())
        self.license_tab = QWidget(self)
        self.license_tab.setLayout(QVBoxLayout())
        self.more_info_tab = QWidget(self)
        self.more_info_tab.setLayout(QVBoxLayout())
        self.tab_view.addTab(self.about_tab, 'About')
        self.tab_view.addTab(self.license_tab, 'License')
        self.tab_view.addTab(self.more_info_tab, 'More Info')
        self.layout().addWidget(self.tab_view)

        # Create about tab
        about_text = '''
MPRUN is a proof of concept that computer software can be useful for 
Snowboard and Ski Athletes to help plan competition runs, tricks, or even goals.

Development started in late January 2024, when athlete Keller Hydle realized the 
power of building apps. 

Keller saw a missed opportunity when it came to Snowboard Competitions, there was really no way to create a solid plan for any event. That's when he came up with MPRUN, a software that would assist athletes in creating comp runs. 

Some athletes (including Keller) struggle with creating good plans, especially for big events like Rev-Tour, and that's where MPRUN comes in. 

MPRUN allows users to visualize comp runs on computer and paper, quickly and easily. It includes a proper toolset to create documents that match course setups, draw lines, and label tricks along the course.
        '''
        about_label = QLabel(about_text, self)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignLeft)
        mp_software_logo = QLabel('', self)
        mp_software_logo.setAlignment(Qt.AlignCenter)
        mp_software_logo.setPixmap(
            QPixmap('ui/Main Logos/MP_Software_Logo.png').scaled(QSize(200, 200), Qt.KeepAspectRatio))
        fsf_logo = QLabel('', self)
        fsf_logo.setAlignment(Qt.AlignCenter)
        fsf_logo.setPixmap(
            QPixmap('ui/Main Logos/free_software_foundation_logo.svg').scaled(QSize(400, 400), Qt.KeepAspectRatio))
        self.about_tab.layout().addWidget(about_label)
        self.about_tab.layout().addStretch()
        self.about_tab.layout().addWidget(mp_software_logo)
        self.about_tab.layout().addWidget(fsf_logo)

        # Create licence tab
        license_text = '''
This program is free software and is distributed under the GNU General Public License, version 3. In short, this means you are free to use and distribute MPRUN for any purpose, commercial or non-commercial, without any restrictions. 

You are also free to modify the program as you wish, with the only restriction that if you distribute the modified version, you must provide access to its source code.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. For more details about the license, check the LISCENSE.txt file included with this distribution.


FILES MADE USING MPRUN:

All files either saved or exported from MPRUN in any format (SVG, PNG, JPG, etc.) are owned by the creators of the work (that's you!) and/or the original authors in case you use derivative works. 

You are responsible for publishing your work under a license of your choosing and for tracking your use of derivative works in the software.
        '''
        license_label = QLabel(license_text, self)
        license_label.setWordWrap(True)
        license_label.setAlignment(Qt.AlignLeft)
        self.license_tab.layout().addWidget(license_label)
        self.license_tab.layout().addStretch()

        # Create more info tab
        credits_label = QLinkLabel('Credits',
                                   'https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit?usp=sharing')
        contact_label = QLinkLabel('Contact Us', 'mailto:ktechindustries2019@gmail.com')
        self.more_info_tab.layout().addWidget(credits_label)
        self.more_info_tab.layout().addWidget(contact_label)
        self.more_info_tab.layout().addStretch()


class VersionWin(QWidget):
    def __init__(self, version):
        super().__init__()
        self.setWindowTitle('MPRUN Version')
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setFixedSize(500, 250)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.version = version

        self.create_ui()

    def create_ui(self):
        # Create main layout
        layout = QVBoxLayout()

        # App image and label
        mprun_img_label = QLabel(self)
        pixmap = QPixmap("ui/Main Logos/MPRUN_icon.png").scaled(80, 80,
                                                                Qt.KeepAspectRatio)
        mprun_img_label.setPixmap(pixmap)
        mprun_img_label.move(20, 20)

        # Text label
        text = f'''
{self.version}

Copyright © K-TECH Industries 2024, All rights reserved.

If you encounter any issues or have suggestions for improvements, contact us at:
        '''
        label = QLabel(text, self)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft)
        label.move(20, 190)

        email_label = QLinkLabel('K-TECH Industries', 'mailto:ktechindustries2019@gmail.com')

        # Add widgets to layout
        layout.addWidget(mprun_img_label)
        layout.addWidget(label)
        layout.addWidget(email_label)

        # Set layout to the main window
        self.setLayout(layout)

    def mousePressEvent(self, e):
        self.close()


class FindActionWin(QWidget):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowTitle('Find Action')
        self.setFixedHeight(500)
        self.setFixedWidth(300)

        # Create a QVBoxLayout and set it as the layout for the QWidget
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QLineEdit for searching
        self.searchInput = QLineEdit()
        self.searchInput.setObjectName('modernLineEdit')
        self.searchInput.setPlaceholderText("Search actions...")

        # Create a QListWidget
        self.listWidget = QListWidget()

        # Add some items to the QListWidget
        self.actions = actions
        self.listWidget.addItems(self.actions)

        # Add the search input and the QListWidget to the layout
        layout.addWidget(self.searchInput)
        layout.addWidget(self.listWidget)

        # Connect the textChanged signal of the search input to the search method
        self.searchInput.textChanged.connect(self.searchActions)

        # Connect itemClicked signal of the listWidget to a method
        self.listWidget.itemClicked.connect(self.performAction)

    def searchActions(self):
        # Get the search text
        searchText = self.searchInput.text().lower()

        # Clear the QListWidget
        self.listWidget.clear()

        # Filter actions based on search text and add them back to the QListWidget
        filteredActions = [action for action in self.actions if searchText in action.lower()]
        self.listWidget.addItems(filteredActions)

    def performAction(self, item):
        action_name = item.text()
        widget = self.actions.get(action_name)
        if widget:
            # Example action: toggling visibility of the widget
            if isinstance(widget, QAction):
                widget.trigger()

            elif isinstance(widget, (QPushButton, QCheckBox, QColorButton)):
                if widget.isCheckable():
                    if widget.isChecked():
                        widget.setChecked(False)
                        widget.click()

                    else:
                        widget.click()

                else:
                    widget.click()

            elif isinstance(widget, (QSpinBox, QDoubleSpinBox, QComboBox)):
                widget.setFocus(Qt.FocusReason.MouseFocusReason)

            self.close()


class DisclaimerWin(QMessageBox):
    def __init__(self, data_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle('DISCLAIMER')
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)

        self.data_file = data_file
        self.setText(use_disclaimer)

        self.show_on_startup_btn = QCheckBox()
        self.show_on_startup_btn.setText('Show this message on startup')

        self.setCheckBox(self.show_on_startup_btn)


class SettingsWin(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Settings (Beta)')
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(700)

        self.p = parent
        self.setLayout(QVBoxLayout())

        self.createGeneralSettings()
        self.createPerformanceSettings()
        self.createUI()
        self.setDefaults()

    def createGeneralSettings(self):
        self.general_tab = QWidget(self)
        self.general_tab.setLayout(QVBoxLayout())

        def createDialogAndGuiGB():
            gui_gb = QGroupBox('Dialogs and GUI')
            gui_gb.setLayout(QVBoxLayout())

            self.show_tip_of_day_checkbtn = QCheckBox('Show tip of the day')
            reset_dialogs_btn = QPushButton('Reset all dialogs')
            reset_dialogs_btn.setFixedWidth(200)
            reset_dialogs_btn.clicked.connect(self.restore_dialogs)

            gui_gb.layout().addWidget(self.show_tip_of_day_checkbtn)
            gui_gb.layout().addWidget(reset_dialogs_btn)

            self.general_tab.layout().addWidget(gui_gb)

        createDialogAndGuiGB()
        self.general_tab.layout().addStretch()

    def createPerformanceSettings(self):
        self.performance_tab = QWidget(self)
        self.performance_tab.setLayout(QVBoxLayout())

        def createMemoryGB():
            memory_gb = QGroupBox('Memory')
            memory_gb_layout = QVBoxLayout()
            memory_gb.setLayout(memory_gb_layout)

            undo_limit_label = QLabel('Undo limit <i>(a higher value increases memory usage)</i>:')
            self.undo_limit_spin = QSpinBox(self)
            self.undo_limit_spin.setRange(5, 1000)
            self.undo_limit_spin.setFixedWidth(100)
            undo_hlayout = ToolbarHorizontalLayout()
            undo_hlayout.layout.addWidget(undo_limit_label)
            undo_hlayout.layout.addWidget(self.undo_limit_spin)
            undo_hlayout.layout.addStretch()
            memory_gb_layout.addWidget(undo_hlayout)

            self.performance_tab.layout().addWidget(memory_gb)

        def createGPUGB():
            gpu_gb = QGroupBox('GPU')
            gpu_gb.setLayout(QVBoxLayout())

            compatible_label = QLabel()
            try:
                subprocess.check_output('nvidia-smi')
                compatible_label.setText('<i>Compatible GPU available.</i>')
            except Exception:  # this command not being found can raise quite a few different errors depending on the configuration
                compatible_label.setText('<i>No compatible GPU available.</i>')

            self.use_gpu_checkbtn = QCheckBox('Use GPU Acceleration')

            gpu_gb.layout().addWidget(compatible_label)
            gpu_gb.layout().addWidget(self.use_gpu_checkbtn)
            self.performance_tab.layout().addWidget(gpu_gb)

        createMemoryGB()
        createGPUGB()

        self.performance_tab.layout().addStretch()

    def createUI(self):
        self.tab_view = QTabWidget(self)
        self.tab_view.setDocumentMode(True)
        self.tab_view.setUsesScrollButtons(False)
        self.tab_view.addTab(self.general_tab, 'General')
        self.tab_view.addTab(self.performance_tab, 'Performance')

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Apply', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Discard', QDialogButtonBox.RejectRole)
        self.button_group.addButton('Reset', QDialogButtonBox.HelpRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.decline)
        self.button_group.helpRequested.connect(self.restore)

        self.layout().addWidget(self.tab_view)
        self.layout().addWidget(self.button_group)

    def setDefaults(self):
        _data = self.p.read_settings()

        for data in _data:
            self.undo_limit_spin.setValue(data['undo_limit'])
            self.show_tip_of_day_checkbtn.setChecked(data['show_daily_tips'])
            self.use_gpu_checkbtn.setChecked(data['use_gpu'])

    def accept(self):
        _data = self.p.read_settings()

        for data in _data:
            data['undo_limit'] = self.undo_limit_spin.value()
            data['show_daily_tips'] = self.show_tip_of_day_checkbtn.isChecked()
            data['use_gpu'] = self.use_gpu_checkbtn.isChecked()

        self.p.write_settings(_data)

        self.close()

    def decline(self):
        self.close()

    def restore_dialogs(self):
        self.show_tip_of_day_checkbtn.setChecked(True)

        _data = self.p.read_settings()

        for data in _data:
            data['disclaimer_read'] = False
            data['show_daily_tips'] = True

        self.p.write_settings(_data)

    def restore(self):
        self.undo_limit_spin.setValue(200)
        self.show_tip_of_day_checkbtn.setChecked(True)
        self.use_gpu_checkbtn.setChecked(True)


class TipWin(QDialog):
    def __init__(self, label: str, tip: str, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setLayout(QHBoxLayout())

        img = QLabel('')
        img.setPixmap(QPixmap('ui/UI Icons/Major/info_circle.svg').scaled(35, 35,
                                                                          Qt.KeepAspectRatio,
                                                                          Qt.SmoothTransformation))
        main_label = QLabel(f'<b>{label}</b>')
        text = QLabel(tip)
        text.setWordWrap(True)

        layout1 = QVBoxLayout()
        layout1.addWidget(main_label)
        layout1.addWidget(text)
        layout1.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(layout1)

        close_btn = QPushButton('X')
        close_btn.setToolTip('Close')
        close_btn.setStyleSheet('font-family: Source Code Pro')
        close_btn.setFixedWidth(20)
        close_btn.clicked.connect(self.delete)

        self.layout().addWidget(img)
        self.layout().addWidget(widget)
        self.layout().addWidget(close_btn)

        self.show()

    def delete(self):
        self.close()
        del self  # clear from memory
