from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


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

    def draw(self):
        glPushMatrix()
        super().draw()

        width = self.width
        length = self.length
        height = self.height

        vertices = [
            (-width / 2, -length / 2, 0), (width / 2, -length / 2, 0), (width / 2, length / 2, 0),
            (-width / 2, length / 2, 0),
            (-width / 2, -length / 2, height), (width / 2, -length / 2, height), (width / 2, length / 2, height),
            (-width / 2, length / 2, height)
        ]

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

        glPopMatrix()


class ObjItem(Item):
    def __init__(self, file: str):
        super().__init__()
        self.outline = False
        self.file = file
        self.vertices, self.faces, self.materials = self.loadOBJFile(self.file)  # Load the file only once

    def draw(self):
        glPushMatrix()
        super().draw()

        # Render the object with colors (solid rendering)
        glBegin(GL_TRIANGLES)
        for face, material_name in self.faces:
            if material_name and material_name in self.materials:
                color = self.materials[material_name].get('Kd', (1.0, 1.0, 1.0))  # Default to white if no color
                glColor3fv(color)
            for vertex in face:
                glVertex3f(*self.vertices[vertex])
        glEnd()

        if self.outlineEnabled():
            # Render outline (wireframe rendering)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # Switch to wireframe mode
            glColor3f(0, 0, 0)  # Set outline color to black
            glLineWidth(1.0)  # Set the width of the outline

            glBegin(GL_TRIANGLES)
            for face, material_name in self.faces:
                for vertex in face:
                    glVertex3f(*self.vertices[vertex])
            glEnd()

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Reset to solid mode

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



