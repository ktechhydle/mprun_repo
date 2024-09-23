from src.scripts.imports import *
from src.framework.custom_classes import *
from src.scripts.app_internal import copyright_message


class FileDataRepairer:
    def __init__(self, parent: QMainWindow, filename=None):
        self.parent = parent
        self.filename = None

        if filename is None:
            file, _ = QFileDialog.getOpenFileName(parent, 'Choose File', '', 'MPRUN files (*.mp)')

            if file:
                self.filename = file
        else:
            self.filename = filename

        self.repair()

    def repair(self):
        if self.filename is not None:
            try:
                with open(self.filename, 'rb') as f:
                    data = self.repair_file(pickle.load(f))

                with open(self.filename, 'wb') as nf:
                    pickle.dump(data, nf)

            except Exception as e:
                print(f"Error loading file: {e}")

            QMessageBox.information(self.parent, 'Process Complete', 'File repair completed successfully.')

    def repair_file(self, serialized_data):
        is_valid, message = self.validate_serialized_data(serialized_data)
        if not is_valid:
            print(f'File is corrupted: {message}')
            self.repair_data(serialized_data)  # attempt to repair
        else:
            print('File is valid.')
        return serialized_data

    def repair_data(self, data):
        """If we update file serialization, we will add repair methods here to fix any errors"""
        pass

    def validate_serialized_data(self, data):
        required_fields = ['mpversion', 'item_count']
        for field in required_fields:
            if field not in data:
                return False, f'Missing field: {field}'

        if data['item_count'] != len(data) - 1:  # account for metadata
            return False, 'Item count mismatch'

        return True, 'Data is valid'
