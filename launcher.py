from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main import *
from custom_widgets import *
import webbrowser
import sys
import os

class Dialog(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('MPRUN - Home')

    def launch_mprun(self):
        app = QApplication([])

        with open('main_style.css', 'r') as style:
            app.setStyleSheet(style.read())

        self.w = MPRUN()
        self.w.show()
        sys.exit(app.exec_())




if __name__ == '__main__':
    win = QApplication([])
    app = Dialog()
    app.show()
    sys.exit(win.exec_())
