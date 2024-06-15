# Import packages
import pickle
import math
import os.path
import vtracer
import webbrowser
import os
import numpy as np
import markdown
import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from PyQt5.Qt import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from scipy.interpolate import splprep, splev
from scipy.signal import savgol_filter
from skimage.measure import *
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

# Import custom packages
from src.framework.undo_commands import *
from src.framework.custom_classes import *
from src.scripts.app_screens import *
from src.scripts.styles import *
from src.scripts.app_internal import *
from src.gui.custom_widgets import *
from src.gui.libraries import *
from src.gui.custom_dialogs import *