import requests
import webbrowser
from PyQt5.QtWidgets import QMessageBox


def get_latest_version(parent):
    url = 'https://raw.githubusercontent.com/ktechhydle/mprun_repo/main/internal data/_version.txt'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()  # Get the latest version from version.txt
        else:
            QMessageBox.warning(parent, 'Error', 'Unable to fetch the latest version.')
    except Exception as e:
        QMessageBox.warning(parent, 'Error', f'Failed to check for updates: {str(e)}')

    return parent.canvas.mpversion