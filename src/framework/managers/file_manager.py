import json
import pickle
import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QGraphicsScene
from src.framework.deserializer import SceneDeserializer
from src.framework.serializer import SceneSerializer
from src.framework.data_repairer import FileDataRepairer


class SceneFileManager:
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.filename = 'Untitled'
        self.parent = None
        self.repair_needed = False

        self.serializer = SceneSerializer(self.scene)
        self.deserializer = SceneDeserializer(self.scene)

    def reset_to_default_scene(self):
        self.scene.clear()
        self.scene.setHasChanges(False)
        self.filename = 'Untitled'
        self.scene.parentWindow.setWindowTitle(f'{self.filename} - MPRUN')
        self.scene.parentWindow.create_default_objects()

    def restore(self):
        if self.scene.hasChanges():
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox(self.scene.parentWindow)
            confirmation_dialog.setWindowTitle('Close Document')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
            confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
            confirmation_dialog.setDefaultButton(QMessageBox.Save)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            if result == QMessageBox.Discard:
                self.reset_to_default_scene()

            elif result == QMessageBox.Save:
                success = self.scene.parentWindow.save()

                if success:
                    self.reset_to_default_scene()

        else:
            self.reset_to_default_scene()

    def save(self):
        if self.filename != 'Untitled':
            with open(self.filename, 'wb') as f:
                pickle.dump(self.serializer.serialize_items(), f)
                self.scene.parentWindow.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                self.scene.setHasChanges(False)

        else:
            self.saveas()

    def saveas(self):
        filename, _ = QFileDialog.getSaveFileName(self.scene.parentWindow, 'Save As', '', 'MPRUN files (*.mp)')

        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(self.serializer.serialize_items(), f)

                self.filename = filename
                self.scene.setHasChanges(False)
                self.scene.parentWindow.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                self.scene.parentWindow.update_recent_file_data(filename)
                self.scene.parentWindow.canvas_view.showMessage('File', f'File {self.filename} saved successfully.')

                return True

    def save_copy(self):
        filename, _ = QFileDialog.getSaveFileName(self.scene.parentWindow, 'Save Copy', f'{self.filename}', 'MPRUN files (*.mp)')

        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(self.serializer.serialize_items(), f)
                self.scene.parentWindow.canvas_view.showMessage('File', f'Copy file {filename} saved successfully.')

    def emergency_save(self):
        if self.filename != 'Untitled':
            with open(self.filename, 'wb') as f:
                pickle.dump(self.serializer.serialize_items(), f)

    def load(self, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.hasChanges():
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        self.scene.parentWindow.update_recent_file_data(filename)

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

                elif result == QMessageBox.Save:
                    parent.save()

                    filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        self.scene.parentWindow.update_recent_file_data(filename)

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

            else:
                filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                          'MPRUN files (*.mp)')

                if filename:
                    self.scene.undo_stack.clear()
                    self.scene.clear()
                    self.scene.parentWindow.update_recent_file_data(filename)

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserializer.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def load_from_file(self, filename, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.hasChanges():
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    if filename.endswith('.mpt'):
                        with open(filename, 'r') as f:
                            data = json.load(f)

                            self.scene.template_manager.deserialize_items(data)

                    elif filename.endswith('.mp'):
                        self.scene.undo_stack.clear()
                        self.scene.clear()

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserializer.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                            self.scene.setHasChanges(False)

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

                elif result == QMessageBox.Save:
                    success = self.save()

                    if success:
                        if filename.endswith('.mpt'):
                            with open(filename, 'r') as f:
                                data = json.load(f)

                                self.scene.template_manager.deserialize_items(data)

                        elif filename.endswith('.mp'):
                            self.scene.undo_stack.clear()
                            self.scene.clear()

                            with open(filename, 'rb') as f:
                                items_data = pickle.load(f)
                                self.deserializer.deserialize_items(items_data)

                                self.filename = filename
                                parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                                self.scene.setHasChanges(False)

                                if self.repair_needed:
                                    # Display a confirmation dialog
                                    confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                    confirmation_dialog.setWindowTitle('Open Document Error')
                                    confirmation_dialog.setIcon(QMessageBox.Warning)
                                    confirmation_dialog.setText(
                                        f"The document has file directories that could not be found. Do you want to do a file repair?")
                                    confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                    confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                    # Get the result of the confirmation dialog
                                    result = confirmation_dialog.exec_()

                                    if result == QMessageBox.Yes:
                                        self.repair_file()

            else:
                if filename.endswith('.mpt'):
                    with open(filename, 'r') as f:
                        data = json.load(f)

                        self.scene.template_manager.deserialize_items(data)

                elif filename.endswith('.mp'):
                    self.scene.undo_stack.clear()
                    self.scene.clear()

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserializer.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                        self.scene.setHasChanges(False)

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def repair_file(self):
        self.w = FileDataRepairer(self.scene.parentWindow, filename=self.filename)
