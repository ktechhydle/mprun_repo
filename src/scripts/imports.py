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