from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
import pickle
import sys
import os

user_data = []

user_data.append({
    'platform': sys.platform,
})

with open('Internal/user_data.mpdat', 'wb') as f:
    pickle.dump(user_data, f)
