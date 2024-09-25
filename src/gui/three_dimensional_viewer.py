from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from src.framework.items import *


class SceneTo3DView(QOpenGLWidget):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowTitle('3D Viewer')
        self.setWindowModality(Qt.ApplicationModal)

        self.scene = scene

        # Variables for camera control
        self.zoom = -50.0  # Initial zoom distance
        self.yaw = 0.0     # Left/right rotation (horizontal)
        self.pitch = 0.0   # Up/down rotation (vertical)
        self.last_mouse_pos = None  # Track mouse position for dragging

        # Variables for panning
        self.pan_x = 0.0  # Horizontal pan
        self.pan_y = 0.0  # Vertical pan
        self.panning = False  # Panning state

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 1.0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply camera transformations
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)  # Rotate pitch (up/down)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)    # Rotate yaw (left/right)

        self.renderScene()

    def renderScene(self):
        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                x, y = item.pos().x(), item.pos().y()
                width = item.boundingRect().width()
                length = item.boundingRect().height()  # Base length
                height = 20  # Cube's fixed height (lying flat)

                # Define the 8 vertices of the cube (lying flat)
                vertices = [
                    (x, y, 0), (x + width, y, 0), (x + width, y, length), (x, y, length),  # Bottom face
                    (x, y + height, 0), (x + width, y + height, 0), (x + width, y + height, length),
                    (x, y + height, length)  # Top face
                ]

                # --- Draw the solid cube ---
                glBegin(GL_QUADS)
                # Bottom face
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

                # Reset color to default after outline
                glColor3f(1.0, 1.0, 1.0)

    def wheelEvent(self, event):
        # Zoom in or out based on the wheel movement
        delta = event.angleDelta().y() / 120  # 120 units per wheel notch
        self.zoom += delta * 25.0  # Adjust zoom speed by changing multiplier
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
            self.yaw += dx * 0.5  # Adjust rotation speed with the multiplier
            self.pitch -= dy * 0.5  # Invert pitch for natural control

            # Limit pitch to prevent flipping over
            # self.pitch = max(-90, min(90, self.pitch))

            # Save the new mouse position
            self.last_mouse_pos = event.pos()

            # Request a repaint
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None


