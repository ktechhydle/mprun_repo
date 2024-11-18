import mprun.gui
from mprun.constants import WINDOW_MODAL
from src.framework.items import *
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException
from pathlib import Path


if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

downloads_path = str(Path.home() / "Downloads")


class iCloudIntegratorWin(mprun.gui.base_dialog):
    def __init__(self, canvas, parent):
        super().__init__()
        self.setWindowTitle('Share To iCloud')
        self.setWindowIcon(QIcon('mprun_assets/assets/logos/mprun_icon.png'))
        self.setWindowModality(WINDOW_MODAL)
        self.setObjectName('tipWindow')
        self.setFixedSize(300, 250)
        self.setLayout(QVBoxLayout())
        self.canvas = canvas
        self.parent = parent

        self.createUI()
        self.default()
        self.default()

    def createUI(self):
        apple_id_label = QLabel('<b>Apple ID:</b>')
        self.apple_id_input = QLineEdit()

        password_label = QLabel('<b>Password:</b>')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.save_for_later_check_btn = QCheckBox('Save this info for later')
        self.save_for_later_check_btn.setChecked(True)

        warning = QLabel('<i>*We do not collect any Apple ID data, such as names, passwords, or emails.</i>')
        warning.setWordWrap(True)

        self.button_group = QDialogButtonBox(self)
        self.button_group.setCenterButtons(True)
        self.button_group.addButton('Share', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.finish)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(apple_id_label)
        self.layout().addWidget(self.apple_id_input)
        self.layout().addWidget(password_label)
        self.layout().addWidget(self.password_input)
        self.layout().addWidget(self.save_for_later_check_btn)
        self.layout().addSpacing(20)
        self.layout().addWidget(warning)
        self.layout().addStretch()
        self.layout().addWidget(self.button_group)

    def default(self):
        _data = self.parent.read_settings()

        for data in _data:
            if data['icloud_username'] and data['icloud_password']:
                self.apple_id_input.setText(data['icloud_username'])
                self.password_input.setText(data['icloud_password'])

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
                                api.drive.params["clientId"] = api.client_id
                                api.drive['Downloads'].mkdir('MPRUN')
                                api.drive['Downloads']['MPRUN'].upload(f)
                    else:
                        QMessageBox.warning(self.parent, 'Incorrect Code', 'Failed to verify security code.')
                        return

            else:
                for photo in self.export():
                    with open(photo, 'rb') as f:
                        api.drive.params["clientId"] = api.client_id
                        api.drive['Downloads'].mkdir('MPRUN')
                        api.drive['Downloads']['MPRUN'].upload(f)

            QMessageBox.information(self.parent, 'File Shared', 'The file has successfully been '
                                                                'transferred to iCloud. It has been saved '
                                                                'to the "Downloads" folder.')

            if self.save_for_later_check_btn.isChecked():
                _data = self.parent.read_settings()

                for data in _data:
                    data['icloud_username'] = self.apple_id_input.text()
                    data['icloud_password'] = self.password_input.text()

                self.parent.write_settings(_data)

            self.close()

        except Exception as e:
            QMessageBox.critical(self.parent, 'Error', f'An unexpected error occurred: {e}')

    def export(self) -> list[str]:
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
