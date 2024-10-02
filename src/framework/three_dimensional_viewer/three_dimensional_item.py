from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


def hexToRGB(hex_code):
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return r, g, b


class Item(object):
    def __init__(self):
        self.pos = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.rotation = [0, 0, 0, 0]
        self.color = [0, 0, 0]

    def setColor(self, hex_code: str):
        """
        Sets the color using a hex code, then converts it to R, G, B format
        """
        r, g, b = hexToRGB(hex_code)
        self.color = [r, g, b]

    def setScale(self, scale: list[float]):
        """
        Sets the scale via a list of [x amount, y amount, z amount]
        """
        self.scale = [scale[0], scale[1], scale[2]]

    def setRotation(self, rotation: float, axis: list[int]):
        """
        Sets the rotation via a list of [amount, use x, use y, use z]
        """
        self.rotation = [rotation, axis[0], axis[1], axis[2]]

    def setPosition(self, pos: list[float]):
        """
        Sets the position via a list of [x, y, z]
        """
        self.pos = pos

    def position(self):
        """
        Returns the x, y, z position of the item
        """
        return self.pos[0], self.pos[1], self.pos[2]

    def scalePercentage(self):
        """
        Returns the x, y, z scale percentages, e.g. 1, 1, 1 for 100% scale
        """
        return self.scale[0], self.scale[1], self.scale[2]

    def rotationDegrees(self):
        """
        Returns the rotation amount, x axis enabled, y axis enabled, z axis enabled
        """
        return self.rotation[0], self.rotation[1], self.rotation[2], self.rotation[3]

    def colorRgb(self):
        """
        Returns the color in R, G, B format
        """
        return self.color[0], self.color[1], self.color[2]

    def draw(self):
        """
        This method is left for the subclass to define
        """
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glScalef(self.scale[0], self.scale[1], self.scale[2])
        glRotatef(self.rotation[0], self.rotation[1], self.rotation[2], self.rotation[3])
        glColor3f(self.color[0], self.color[1], self.color[2])


class CubeItem(Item):
    def __init__(self, cube: list):
        super().__init__()
        self.width = cube[0]
        self.length = cube[1]
        self.height = cube[2]
        self.vbo = None
        self.setupVertexData()

    def setupVertexData(self):
        # Define vertices for the cube using NumPy
        width = self.width
        length = self.length
        height = self.height

        vertices = np.array([
            # Bottom face
            -width / 2, -length / 2, 0,
            width / 2, -length / 2, 0,
            width / 2, length / 2, 0,
            -width / 2, length / 2, 0,

            # Top face
            -width / 2, -length / 2, height,
            width / 2, -length / 2, height,
            width / 2, length / 2, height,
            -width / 2, length / 2, height
        ], dtype=np.float32)

        # Generate and bind the VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    def draw(self):
        glPushMatrix()
        super().draw()

        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # Define vertex pointer
        glVertexPointer(3, GL_FLOAT, 0, None)

        # Draw using the VBO
        glDrawArrays(GL_QUADS, 0, 8)

        glDisableClientState(GL_VERTEX_ARRAY)

        glPopMatrix()


class PlaneItem(Item):
    def __init__(self, rect: list):
        super().__init__()
        self.rect = rect
        self.vbo = None
        self.setupVertexData()

    def setupVertexData(self):
        # Define vertices for the plane
        width = self.rect[0]
        length = self.rect[1]

        vertices = np.array([
            [-width / 2, 0, -length / 2],  # Bottom left
            [width / 2, 0, -length / 2],  # Bottom right
            [width / 2, 0, length / 2],  # Top right
            [-width / 2, 0, length / 2]  # Top left
        ], dtype=np.float32)

        # Generate and bind the VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    def draw(self):
        glPushMatrix()
        super().draw()

        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # Define vertex pointer
        glVertexPointer(3, GL_FLOAT, 0, None)

        # Draw using the VBO
        glDrawArrays(GL_QUADS, 0, 8)

        glDisableClientState(GL_VERTEX_ARRAY)

        glPopMatrix()

    def setRect(self, rect: list):
        self.rect = rect


class ObjItem(Item):
    def __init__(self, file: str):
        super().__init__()
        self.outline = False
        self.file = file
        self.vertices, self.faces, self.materials = self.loadOBJFile(self.file)
        self.vertex_vbo = None
        self.index_vbo = None
        self.setupVertexData()

    def setupVertexData(self):
        # Convert vertex list to numpy array
        vertices_np = np.array(self.vertices, dtype=np.float32)

        # Flatten faces to create index array
        indices = [vertex for face, _ in self.faces for vertex in face]
        indices_np = np.array(indices, dtype=np.uint32)

        # Create VBO for vertices
        self.vertex_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices_np.nbytes, vertices_np, GL_STATIC_DRAW)

        # Create VBO for indices
        self.index_vbo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_vbo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_np.nbytes, indices_np, GL_STATIC_DRAW)

    def draw(self):
        glPushMatrix()
        super().draw()

        # Enable vertex array
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_vbo)

        # First Pass: Render the object normally
        offset = 0
        for face, material_name in self.faces:
            if material_name and material_name in self.materials:
                color = self.materials[material_name].get('Kd', (1.0, 1.0, 1.0))  # Default to white
                glColor3fv(color)

            face_vertex_count = len(face)
            glDrawElements(GL_TRIANGLES, face_vertex_count, GL_UNSIGNED_INT, ctypes.c_void_p(offset * 4))
            offset += face_vertex_count

        glDisableClientState(GL_VERTEX_ARRAY)

        # Enabling outline gives a hand drawn like appearance
        if self.outlineEnabled():
            # Second Pass: Render only the outline

            # Enable back-face culling to render only outer edges
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)  # Cull front faces to render the outline from back faces

            # Set outline color and width
            glLineWidth(3.0)
            r, g, b = hexToRGB('#aba4ab')
            glColor3f(r, g, b)

            # Enable wireframe mode
            glPolygonMode(GL_BACK, GL_LINE)

            # Slightly scale the object to create the outline effect
            glPushMatrix()
            glScalef(1.01, 1.01, 1.01)

            # Render the object again in wireframe mode to create the silhouette
            glEnableClientState(GL_VERTEX_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
            glVertexPointer(3, GL_FLOAT, 0, None)
            glDrawElements(GL_TRIANGLES, len(self.faces) * 3, GL_UNSIGNED_INT, None)

            glDisableClientState(GL_VERTEX_ARRAY)
            glPopMatrix()

            # Reset the polygon mode to fill
            glPolygonMode(GL_BACK, GL_FILL)
            glDisable(GL_CULL_FACE)  # Disable culling

        glPopMatrix()

    def setOutlineEnabled(self, enabled: bool):
        self.outline = enabled

    def outlineEnabled(self):
        return self.outline

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

        with open(f'course elements/3d/{file_path}', 'r') as file:
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


class AxisItem(Item):
    def __init__(self):
        super().__init__()
        self.lineWidth = 2.0

    def setLineWidth(self, width: float):
        self.lineWidth = width

    def draw(self):
        glPushMatrix()
        super().draw()
        glLineWidth(self.lineWidth)

        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(2.0, 2.0)

        # X-axis (Red)
        r, g, b = hexToRGB('#ff0000')  # set red
        glColor3f(r, g, b)
        glBegin(GL_LINES)
        glVertex3f(64000.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        # Draw negative X with stipple
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xAAAA)

        glBegin(GL_LINES)
        glVertex3f(-64000.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        glDisable(GL_LINE_STIPPLE)

        # Y-axis (Green)
        r, g, b = hexToRGB('#00ff00')  # set green
        glColor3f(r, g, b)
        glBegin(GL_LINES)
        glVertex3f(0.0, 64000.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        # Draw negative Y with stipple
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xAAAA)

        glBegin(GL_LINES)
        glVertex3f(0.0, -64000.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        glDisable(GL_LINE_STIPPLE)

        # Z-axis (Blue)
        r, g, b = hexToRGB('#0000ff')  # set blue
        glColor3f(r, g, b)
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, -64000.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        # Draw negative Y with stipple
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xAAAA)

        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, 64000.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        glDisable(GL_LINE_STIPPLE)

        glPopMatrix()