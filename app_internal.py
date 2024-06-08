from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
import pickle

user_data = []

with open('Internal/user_data.mpdat', 'wb') as f:
    pickle.dump(user_data, f)