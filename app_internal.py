from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
import pickle
import sys
import os

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

user_data = []

user_data.append({
    'disclaimer_read': False,
    'tutorial_watched': False,
})

with open('Internal/user_data.mpdat', 'wb') as f:
    pickle.dump(user_data, f)
