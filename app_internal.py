from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
import json
import sys
import os

default_text = """Run #:
Page #:
Competition:
Athlete:
Date:"""

data_use_disclaimer = '''This app collects user data, including...

Content You Read in App:
This app stores the content you read in app (like this dialog) so that you don't get popup after popup everytime you open the app. The content you read includes this dialog, the What's New Dialog, and the Tutorial Video Dialog.

Computer Info:
This app also stores the platform you are running for cross-platform differences.

Any data you are curious about can be found in the user_data.mpdat file included with this distribution.

Do you accept?'''

copyright_message = '''

Copyright (C) 2023-2024 MPRUN Document
<https://github.com/ktechhydle/mprun_repo> All Rights Reserved.

MPRUN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MPRUN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MPRUN. If not, see <http://www.gnu.org/licenses/>.

!DO NOT EDIT ANY INFORMATION FOUND IN THIS DOCUMENT!

'''

user_data = [{
    'disclaimer_read': False,
    'whatsnew_read': False,
    'tutorial_watched': False,
    'platform': sys.platform
}]

if os.path.exists('Internal/user_data.mpdat'):
    pass

else:
    with open('Internal/user_data.mpdat', 'w') as f:
        json.dump(user_data, f)

class DisclaimerWin(QMessageBox):
    def __init__(self, data_file, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Disclaimer')
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        self.data_file = data_file
        self.setText(data_use_disclaimer)
