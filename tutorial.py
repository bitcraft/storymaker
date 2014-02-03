from pygoap.actions import *
from pygoap.goals import *

from pygoap.agent import GoapAgent
from pygoap.environment import Environment

logging.basicConfig(level=logging.DEBUG)

"""
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
"""
"""
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

"""


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.__next__()
        return cr
    return start


@coroutine
def print_action(caller):
    try:
        td = (yield)
        print("hello! I'm {}.".format(caller.name))
    except GeneratorExit:
        pass

#generator
def print_context(caller, memory):
    effects = [SimpleGoal(introduced_self=True)]
    action = print_action(caller)
    yield action, effects


class Human:
    """
    actor that has the following human traits:
        emotion
        identity
        desire
        breeding
        is sexed (male / female)
    """

    name = "Pathetic Human"

    def birth(self):
        pass


class RandomStory:
    def __init__(self):
        self.init()

    def build_environment(self):
        return Environment()

    def build_actor(self):
        friendly_goal = SimpleGoal(introduced_self=True)

        a = GoapAgent()
        a.add_context(print_context)
        a.add_goal(friendly_goal)
        return a

    def init(self):
        self.env = self.build_environment()
        for i in range(4):
            a = self.build_actor()
            self.env.add(a)

    def tell(self):
        self.env.update(1)
        self.env.update(1)
        self.env.update(1)
        self.env.update(1)
        self.env.update(1)


s = RandomStory()
s.tell()
