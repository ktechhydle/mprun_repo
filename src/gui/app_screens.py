from src.scripts.imports import *
from src.gui.custom_widgets import *
from src.scripts.app_internal import *
from PyQt5 import QtWidgets, QtGui, QtCore


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
        self.about_tab.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
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
        self.license_tab.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))

        # Create more info tab
        credits_label = QLinkLabel('Credits', 'https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit?usp=sharing')
        contact_label = QLinkLabel('Contact Us', 'mailto:ktechindustries2019@gmail.com')
        self.more_info_tab.layout().addWidget(credits_label)
        self.more_info_tab.layout().addWidget(contact_label)
        self.more_info_tab.layout().addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))

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
