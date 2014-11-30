"""
story generator
===============

program generates stories and illustrates them with GIF's from imgur
gifs will have to be annotated for content and emotional style

storytelling is about picking points in time and conveying a meaning

it is not telling every single detail, ad nauseam.  the structure will be as
follows:

AI environment 'developing' the story

the 'storyteller' will choose points of the narrative to construct 'sketches'
that summarize the story, or to tell details that are important to the goals of
the story.

the power of the ai framework is that it will be used twice:
    1. to create the story
    2. to tell the story

the storyteller has goals that will be set at the start of execution.
as the events from the ai simulation (1) are created, the storyteller can
evaluate and choose specific events to report.

as a side project, interactive fiction can be created with this system.

it is the storyteller that checks the blackboard of each agent (omniscient
narrator) the storyteller has values assigned to particular datum on the
blackboard these datum are chosen by the programmer/designer to create
interesting *human* narratives days of our lives is a worthy inspiration for
these values
examples may include:
    love
    hate
    desire
    struggle
    conflict

the goal is to create interesting narratives for people.  society may have
different values:
asian values:
    family conflicts
    conflict on social norms
    acting out of class

religious values:
    sinful acts
    altruism
    broken character

these can be parsed from agent blackboards and individual actions can be chosen
that have significant ramifications to the storyteller's key roles.

the 'main' ai will have to create rich, complex interactions.  this means rich,
complex action planning.  a shortcut would be to only code interactions that are
necessary to the storyteller's predetermined goals.  then, more interactions can
be developed to create narratives that are deeper.

finally, the scope of this project is not beautiful written english.  it is
complex narratives. this will be accomplished:
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
humans are empathetical...if story contains information about lost plans,\
readers will know

exerpt from days of our lives:
Liz was married to Tony. Neither loved the other, and, indeed, Liz was in love
with Neil.  However, unknown to either Tony or Neil, Stephano, Tony’s father,
who wanted Liz to produce a grandson for him, threatened Liz that if she left
Tony, he would kill Neil. Liz told Neil that she did not love him, that she was
still in love with Tony, and that he should forget about her. Eventually, Neil
was convinced and he married Marie. Later, when Liz was finally free from Tony
(because Stephano had died), Neil was not free to marry her and their trouble
went on.
"""

import random

from lib.human import Human
from lib.traits import Traits
from pygoap.environment2d import Environment2D
from pygoap.goals import *


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
random_facts = [DatumPrecept(None, *i.split()) for i in
                random_facts.strip().split('\n')]


# attempt to model a complex relationship between actors.
# modeled after a soap opera, for ultimate drama
def build():
    env = Environment2D()

    liz = Human(name="liz", sex=1)
    liz.traits = Traits.random()
    liz.model()
    env.add(liz)
    env.set_position(liz, (0, 0))

    tony = Human(name="tony", sex=0)
    tony.traits = Traits.random()
    tony.model()
    env.add(tony)
    env.set_position(tony, (10, 10))

    neil = Human(name="neil", sex=0)
    neil.traits = Traits.random()
    neil.model()
    env.add(neil)
    env.set_position(neil, (10, 0))

    stephano = Human(name="stephano", sex=0)
    stephano.traits = Traits.random()
    stephano.model()
    env.add(stephano)
    env.set_position(stephano, (0, 10))

    marie = Human(name="marie", sex=1)
    marie.traits = Traits.random()
    marie.model()
    env.add(marie)
    env.set_position(marie, (5, 5))

    def goal(actor, key, value):
        return PreceptGoal(DatumPrecept(actor, key, value))

    # plant seeds of the simulation
    stephano.goals.add(goal(liz, "has baby", True))
    liz.goals.add(goal(liz, "married", neil))
    neil.goals.add(goal(neil, "married", liz))
    marie.goals.add(goal(marie, "married", neil))

    # inject environment state
    liz.process(DatumPrecept(liz, "married", tony))
    tony.process(DatumPrecept(tony, "married", liz))

    # add random facts to give them something to talk about
    infuse = 0
    if infuse:
        for a in env.agents:
            with a.planning_lock:
                for i in range(random.randint(5, 10)):
                    p = random.choice(random_facts)
                    a.process(p)

    return env


def main():
    import time

    env = build()

    for i in range(10):
        print("== {:>8} {}".format(round(env.time, 2), "=" * 90))
        env.update(1)
        time.sleep(1)


if __name__ == '__main__':
    main()
