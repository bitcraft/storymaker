__author__ = 'Leif'

from pygoap.actions import Ability, ActionContext
from pygoap.agent import GoapAgent
from pygoap.goals import *
import random


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def hello_action(caller):
    try:
        td = (yield)
        print("Hello, I'm {}!".format(caller.name))
    except GeneratorExit:
        pass


class HelloAbility(Ability):
    def get_contexts(self, caller, memory=None):
        action = hello_action(caller)
        effects = [SimpleGoal(introduced_self=True)]
        context = ActionContext(self, caller, action, None, effects)
        yield context


@coroutine
def create_life_action(context, caller):
    ttl = 3
    try:
        while 1:
            td = (yield)
            if ttl <= 0:
                print('birth')
                break
            print('creating life...{}'.format(ttl))
            ttl -= td
    except GeneratorExit:
        pass


class CreateLifeAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(has_baby=True)]
        prereqs = [SimpleGoal(preggers=True)]
        action = create_life_action(self, caller)
        context = ActionContext(self, caller, action, prereqs, effects)
        yield context


@coroutine
def copulate_action(context, caller):
    try:
        td = (yield)
        print('just had sex!')
    except GeneratorExit:
        pass


class CopulateAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(preggers=True)]
        action = copulate_action(self, caller)
        context = ActionContext(self, caller, action, None, effects)
        yield context


class Human(GoapAgent):
    """
    actor that has the following human traits:
        emotion
        identity
        desire
        breeding
        is sexed (male / female)
    """

    def __init__(self):
        super(Human, self).__init__()
        self.name = "Pathetic Human"
        self.sex = 0
        self.friendly = 0
        self.sex_desire = 0

    def reset(self):
        self.sex = 0
        self.friendly = 0
        self.sex_desire = 0
        self.goals = []
        self.abilities = []
        self.plan = []

    def model(self):
        self.model_abilities()
        self.model_goals()

    def model_abilities(self):
        """
        add abilities that are inherent to humans
        """
        if self.sex:
            self.add_ability(CreateLifeAbility())

        if self.friendly > .25:
            self.add_ability(HelloAbility())
            self.add_ability(CopulateAbility())

    def model_goals(self):
        """
        add goals that are inherent to humans
        """

        if self.sex:
            preggers_goal = SimpleGoal(has_baby=True)
            self.add_goal(preggers_goal)

        if self.friendly > .25:
            friendly_goal = SimpleGoal(introduced_self=True)
            self.add_goal(friendly_goal)

        if self.sex_desire > .50:
            copulate_goal = SimpleGoal(had_sex=True)
            self.add_goal(copulate_goal)

    def birth(self):
        pass


def random_human():
    h = Human()
    h.sex = bool(random.randint(0, 1))
    h.friendly = random.random()
    h.sex_desire = random.random()
    h.model()
    return h