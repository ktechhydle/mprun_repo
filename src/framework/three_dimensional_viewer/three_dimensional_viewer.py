import os.path
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from src.framework.items import *
from src.framework.three_dimensional_viewer.three_dimensional_item import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# FPS tracking
frame_count = 0
start_time = time.time()


class SceneTo3DView(QOpenGLWidget):

    def __init__(self, scene: QGraphicsScene, parent):
        super().__init__(parent)
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowTitle('3D Viewer')
        self.setWindowFlag(Qt.Tool)
        self.resize(600, 600)

        self.setLayout(QVBoxLayout())
        self.createUI()

        self.scene = scene
        self.scene.changed.connect(self.update)
        self.parent = parent

        # Variables for camera control
        self.zoom = -50.0  # Initial zoom distance
        self.yaw = 0.0  # Left/right rotation (horizontal)
        self.pitch = 0.0  # Up/down rotation (vertical)
        self.last_mouse_pos = None  # Track mouse position for dragging

        # Variables for panning
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.panning = False

    def createUI(self):
        navigation_label = QLabel('Left Click to Orbit\n'
                                  'Shift + Left Click to Pan')
        navigation_label.setStyleSheet('color: black')
        self.fps_label = QLabel('FPS: ')
        self.fps_label.setStyleSheet('color: black')

        self.layout().addWidget(navigation_label)
        self.layout().addWidget(self.fps_label)
        self.layout().addStretch()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        r, g, b = hexToRGB("#ffffff")
        glClearColor(r, g, b, 1.0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, width / height, 0.5, 10000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        Renders the scene in a loop
        """
        global frame_count, start_time
        frame_count += 1

        # Calculate FPS every second
        if time.time() - start_time >= 1.0:
            fps = frame_count / (time.time() - start_time)
            self.fps_label.setText(f'FPS: {int(fps)}')
            # Reset for the next second
            frame_count = 0
            start_time = time.time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply pan offsets
        glTranslatef(self.pan_x, -self.pan_y, self.zoom)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)

        # Render the scene
        self.renderScene()

    def addItem(self, item: Item):
        """
        Adds the item to the scene
        """
        item.draw()

    def renderScene(self):
        """
        Renders the initial plane, and figures out what is available to draw next
        """
        glPushMatrix()

        glRotatef(90, 1, 0, 0)

        item = CubeItem([64000, 64000, 10])
        item.setColor('#ebe4ec')
        self.addItem(item)

        glPopMatrix()

        for graphics_scene_item in self.scene.items():
            self.renderItem(graphics_scene_item)

    def renderItem(self, item: QGraphicsItem):
        """
        Renders a specific item based on the type of QGraphicsItem
        """
        if isinstance(item, CustomSvgItem):
            obj_file_path = ''

            if os.path.basename(item.source()).lower().startswith('jump'):
                obj_file_path = 'course elements/3d/jump.obj'

            elif os.path.basename(item.source()).lower().endswith('halfpipe.svg'):
                obj_file_path = 'course elements/3d/halfpipe.obj'

            elif os.path.basename(item.source()).lower().startswith('tree'):
                if not hasattr(item, 'obj_file_path'):
                    choices = ['course elements/3d/tree.obj', 'course elements/3d/tree_smaller.obj']
                    item.obj_file_path = random.choice(choices)  # Store the choice
                obj_file_path = item.obj_file_path

            if obj_file_path != '':
                glPushMatrix()
                glRotatef(270, 1, 0, 0)

                obj_item = ObjItem(obj_file_path)
                obj_item.setColor('#ebe4ec')  # snow color
                obj_item.setPosition(
                    [item.sceneBoundingRect().center().x() - 90, -item.sceneBoundingRect().center().y() - 90, 0])
                obj_item.setScale([item.scale(), item.scale(), item.scale()])
                obj_item.setRotation(item.rotation(), [0, 0, 1])
                obj_item.setOutlineEnabled(True)
                self.addItem(obj_item)

                glPopMatrix()

        # Continue processing other items if they're not CustomSvgItem
        if not isinstance(item, CustomSvgItem):
            self.renderOtherItem(item)

    def renderOtherItem(self, item: QGraphicsItem):
        # Specific item rendering will go here
        pass

    def wheelEvent(self, event):
        """
        Controls zooming in and out
        """
        delta = event.angleDelta().y() / 120  # 120 units per wheel notch
        self.zoom += delta * 25.0  # Adjust zoom speed by changing multiplier
        self.zoom = max(self.zoom, -10000.0)  # Limit zoom out to -1000.0
        self.update()  # Request a repaint

    def mousePressEvent(self, event):
        """
        Handles initial mouse press event
        """
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
        if event.modifiers() & Qt.ShiftModifier:  # Check if Shift key is pressed
            self.panning = True  # Start panning

    def mouseMoveEvent(self, event):
        """
        Handles panning and orbiting
        """
        if self.panning and self.last_mouse_pos is not None:
            # Calculate the mouse movement delta
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # Update pan offsets
            self.pan_x += dx * 2
            self.pan_y += dy * 2

            # Save the new mouse position
            self.last_mouse_pos = event.pos()

            # Request a repaint
            self.update()
        elif self.last_mouse_pos is not None:
            # Existing code for rotation
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            self.yaw += dx * 0.3
            self.pitch -= dy * 0.3

            self.pitch = max(-89, min(89, self.pitch))

            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Handles variable cleanup
        """
        if event.button() == Qt.LeftButton:
            if self.panning:
                self.panning = False  # Stop panning
            self.last_mouse_pos = None
