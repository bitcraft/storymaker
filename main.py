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
"""

from lib.human import random_human, Human
from lib.traits import Traits
from pygoap.precepts import *
from pygoap.environment import Environment
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
random_facts = [DatumPrecept(None, *i.split()) for i in random_facts.strip().split('\n')[:2]]


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

        tony = Human(name="tony", sex=0)
        tony.traits = Traits.random()
        tony.model()
        self.env.add(tony)

        neil = Human(name="neil", sex=0)
        neil.traits = Traits.random()
        neil.model()
        self.env.add(neil)

        stephano = Human(name="stephano", sex=0)
        stephano.traits = Traits.random()
        stephano.model()
        self.env.add(stephano)

        marie = Human(name="marie", sex=1)
        marie.traits = Traits.random()
        marie.model()
        self.env.add(marie)

        # plant seeds of the simulation
        stephano.goals.add(PreceptGoal(DatumPrecept(liz, "has_baby", True)))

        liz.goals.add(PreceptGoal(DatumPrecept(liz, "married", neil)))
        neil.goals.add(PreceptGoal(DatumPrecept(neil, "married", liz)))

        marie.goals.add(PreceptGoal(DatumPrecept(marie, "married", neil)))

        with liz.planning_lock:
            liz.process(DatumPrecept(liz, "married", tony))

        with tony.planning_lock:
            tony.process(DatumPrecept(tony, "married", liz))

        # add random facts to give them something to talk about
        for a in self.env.agents:
            with a.planning_lock:
                for i in range(random.randint(5, 10)):
                    p = random.choice(random_facts)
                    a.process(p)

    def tell(self):
        for i in range(20):
            print("== {} {}".format(self.env.time, "=" * 100))

            self.env.update(1)

            chatty = 1
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
        return Environment()


if __name__ == '__main__':
    from lib.storyboard import *

    teller = Storyteller()
    s = RandomStory()
    s.tell()