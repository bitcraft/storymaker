"""
set of actions and functions related to human abilities
"""
from functools import partial
import asyncio

from pygoap.agent import GoapAgent


class Body:
    pass


class Organ:
    """
    heartlungs, mouth, eyes, ears
    """

    def __init__(self):
        self.age = 0

    def trigger_update(self):
        pass

    def start(self, body):
        pass


class HeartLungs(Organ):
    # if enough o2, schedule beat, raise body.alive
    min_rate = 20
    max_rate = 120

    def __init__(self):
        Organ.__init__(self)
        self.rate = 60
        self._handle = None

    def start(self, body):
        def trigger_update(body):
            loop = asyncio.get_event_loop()
            next_beat = self.rate / 60.0
            self._handle = loop.call_later(next_beat, self.beat, body)

        if self._handle is None:
            self.trigger_update = partial(trigger_update, body)
            self.trigger_update()

    def beat(self, body):
        self.trigger_update()
        body.bp += 1.0
        body.alive += 1.0
        body.oxygen += .5


class Mouth(Organ):
    # if alive and not talking/eating, schedule breath
    def tick(self, body, dt):
        pass


class Eye(Organ):
    # if alive, allow vision precepts
    def tick(self, body, dt):
        pass


class Ear(Organ):
    # if alive, allow sound precepts
    def tick(self, body, dt):
        pass


class Brain(Organ):
    def tick(self, body, dt):
        pass


"""
    "strength",      capacity for muscle to move
    "perception",    abilty to notice prepects
    "endurance",     capacity to move muscles
    "charisma",      ability to influence others
    "intelligence",  ???
    "agility",       ability to perform complex maneuvers
    "luck",          ???
    "chatty",        ???
    "moral",         follows societal expectations
    "tradition",     ???
    "alignment",     good/evil ???
    "esteem",        confidence that actions performed will succeed
    "report"         ???

    "strength",      capacity for muscle to move
    "perception",    abilty to notice prepects
    "endurance",     capacity to move muscles
    "charisma",      ability to influence others
    "intelligence",  ???
    "agility",       ability to perform complex maneuvers
    "luck",          ???
    "chatty",        ???
    "moral",         follows societal expectations
    "tradition",     ???
    "alignment",     good/evil ???
    "esteem",        confidence that actions performed will succeed
    "report"         ???

so, following a deterministic view of behaviour, a human can be reduced to a
collection of organs, a model of chemicals, and a memory.

think of goal planning as one action determining the next action by seeking
the nearest action in n-dimension space, where each action exists in a position
determined by the internal 'chemical' state of the agent

just as a thought experiment, one could use the ancient model of human behaviour
whereby every action taken is a result of the state of the person's 'humours'.
"""


class Human(GoapAgent):
    organs = [Brain, HeartLungs, Mouth, Eye, Ear]

    def __init__(self, *arg, **kwarg):
        super().__init__()
        body = Body()
        body.strength = 1.0
        body.oxygen = 1.0
        body.alive = 1.0
        body.energy = 1.0
        body.stress = 0.0
        body.age = 0.0
        body.will = 1.0
        body.temp = 0.5
        body.bp = .5
        body.metabolism = .5

        organs = {i.__name__.lower(): i() for i in self.organs}

        body.organs = organs
        self.body = body

    def start(self):
        for organ in list(self.body.organs.values()):
            organ.start(self.body)

    def model(self):
        """set the goals and abilities of the agent
        this method is going to be slow so it should only be called when needed
        """
        self.model_abilities()
        self.model_goals()

    def model_abilities(self):
        """
        add abilities that are relevant to the state of the body
        """
        pass

    def model_goals(self):
        """
        add goals that are relevant to the state of the body
        """
        pass
