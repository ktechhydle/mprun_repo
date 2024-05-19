import customtkinter as ctk
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
import sys


class AboutWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('About MPRUN')
        self.setWindowIcon(QtGui.QIcon('logos and icons/MPRUN_icon.ico'))
        self.setFixedSize(500, 700)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.create_ui()

    def create_ui(self):
        # Create main layout
        layout = QtWidgets.QVBoxLayout()

        # App image and label
        mprun_img_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("logos and icons/MPRUN_logo_rounded_corners_version.png").scaled(80, 80,
                                                                                                QtCore.Qt.KeepAspectRatio)
        mprun_img_label.setPixmap(pixmap)
        mprun_img_label.move(20, 20)

        # Text label
        text = '''ABOUT:
        
MPRUN is a proof of concept that computer software can be useful for 
Snowboard and Ski Athletes to help plan competition runs, tricks, or even goals.

Development started in late January 2024, when athlete Keller Hydle realized the 
power of building apps. 

LICENCE:

This program is free software and is distributed under the GNU General Public License, version 3. In short, this means you are free to use and distribute Inkscape for any purpose, commercial or non-commercial, without any restrictions. You are also free to modify the program as you wish, with the only restriction that if you distribute the modified version, you must provide access to its source code.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. For more details about the license, check the LISCENSE.txt file included with this distribution.


FILES MADE USING MPRUN:

All files either saved or exported from MPRUN in any format (SVG, PNG, JPG, etc.) are owned by the creators of the work (that's you!) and/or the original authors in case you use derivative works. 

You are responsible for publishing your work under a license of your choosing and for tracking your use of derivative works in the software.
        '''
        label = QtWidgets.QLabel(text, self)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.move(20, 190)

        # Add widgets to layout
        layout.addWidget(mprun_img_label)
        layout.addWidget(label)

        # Set layout to the main window
        self.setLayout(layout)

class VersionWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('MPRUN Version')
        self.setWindowIcon(QtGui.QIcon('logos and icons/MPRUN_icon.ico'))
        self.setFixedSize(500, 300)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.create_ui()

    def create_ui(self):
        # Create main layout
        layout = QtWidgets.QVBoxLayout()

        # App image and label
        mprun_img_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("logos and icons/MPRUN_logo_rounded_corners_version.png").scaled(80, 80,
                                                                                                QtCore.Qt.KeepAspectRatio)
        mprun_img_label.setPixmap(pixmap)
        mprun_img_label.move(20, 20)

        # Text label
        text = '''
1.0.0

Copyright © K-TECH Industries 2024, All rights reserved.

If you encounter any issues or have suggestions for improvements, contact us at:
ktechindustries2019@gmail.com

Your input helps us make MPRUN even better.

Thank you for using MPRUN!
        '''
        label = QtWidgets.QLabel(text, self)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.move(20, 190)

        # Add widgets to layout
        layout.addWidget(mprun_img_label)
        layout.addWidget(label)

        # Set layout to the main window
        self.setLayout(layout)



if __name__ == '__main__':
    app = VersionWin()
    app.mainloop()
