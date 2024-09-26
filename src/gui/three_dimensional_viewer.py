import os.path
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from src.framework.items import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


def hexToRGB(hex_code):
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return r, g, b


def resetToWhite():
    r, g, b = hexToRGB('#ffffff')
    glColor3f(r, g, b)


def resetToSnowWhite():
    r, g, b = hexToRGB('#ebe4ec')
    glColor3f(r, g, b)


def resetToTestColor():
    r, g, b = hexToRGB('#00ff00')
    glColor3f(r, g, b)


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
        r, g, b = hexToRGB("#ffffff")
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
        width = 64000
        length = 64000
        height = 10  # Cube's fixed height

        glPushMatrix()

        # Translate the cube to be centered at the origin (0, 0)
        glTranslatef(0, 0, 0)
        glRotatef(90, 1, 0, 0)

        resetToSnowWhite()

        # Define the 8 vertices of the cube
        vertices = [
            (-width / 2, -length / 2, 0), (width / 2, -length / 2, 0), (width / 2, length / 2, 0),
            (-width / 2, length / 2, 0),
            (-width / 2, -length / 2, height), (width / 2, -length / 2, height), (width / 2, length / 2, height),
            (-width / 2, length / 2, height)
        ]

        # --- Draw the solid cube ---
        glBegin(GL_QUADS)
        # ... (the rest of your drawing code remains unchanged)

        # Bottom face (now on x-y plane, height along z)
        glVertex3f(*vertices[0])
        glVertex3f(*vertices[1])
        glVertex3f(*vertices[2])
        glVertex3f(*vertices[3])

        # Top face
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

        glPopMatrix()

        for graphics_scene_item in self.scene.items():
            self.renderItem(graphics_scene_item)

    def renderItem(self, item: QGraphicsItem):
        glPushMatrix()  # Push a new matrix to handle transformations

        if isinstance(item, CustomSvgItem):
            if os.path.basename(item.source()).lower().startswith('jump'):
                obj_file_path = 'course elements/jump.obj'
                resetToTestColor()

            elif os.path.basename(item.source()).lower().startswith('tree'):
                obj_file_path = 'course elements/tree.obj'
                resetToSnowWhite()

            else:
                obj_file_path = 'course elements/tree.obj'

            vertices, faces, materials = self.loadOBJFile(obj_file_path)  # Load OBJ with materials

            glRotatef(270, 1, 0, 0)
            glTranslatef(item.sceneBoundingRect().center().x() - 90, -item.sceneBoundingRect().center().y() - 90, 0)

            # Render the object with colors
            glBegin(GL_TRIANGLES)
            for face, material_name in faces:
                if material_name and material_name in materials:
                    color = materials[material_name].get('Kd', (1.0, 1.0, 1.0))  # Default to white if no color
                    glColor3fv(color)
                for vertex in face:
                    glVertex3f(*vertices[vertex])
            glEnd()

        # Pop matrix to ensure OpenGL transformations are reset
        glPopMatrix()

        # Continue processing other items if they're not CustomSvgItem
        if not isinstance(item, CustomSvgItem):
            self.renderOtherItem(item)

    def renderOtherItem(self, item: QGraphicsItem):
        glPushMatrix()

        if not isinstance(item, (CanvasItem, CanvasTextItem)):
            # Check if the item already has a stored obj_file_path
            if not hasattr(item, 'obj_file_path'):
                choices = ['course elements/tree.obj', 'course elements/tree_smaller.obj']
                item.obj_file_path = random.choice(choices)  # Store the choice

            # Use the stored obj_file_path
            vertices, faces, materials = self.loadOBJFile(item.obj_file_path)  # Load OBJ with materials

            glRotatef(270, 1, 0, 0)
            glTranslatef(item.sceneBoundingRect().center().x() - 90, -item.sceneBoundingRect().center().y() - 90, 0)

            # Render the object with colors
            glBegin(GL_TRIANGLES)
            for face, material_name in faces:
                if material_name and material_name in materials:
                    color = materials[material_name].get('Kd', (1.0, 1.0, 1.0))  # Default to white if no color
                    glColor3fv(color)
                for vertex in face:
                    glVertex3f(*vertices[vertex])
            glEnd()

        glPopMatrix()

    def loadOBJFile(self, file_path):
        vertices = []
        faces = []
        materials = {}
        current_material = None

        with open(file_path, 'r') as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue

                if parts[0] == 'v':
                    # Parse vertex
                    vertex = tuple(map(float, parts[1:4]))  # x, y, z
                    vertices.append(vertex)

                elif parts[0] == 'f':
                    # Parse face
                    face = [int(p.split('/')[0]) - 1 for p in parts[1:]]  # Get vertex indices
                    faces.append((face, current_material))

                elif parts[0] == 'mtllib':
                    # Load material file
                    material_file = parts[1]
                    materials = self.loadMTLFile(material_file)

                elif parts[0] == 'usemtl':
                    # Set current material for upcoming faces
                    current_material = parts[1]

        return vertices, faces, materials

    def loadMTLFile(self, file_path):
        materials = {}
        current_material = None

        with open(f'course elements/{file_path}', 'r') as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue

                if parts[0] == 'newmtl':
                    # Start a new material
                    current_material = parts[1]
                    materials[current_material] = {'Kd': (1.0, 1.0, 1.0)}  # Default to white

                elif parts[0] == 'Kd':
                    # Diffuse color (R, G, B)
                    kd = tuple(map(float, parts[1:4]))
                    materials[current_material]['Kd'] = kd

        return materials

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
