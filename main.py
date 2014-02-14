__author__ = 'Leif'

"""
story generator
===============

program generates stories and illustrates them with GIF's from imgur
gifs will have to be annotated for content and emotional style

storytelling is about picking points in time and conveying a meaning

it is not telling every single detail, ad nauseam.  the structure will be as follows:

AI environment 'developing' the story

the 'storyteller' will choose points of the narrative to construct 'sketches' that
summarize the story, or to tell details that are important to the goals of the story.

the power of the ai framework is that it will be used twice:
    1. to create the story
    2. to tell the story

the storyteller has goals that will be set at the start of execution.
as the events from the ai simulation (1) are created, the storyteller can evaluate
and choose specific events to report.

as a side project, interactive fiction can be created with this system.

it is the storyteller that checks the blackboard of each agent (omniscient narrator)
the storyteller has values assigned to particular datum on the blackboard
these datum are chosen by the programmer/designer to create interesting *human* narratives
days of our lives is a worthy inspiration for these values
examples may include:
    love
    hate
    desire
    struggle
    conflict

the goal is to create interesting narratives for people.  society may have different values:
asian values:
    family conflicts
    conflict on social norms
    acting out of class

religious values:
    sinful acts
    altruism
    broken character

these can be parsed from agent blackboards and individual actions can be chosen that have significant
ramifications to the storyteller's key roles.

the 'main' ai will have to create rich, complex interactions.  this means rich, complex action
planning.  a shortcut would be to only code interactions that are necessary to the storyteller's
predetermined goals.  then, more interactions can be developed to create narratives that are
deeper.

finally, the scope of this project is not beautiful written english.  it is complex narratives.
this will be accomplished:
    first through simple VO statements from the storyteller
    next addition of images with appropriate metadata
    finally, an artistic rendering of the image + narrative text

impression:
    the intense feelings toward another person whom you've only known in short moments
    the feelings that come about when learning that they have died 'before their time'
    it is a sadness in knowing that relationships with that person can never...never ever happen
    it is the ultimate loss for another person
    ...feeling the potential for a relationship and it being lost...outside of your control
    rip zhou min, ben...

loss of plans can create an emotional response
humans are empathetical...if story contains information about lost plans, readers will know

exerpt from days of our lives:
Liz was married to Tony. Neither loved the other, and, indeed, Liz was in love with Neil. 
However, unknown to either Tony or Neil, Stephano, Tony’s father, who wanted Liz to produce
a grandson for him, threatened Liz that if she left Tony, he would kill Neil. Liz told Neil
that she did not love him, that she was still in love with Tony, and that he should forget
about her. Eventually, Neil was convinced and he married Marie. Later, when Liz was finally
free from Tony (because Stephano had died), Neil was not free to marry her and their
trouble went on.

action builders = generators
action context = coroutine

ALSO, I'm learning pyglet and OPENGL here so....yeah it's gonna be messy.
"""

from lib.human import Human
from lib.traits import Traits
from pygoap.precepts import *
from pygoap.environment2d import Environment2D
from pygoap.goals import *
import random

#logging.basicConfig(level=logging.DEBUG)


random_facts = """
sky blue
grass green
home comfortable
dogs bark
cows moo
baby blue
sheep baa
fish swim
ice cold
fire hot
snakes bite
turtle slow
rabbit fast
coffee black
egg white
clouds rain
sun shines
flower bloom
beetles crawl
worms dig
birds chirp
cats claw
world mad
top spins
engineers build
thieves take
stranger danger
trees breathe
kittens play
covered skin
freedom free
rat race
bunny suit
dogs colorblind
boats sail
trains pull
parents raise
farmers grow
drunkards walk
walking spanish
"""
random_facts = [DatumPrecept(None, *i.split()) for i in random_facts.strip().split('\n')]


class RandomStory:
    def __init__(self):
        self.env = None
        self.init()

    def init(self):
        self.env = self.build_environment()

        liz = Human(name="liz", sex=1)
        liz.traits = Traits.random()
        liz.model()
        self.env.add(liz)
        self.env.set_position(liz, (0, 0))

        tony = Human(name="tony", sex=0)
        tony.traits = Traits.random()
        tony.model()
        self.env.add(tony)
        self.env.set_position(tony, (10, 10))

        neil = Human(name="neil", sex=0)
        neil.traits = Traits.random()
        neil.model()
        self.env.add(neil)
        self.env.set_position(neil, (10, 0))

        stephano = Human(name="stephano", sex=0)
        stephano.traits = Traits.random()
        stephano.model()
        self.env.add(stephano)
        self.env.set_position(stephano, (0, 10))

        marie = Human(name="marie", sex=1)
        marie.traits = Traits.random()
        marie.model()
        self.env.add(marie)
        self.env.set_position(marie, (5, 5))

        # plant seeds of the simulation
        stephano.goals.add(PreceptGoal(DatumPrecept(liz, "has baby", True)))

        liz.goals.add(PreceptGoal(DatumPrecept(liz, "married", neil)))
        neil.goals.add(PreceptGoal(DatumPrecept(neil, "married", liz)))

        marie.goals.add(PreceptGoal(DatumPrecept(marie, "married", neil)))

        with liz.planning_lock:
            liz.process(DatumPrecept(liz, "married", tony))

        with tony.planning_lock:
            tony.process(DatumPrecept(tony, "married", liz))

        # add random facts to give them something to talk about
        infuse = 0
        if infuse:
            for a in self.env.agents:
                with a.planning_lock:
                    for i in range(random.randint(5, 10)):
                        p = random.choice(random_facts)
                        a.process(p)

    def tell(self, dt):
        print("== {:>10} {}".format(round(self.env.time, 2), "=" * 90))

        self.env.update(dt)

        chatty = 0
        if chatty:
            # hack to make the agents chatty
            for a in self.env.agents:
                to_remove = []
                for p in a.memory:
                    try:
                        if p.name == "chatter":
                            to_remove.append(p)
                    except AttributeError:
                        pass

                for p in to_remove:
                    a.memory.remove(p)

    @staticmethod
    def build_environment():
        return Environment2D()


from lib.storyboard import *
import pyglet
import math
from pyglet.gl import *


def cube_vertices(x, y, z, n):
    """
    Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n, # top
        x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n, y - n, z + n, # bottom
        x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n, y + n, z - n, # left
        x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n, y + n, z + n, # right
        x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n, y + n, z + n, # front
        x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n, y + n, z - n, # back
    ]


class Window(pyglet.window.Window):
    def __init__(self, env, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.rotation = (-90, -50)
        self.position = (20, 20, 10)

        #self.position = (0,0,0)

        self.env = env

        self.label = pyglet.text.Label('', font_name='Arial', font_size=10,
                                       x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
                                       color=(255, 255, 255, 255))

        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, .01)

    def update(self, dt):
        x, y = self.rotation
        x += .01
        #y += .01
        self.rotation = (x, y)

        x, y, z = self.position
        z -= .001
        self.position = x, y, z

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
        batch = pyglet.graphics.Batch()
        for a in self.env.agents:
            x, z = self.env.get_position(a)
            y = 0
            label = pyglet.text.Label('ba', font_name='Arial', font_size=18,
                                      x=x * 10, y=z * 10, anchor_x='left', anchor_y='top', color=(255, 255, 255, 255),
                                      batch=batch)
        batch.draw()

        self.draw_debug()

        #glMatrixMode(GL_PROJECTION)
        #glPopMatrix()

    def on_resize(self, width, height):
        self.label.y = height - 10

    def draw_debug(self):
        x, y, z = self.position
        self.label.text = "{:.0f} ({:.2f}, {:.2f}, {:.2f})".format(pyglet.clock.get_fps(), x, y, z)
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
        Configure OpenGL to draw in 3d.
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
    s = RandomStory()
    win = Window(s.env, width=800, height=600, caption='Pyglet', resizable=True)

    teller = Storyteller()
    pyglet.clock.schedule_interval(s.tell, 1)
    pyglet.app.run()


if __name__ == '__main__':
    main()