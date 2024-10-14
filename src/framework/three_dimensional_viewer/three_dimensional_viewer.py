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
        self.target_x = 0.0  # The x coordinate of the orbit center
        self.target_y = 0.0  # The y coordinate of the orbit center
        self.target_z = 0.0  # The z coordinate of the orbit center
        self.camera_distance = 50.0  # Distance from the target

        # Variables for panning
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.panning = False

    def createUI(self):
        """
        Creates a simple set of QLabels in the top-left corner showing navigation tips
        """
        navigation_label = QLabel('Left Click to Orbit\n'
                                  'Shift + Left Click to Pan')
        navigation_label.setStyleSheet('color: black')
        self.fps_label = QLabel('FPS: ')
        self.fps_label.setStyleSheet('color: black')
        isometric_view_btn = QPushButton('Isometric View')
        isometric_view_btn.setFixedWidth(150)
        isometric_view_btn.clicked.connect(self.isometricView)
        self.outline_width_slider = QSlider()
        self.outline_width_slider.setFixedHeight(200)
        self.outline_width_slider.setOrientation(Qt.Orientation.Vertical)
        self.outline_width_slider.setRange(1, 10)
        self.outline_width_slider.setValue(3)
        self.outline_width_slider.valueChanged.connect(self.update)

        self.layout().addWidget(navigation_label)
        self.layout().addWidget(self.fps_label)
        self.layout().addWidget(isometric_view_btn)
        self.layout().addWidget(self.outline_width_slider)
        self.layout().addStretch()

    def initializeGL(self):
        self._items = []
        glEnable(GL_DEPTH_TEST)
        r, g, b = hexToRGB("#ffffff")
        glClearColor(r, g, b, 1.0)

        # Set up the initial camera position for isometric view
        self.isometricView()

    def isometricView(self):
        # Set camera distance and angles for isometric view
        self.yaw = 45.0  # Yaw angle for isometric view
        self.pitch = 45.0  # Pitch angle for isometric view

        self.update()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, width / height, 0.5, 64000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        A constant loop whenever the scene is rendered

        -Applies pan, zoom, orbit functions
        -Handles FPS counting
        -Creates the scene
        """
        global frame_count, start_time
        frame_count += 1

        # Calculate FPS every second
        if time.time() - start_time >= 1.0:
            fps = frame_count / (time.time() - start_time)
            self.fps_label.setText(f'FPS: {int(fps)}')
            frame_count = 0
            start_time = time.time()

        # Clear the depth buffer and apply a gradient background
        glClear(GL_DEPTH_BUFFER_BIT)

        # Draw gradient background
        self.drawGradientBackground()

        # Reset for 3D rendering
        glClear(GL_DEPTH_BUFFER_BIT)  # Clear the depth buffer to ensure 3D scene renders correctly
        glLoadIdentity()

        # Apply pan offsets
        glTranslatef(self.pan_x, -self.pan_y, self.zoom)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)

        # Render the scene
        self.renderScene()

    def drawGradientBackground(self):
        """
        Draws a full-screen quad with a gradient background.
        """
        glDisable(GL_DEPTH_TEST)  # Disable depth testing so the background isn't affected by 3D objects

        # Set up 2D orthographic projection to draw the background
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Start drawing the quad
        glBegin(GL_QUADS)

        # Set gradient colors (define color for each vertex)
        r, g, b = hexToRGB('#12a1dc')

        # Top-left
        glColor3f(r, g, b)
        glVertex2f(0, self.height())

        # Top-right
        glColor3f(r, g, b)
        glVertex2f(self.width(), self.height())

        r, g, b = hexToRGB('#ffffff')

        # Bottom-right
        glColor3f(r, g, b)
        glVertex2f(self.width(), 0)

        # Bottom-left
        glColor3f(r, g, b)
        glVertex2f(0, 0)

        glEnd()

        # Restore projection matrix and enable depth test again
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

    def addItem(self, item: Item):
        """
        Adds the item to the scene
        """
        item.draw()
        self._items.append(item)

    def items(self) -> list[Item]:
        return self._items

    def renderScene(self):
        """
        Renders the initial plane, and figures out what is available to draw next
        """
        glPushMatrix()

        glRotatef(90, 1, 0, 0)

        # add axis indicator
        axis_item = AxisItem()
        self.addItem(axis_item)

        if not hasattr(self, 'terrain_item'):
            self.terrain_item = ObjItem('course elements/3d/terrain.obj')
            self.terrain_item.setColor('#ebe4ec')
            self.terrain_item.setRotation(-90, [1, 0, 0])
            self.terrain_item.setScale([200, 200, 200])
            self.terrain_item.setOutlineEnabled(True)

        self.addItem(self.terrain_item)

        glPopMatrix()

        for graphics_scene_item in self.scene.items():
            self.renderItem(graphics_scene_item)

    def renderItem(self, item: QGraphicsItem):
        """
        Renders a specific item based on the type of QGraphicsItem
        """
        if isinstance(item, CustomSvgItem):
            basename = os.path.basename(item.source()).lower()

            # File path mappings for various item types
            path_map = {
                'jump': 'course elements/3d/jump.obj',
                'short tube': 'course elements/3d/short_tube.obj',
                'long tube': 'course elements/3d/long_tube.obj',
                'xl tube': 'course elements/3d/xl_tube.obj',
                'xxl tube': 'course elements/3d/xxl_tube.obj',
                'short rail': 'course elements/3d/short_rail.obj',
                'tree': ['course elements/3d/tree.obj', 'course elements/3d/tree_smaller.obj']
            }

            # Determine obj file path based on basename
            obj_file_path = ''
            if basename.startswith('jump'):
                obj_file_path = path_map['jump']
            elif basename.startswith('short tube'):
                obj_file_path = path_map['short tube']
            elif basename.startswith('long tube'):
                obj_file_path = path_map['long tube']
            elif basename.startswith('xl tube'):
                obj_file_path = path_map['xl tube']
            elif basename.startswith('xxl tube'):
                obj_file_path = path_map['xxl tube']
            elif basename.startswith('short rail'):
                obj_file_path = path_map['short rail']
            elif basename.startswith('tree'):
                if not hasattr(item, 'obj_file_path'):
                    item.obj_file_path = random.choice(path_map['tree'])
                obj_file_path = item.obj_file_path
            elif basename.endswith('halfpipe.svg'):
                obj_file_path = 'course elements/3d/halfpipe.obj'

            if obj_file_path != '':
                glPushMatrix()
                glRotatef(270, 1, 0, 0)

                # Cache ObjItem if not already cached
                if not hasattr(item, 'obj_item'):
                    item.obj_item = ObjItem(obj_file_path)
                    item.obj_item.setColor('#ebe4ec')  # snow color
                    item.obj_item.setOutlineEnabled(True)

                # Always update the ObjItem's transformation based on the current QGraphicsItem state
                item.obj_item.setPosition([item.sceneBoundingRect().center().x() - 90, -item.sceneBoundingRect().center().y() + 90, 0])
                item.obj_item.setScale([item.scale(), item.scale(), item.scale()])
                item.obj_item.setRotation(item.rotation(), [0, 0, 1])
                item.obj_item.setOutlineWidth(self.outline_width_slider.value())

                # Draw the cached ObjItem with updated transformations
                self.addItem(item.obj_item)

                glPopMatrix()

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
        Handles initial mouse press event coordinates
        """
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            if event.modifiers() & Qt.ShiftModifier:
                self.panning = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """
        Handles panning and orbiting
        """
        if self.panning and self.last_mouse_pos is not None and (event.modifiers() & Qt.ShiftModifier):
            # Calculate the mouse movement delta for panning
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # Update pan offsets
            self.pan_x += dx * 2
            self.pan_y += dy * 2

            # Save the new mouse position
            self.last_mouse_pos = event.pos()
            self.update()

        elif self.last_mouse_pos is not None:
            # Existing code for rotation
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            self.yaw += dx * 0.3
            self.pitch -= dy * 0.3

            self.pitch = max(-90, min(90, self.pitch))

            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Handles variable cleanup
        """
        if self.panning:
            self.panning = False  # Stop panning
        self.last_mouse_pos = None
        self.unsetCursor()

    def closeEvent(self, event):
        for item in self.scene.items():
            if isinstance(item, CustomSvgItem):

                # Clear any cached data
                if hasattr(item, 'obj_item'):
                    del item.obj_item

        event.accept()
