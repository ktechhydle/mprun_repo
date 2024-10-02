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
        self.outline_width_slider = QSlider()
        self.outline_width_slider.setFixedHeight(200)
        self.outline_width_slider.setOrientation(Qt.Orientation.Vertical)
        self.outline_width_slider.setRange(1, 10)
        self.outline_width_slider.setValue(3)
        self.outline_width_slider.valueChanged.connect(self.update)

        self.layout().addWidget(navigation_label)
        self.layout().addWidget(self.fps_label)
        self.layout().addWidget(self.outline_width_slider)
        self.layout().addStretch()

    def initializeGL(self):
        self._items = []
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
        self._items.append(item)

    def items(self):
        return self._items

    def renderScene(self):
        """
        Renders the initial plane, and figures out what is available to draw next
        """
        glPushMatrix()

        glRotatef(90, 1, 0, 0)

        # add initial plane
        item = PlaneItem([64000, 64000])
        item.setRotation(90, [1, 0, 0])
        item.setColor('#ebe4ec')
        self.addItem(item)

        # add axis indicator
        axis_item = AxisItem()
        self.addItem(axis_item)

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

            elif os.path.basename(item.source()).lower().startswith('short tube'):
                obj_file_path = 'course elements/3d/short_tube.obj'

            elif os.path.basename(item.source()).lower().startswith('long tube'):
                obj_file_path = 'course elements/3d/long_tube.obj'

            elif os.path.basename(item.source()).lower().startswith('xl tube'):
                obj_file_path = 'course elements/3d/xl_tube.obj'

            elif os.path.basename(item.source()).lower().startswith('xxl tube'):
                obj_file_path = 'course elements/3d/xxl_tube.obj'

            elif os.path.basename(item.source()).lower().startswith('short rail'):
                obj_file_path = 'course elements/3d/short_rail.obj'

            elif os.path.basename(item.source()).lower().startswith('tree'):
                if not hasattr(item, 'obj_file_path'):
                    choices = ['course elements/3d/tree.obj', 'course elements/3d/tree_smaller.obj']
                    item.obj_file_path = random.choice(choices)  # Store the choice
                obj_file_path = item.obj_file_path

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
