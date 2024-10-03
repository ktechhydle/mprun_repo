import requests
import webbrowser
from PyQt5.QtWidgets import QMessageBox


def get_latest_version(parent):
    url = 'https://raw.githubusercontent.com/ktechhydle/mprun_repo/main/internal data/_version.txt'
    try:
        # Set a timeout of 5 seconds
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.text.strip()  # Get the latest version from version.txt
        else:
            QMessageBox.warning(parent, 'Error', 'Unable to fetch the latest version.')
    except requests.exceptions.Timeout:
        QMessageBox.warning(parent, 'Error', 'The request timed out. Please check your internet connection.')
    except Exception as e:
        QMessageBox.warning(parent, 'Error', f'Failed to check for updates: {str(e)}')

    # Return the current version if fetching the latest one fails
    return parent.canvas.mpversion
