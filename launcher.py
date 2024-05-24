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
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setGeometry(0, 0, 1200, 800)
        self.setObjectName('mainHomeScreen')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createHomeScreen()
        self.createHomeScreenUI()
        self.createHeader()

    def createHeader(self):
        # Home screen heading
        self.homeScreenHeader = QWidget(self)
        self.homeScreenHeader.setObjectName('homeScreenHeader')
        self.homeScreenHeader.setFixedHeight(100)

        self.homeScreenHeaderLayout = QHBoxLayout()
        self.homeScreenHeader.setLayout(self.homeScreenHeaderLayout)

        self.layout.addWidget(self.homeScreenHeader)

        # Home screen header widgets
        icon = QIconWidget('', 'logos and icons/MPRUN_logo_rounded_corners_version.png', 60, 60, self)

        # Add home screen header widgets
        self.homeScreenHeaderLayout.addWidget(icon)

    def createHomeScreen(self):
        self.homeScreen = QWidget(self)
        self.homeScreen.setObjectName('homeScreen')
        self.homeScreen.setFixedHeight(800)
        self.homeScreen.setFixedWidth(1200)

        self.layout.addWidget(self.homeScreen)

    def createHomeScreenUI(self):
        tabViewLayout = QVBoxLayout(self)
        tabViewLayout.addSpacing(100)

        create_new_btn = QPushButton('New File')

        tabViewLayout.addWidget(create_new_btn)

    def launchMPRUN(self):
        app = QApplication([])

        with open('main_style.css', 'r') as style:
            app.setStyleSheet(style.read())

        self.w = MPRUN()
        self.w.show()
        sys.exit(app.exec_())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.homeScreenHeader.setFixedWidth(self.width())
        self.homeScreen.setFixedWidth(self.width())
        self.homeScreen.setFixedHeight(self.height())




if __name__ == '__main__':
    win = QApplication([])

    with open('main_style.css', 'r') as style:
        win.setStyleSheet(style.read())

    app = Dialog()
    app.show()
    sys.exit(win.exec_())
