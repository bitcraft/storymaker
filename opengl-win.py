import math

import pyglet
from pyglet.gl import *


def cube_vertices(x, y, z, n):
    """
    Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n,
        y + n, z - n, # top
        x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n,
        y - n, z + n, # bottom
        x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n,
        y + n, z - n, # left
        x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n,
        y + n, z + n, # right
        x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n,
        y + n, z + n, # front
        x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n,
        y + n, z - n, # back
    ]


class Window(pyglet.window.Window):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotation = (-90, -50)
        self.position = (20, 20, 5)

        self.env = env

        self.label = pyglet.text.Label('', font_name='Arial', font_size=10,
                                       x=10, y=self.height - 10,
                                       anchor_x='left', anchor_y='top',
                                       color=(255, 255, 255, 255))

        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def on_draw(self):
        self.clear()
        self.set_3d()
        batch = pyglet.graphics.Batch()
        for i, a in enumerate(self.env.agents):
            i += 1
            x, z = self.env.get_position(a)
            y = 0
            glColor3d(1.0 / i, 1.0, 1.0 / i)
            vertex_data = cube_vertices(x, y, z, 0.5)
            batch.add(24, GL_QUADS, None, ('v3f/static', vertex_data))
        batch.draw()
        self.set_2d()
        self.draw_debug()

    def on_resize(self, width, height):
        self.label.y = height - 10

    def draw_debug(self):
        x, y, z = self.position
        self.label.text = "{:.0f} ({:.2f}, {:.2f}, {:.2f})".format(
            pyglet.clock.get_fps(), x, y, z)
        self.label.draw()

    def set_3d(self):
        """
        Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def set_iso3d(self):
        """
        Configure OpenGL to draw in isometric 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10.0, 10.0, -10.0, 10.0, -10.0, 10.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(35.264, 1.0, 0.0, 0.0)
        glRotatef(-45.0, 0.0, 1.0, 0.0)
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def set_2d(self):
        """
        Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


def main():
    def update(dt):
        print(("== {:>8} {}".format(round(env.time, 2), "=" * 90)))

        env.update(dt)

        if env.time > 5:
            pass

        # hack to make the agents chatty
        chatty = 0
        if chatty:
            for a in env.agents:
                for i in [p for p in a.memory.of_class(DatumPrecept) if
                          p.name == 'chatter']:
                    a.memory.remove(i)

    env = build()
    win = Window(env, width=800, height=600, caption='Pyglet', resizable=True)
    pyglet.clock.schedule_interval(update, 1)
    pyglet.app.run()
    return win
