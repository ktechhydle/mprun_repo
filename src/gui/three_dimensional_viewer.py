import os.path

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from src.framework.items import *


def hexToRGB(hex_code):
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return r, g, b


def resetToWhite():
    glColor3f(1, 1, 1)


def resetToBlack():
    glColor3f(0, 0, 0)


class SceneTo3DView(QOpenGLWidget):

    def __init__(self, scene: QGraphicsScene, parent):
        super().__init__(None)
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowTitle('3D Viewer')
        self.setWindowModality(Qt.ApplicationModal)

        self.scene = scene
        self.parent = parent

        # Variables for camera control
        self.zoom = -50.0  # Initial zoom distance
        self.yaw = 0.0  # Left/right rotation (horizontal)
        self.pitch = 0.0  # Up/down rotation (vertical)
        self.last_mouse_pos = None  # Track mouse position for dragging

        # Variables for panning
        self.pan_x = 0.0  # Horizontal pan
        self.pan_y = 0.0  # Vertical pan
        self.panning = False  # Panning state

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        r, g, b = hexToRGB("#737373")
        glClearColor(r, g, b, 1.0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(120.0, width / height, 0.5, 1000.0)  # Adjusted FOV and near plane
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Ensure translations are normalized for camera positioning
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)  # Rotate pitch (up/down)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)  # Rotate yaw (left/right)

        # Render the scene
        self.renderScene()

    def renderScene(self):
        item = self.scene.selectedItems()[0]

        width = item.boundingRect().width()
        length = item.boundingRect().height()  # Base length
        height = 20  # Cube's fixed height (for thickness)

        # Calculate the offsets to center the plane
        x_offset = width / 2
        z_offset = length / 2

        # Define the 8 vertices of the cube (flat on the x-z plane)
        vertices = [
            (-x_offset, 0, -z_offset), (x_offset, 0, -z_offset), (x_offset, 0, z_offset), (-x_offset, 0, z_offset),
            # Bottom face (lying flat)
            (-x_offset, height, -z_offset), (x_offset, height, -z_offset), (x_offset, height, z_offset),
            (-x_offset, height, z_offset)  # Top face
        ]

        r, g, b = hexToRGB("#ffffff")
        glColor3f(r, g, b)

        # --- Draw the solid cube ---
        glBegin(GL_QUADS)
        # Bottom face (lying flat)
        glVertex3f(*vertices[0])
        glVertex3f(*vertices[1])
        glVertex3f(*vertices[2])
        glVertex3f(*vertices[3])

        # Top face (lying flat)
        glVertex3f(*vertices[4])
        glVertex3f(*vertices[5])
        glVertex3f(*vertices[6])
        glVertex3f(*vertices[7])

        # Front face
        glVertex3f(*vertices[0])
        glVertex3f(*vertices[1])
        glVertex3f(*vertices[5])
        glVertex3f(*vertices[4])

        # Back face
        glVertex3f(*vertices[2])
        glVertex3f(*vertices[3])
        glVertex3f(*vertices[7])
        glVertex3f(*vertices[6])

        # Left face
        glVertex3f(*vertices[0])
        glVertex3f(*vertices[3])
        glVertex3f(*vertices[7])
        glVertex3f(*vertices[4])

        # Right face
        glVertex3f(*vertices[1])
        glVertex3f(*vertices[2])
        glVertex3f(*vertices[6])
        glVertex3f(*vertices[5])
        glEnd()

        # --- Draw the cube outline ---
        glColor3f(0.0, 0.0, 0.0)  # Set color to black for the outline
        glLineWidth(2.0)  # Set line width

        glBegin(GL_LINES)
        # Bottom edges
        for start, end in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            glVertex3f(*vertices[start])
            glVertex3f(*vertices[end])

        # Top edges
        for start, end in [(4, 5), (5, 6), (6, 7), (7, 4)]:
            glVertex3f(*vertices[start])
            glVertex3f(*vertices[end])

        # Vertical edges (connecting top and bottom faces)
        for start, end in [(0, 4), (1, 5), (2, 6), (3, 7)]:
            glVertex3f(*vertices[start])
            glVertex3f(*vertices[end])
        glEnd()

        for colliding_item in item.collidingItems():
            if isinstance(colliding_item, CustomSvgItem):
                if os.path.basename(colliding_item.source()) in self.parent.libraries_tab.items():
                    print(colliding_item.source())
                    self.renderItem(colliding_item)

    def renderItem(self, item: CustomSvgItem):
        if os.path.basename(item.source()).lower().startswith('jump'):
            obj_file_path = 'course elements/test.obj'
            vertices, faces = self.loadOBJFile(obj_file_path)  # Load the OBJ file

            print(item.pos())

            glPushMatrix()  # Save the current matrix state
            glTranslatef(item.pos().x(), item.pos().y(), 0)  # Translate to the item's position

            r, g, b = hexToRGB("#00ff00")
            glColor3f(r, g, b)

            # Render the object as before
            glBegin(GL_TRIANGLES)
            for face in faces:
                for vertex in face:
                    glVertex3f(*vertices[vertex])
            glEnd()

            # Render the outline
            resetToBlack()
            glLineWidth(2.0)
            glBegin(GL_LINES)
            for face in faces:
                for i in range(len(face)):
                    v1 = vertices[face[i]]
                    v2 = vertices[face[(i + 1) % len(face)]]
                    glVertex3f(*v1)
                    glVertex3f(*v2)
            glEnd()

            resetToWhite()

            glPopMatrix()

    def loadOBJFile(self, file_path):
        vertices = []
        faces = []

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    # Parse vertex
                    parts = line.split()
                    vertex = tuple(map(float, parts[1:4]))  # x, y, z
                    vertices.append(vertex)
                elif line.startswith('f '):
                    # Parse face
                    parts = line.split()
                    face = [int(p.split('/')[0]) - 1 for p in parts[1:]]  # Get vertex indices
                    faces.append(face)

        return vertices, faces

    def wheelEvent(self, event):
        # Zoom in or out based on the wheel movement
        delta = event.angleDelta().y() / 120  # 120 units per wheel notch
        self.zoom += delta * 15.0  # Adjust zoom speed by changing multiplier
        self.zoom = max(self.zoom, -1000.0)  # Limit zoom out to -1000.0
        self.update()  # Request a repaint

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            # Calculate the mouse movement delta
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # Update yaw and pitch based on mouse movement
            self.yaw += dx * 0.3  # Adjust rotation speed for yaw
            self.pitch -= dy * 0.3  # Invert pitch and adjust speed

            # Limit pitch to prevent flipping over
            self.pitch = max(-89, min(89, self.pitch))  # Adjust pitch limits slightly

            # Save the new mouse position
            self.last_mouse_pos = event.pos()

            # Request a repaint
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
