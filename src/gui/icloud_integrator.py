from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException
from pathlib import Path
from src.scripts.imports import *
from src.gui.custom_widgets import ToolbarHorizontalLayout
from src.gui.app_screens import AllCanvasExporter
from src.framework.custom_classes import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

downloads_path = str(Path.home() / "Downloads")


class iCloudIntegraterWin(QDialog):
    def __init__(self, canvas, parent):
        super().__init__()
        self.setWindowTitle('Share To iCloud')
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(300)
        self.setLayout(QVBoxLayout())
        self.canvas = canvas
        self.parent = parent

        self.createUI()

    def createUI(self):
        apple_id_label = QLabel('<b>Apple ID:</b>')
        self.apple_id_input = QLineEdit()
        id_hlayout = ToolbarHorizontalLayout()
        id_hlayout.layout.addWidget(apple_id_label)
        id_hlayout.layout.addWidget(self.apple_id_input)

        password_label = QLabel('<b>Password:</b>')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_hlayout = ToolbarHorizontalLayout()
        password_hlayout.layout.addWidget(password_label)
        password_hlayout.layout.addWidget(self.password_input)

        warning = QLabel('<i>We do not collect any Apple ID data, such as names, passwords, or emails.</i>')
        warning.setAlignment(Qt.AlignCenter)
        warning.setWordWrap(True)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Share', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.finish)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(id_hlayout)
        self.layout().addWidget(password_hlayout)
        self.layout().addWidget(warning)
        self.layout().addWidget(self.button_group)

    def finish(self):
        try:
            try:
                api = PyiCloudService(self.apple_id_input.text(), self.password_input.text())
            except PyiCloudFailedLoginException:
                QMessageBox.warning(self.parent, 'Incorrect Credentials', 'Your Apple ID or Password was incorrect, '
                                                                          'please enter the correct credentials.')
                return

            if api.requires_2fa:
                code, ok = QInputDialog.getInt(self.parent, '2FA Code', 'Enter the 2FA code sent to your Apple device:')

                if ok:
                    if api.validate_2fa_code(str(code)):
                        for photo in self.export():
                            with open(photo, 'rb') as f:
                                api.drive['Downloads'].upload(f, filename=os.path.basename(photo))
                    else:
                        QMessageBox.warning(self.parent, 'Incorrect Code', 'Failed to verify security code.')
                        return

            else:
                for photo in self.export():
                    with open(photo, 'rb') as f:
                        api.drive['Downloads'].upload(f)

            QMessageBox.information(self.parent, 'File Shared', 'The file has successfully been '
                                                                'transferred to iCloud. It has been saved '
                                                                'to your "Downloads" folder.')

        except Exception as e:
            QMessageBox.critical(self.parent, 'Error', f'An unexpected error occurred: {e}')

    def export(self):
        try:
            # Get the user's Downloads folder
            downloads_folder = downloads_path

            # Create a subdirectory in Downloads
            subdirectory = os.path.join(downloads_folder,
                                        'Canvas Assets')
            os.makedirs(subdirectory, exist_ok=True)

            file_extension = '.png'  # Set file extension to PNG
            tooltip_count = {}
            exported_filenames = []

            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    tooltip = item.toolTip()
                    if tooltip in tooltip_count:
                        tooltip_count[tooltip] += 1
                    else:
                        tooltip_count[tooltip] = 1

                    unique_filename = f"{tooltip}_{tooltip_count[tooltip]}{file_extension}"
                    filename = os.path.join(subdirectory, unique_filename)
                    exported_filenames.append(filename)

                    # Export the item as a PNG
                    self.export_as_png(filename, item)

            return exported_filenames

        except Exception as e:
            print(e)

    def export_as_png(self, filename, selected_item):
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
