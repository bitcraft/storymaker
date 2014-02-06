__author__ = 'Leif'

from pygoap.actions import *
from pygoap.agent import GoapAgent
from pygoap.goals import *
from pygoap.precepts import *
from lib.english import make_english
from collections import defaultdict
import random


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def age_action(context, caller):
    """
    Makes the caller older
    """

    age = 0
    try:
        while 1:
            now = (yield)
            age += td
    except GeneratorExit:
        pass


class AgeAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = []
        prereqs = []
        action = age_action(self, caller)
        context = ActionContext(self, caller, action, prereqs, effects)
        yield context


@coroutine
def give_birth_action(context, caller):
    """
    Make a new human child
    """

    try:
        now = (yield)
        p = ActionPrecept(caller, "birth", None)
        caller.environment.enqueue_precept(p)
    except GeneratorExit:
        pass


class GiveBirthAbility(Ability):
    """
    Make a new human child
    """

    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(has_baby=True), SimpleGoal(ready_to_birth=False)]
        prereqs = [SimpleGoal(ready_to_birth=True)]
        action = give_birth_action(self, caller)
        context = ActionContext(self, caller, action, prereqs, effects)
        yield context


@coroutine
def create_life_action(context, caller):
    last_time = None
    ttl = 5
    try:
        while 1:
            now = (yield)
            if last_time is None:
                last_time = now
            if now - last_time >= ttl:
                break
    except GeneratorExit:
        pass


class CreateLifeAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(ready_to_birth=True)]
        prereqs = [SimpleGoal(had_sex=True)]
        action = create_life_action(self, caller)
        context = ActionContext(self, caller, action, prereqs, effects)
        yield context


@coroutine
def copulate_action(context, caller):
    try:
        now = (yield)
        p = ActionPrecept(caller, "sex", None)
        caller.environment.enqueue_precept(p)
    except GeneratorExit:
        pass


class CopulateAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(had_sex=True)]
        action = copulate_action(self, caller)
        context = ActionContext(self, caller, action, None, effects)
        yield context


@coroutine
def speak_action(context, caller, p):
    try:
        now = (yield)
        print('[{}]\t\t{}'.format(caller.name, make_english(caller, p)))
    except GeneratorExit:
        pass


class SpeakAction(Action):
    """
    make a basic english sentence that describes a memory (precept)
    """

    def __init__(self, context, caller, p):
        super(SpeakAction, self).__init__(context, caller)
        self.p = p

    def update(self, dt):
        msg = '[{}]\t\t{}'.format(self.caller.name, make_english(self.caller, self.p))
        p = SpeechPrecept(self.caller, msg)
        self.finished = True
        return p


class ConverseAbility(Ability):
    """
    examine caller's memory and create some things to say
    """

    # this will be moved in to another class someday
    def __init__(self):
        super(ConverseAbility, self).__init__()
        self.perception_map = defaultdict(list)

    def get_contexts_(self, caller, memory=None):
        if memory is not None:
            p = random.choice(list(memory))
            if p not in self.perception_map[caller]:
                effects = [SimpleGoal(chatter=True)]
                action = speak_action(self, caller, p)

                # assume when speaking, all other actors will receive the message
                self.perception_map[caller].append(p)

                yield ActionContext(self, caller, action, None, effects)

    def get_contexts(self, caller, memory=None):
        p = SpeechPrecept(caller, "context!!!{}".format(caller.name))
        effects = [SimpleGoal(chatter=True)]
        action = SpeakAction(self, caller, p)
        yield ActionContext(self, caller, action, None, effects)


class Trait:
    def __init__(self, name, kind):
        self.name = name
        self.value = kind()

    def __eq__(self, other):
        return self.value == other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other


class Traits:
    """
    Traits are generally not modified, and goals should not normally be
    triggered by changes or the state of a trait.
    """
    default = [
        "strength",
        "perception",
        "endurance",
        "charisma",
        "intelligence",
        "agility",
        "luck",
        "chatty",
        "morality",
        "tradition",
        "alignment",
        "touchy",
        "esteem",
        "karma",
        "report"
    ]

    def __init__(self):
        self.__traits = {}
        for name in self.default:
            self.__traits[name] = Trait(name, float)

    def __getattr__(self, item):
        try:
            return self.__traits[item]
        except KeyError:
            raise AttributeError

    @classmethod
    def random(cls):
        t = cls()
        for key, value in t.__traits.items():
            t.__traits[key].value = random.random()
        return t


class Moods(Traits):
    """
    Moods are subject to constant change and should influence goals.
    """
    default = [
        "happy",       # negative is depression
        "hunger",      # negative requires food
        "rest",        # negative requires sleep
        "agitated",    # high values affect behaviour
        "stress"       # high values affect behaviour
    ]


class Preferences:
    """
    Preferences are a map that determines the effects actions have on behaviour
    """

    pass

class Human(GoapAgent):
    population = 0

    def __init__(self):
        super(Human, self).__init__()
        self.traits = Traits()
        self.moods = Moods()
        self.sex = 0
        self.name = "Pathetic Human {} ({})".format(Human.population, self.sex)
        Human.population += 1

    def reset(self):
        self.sex = 0
        self.traits = Traits()
        self.moods = Moods()
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
        self.name = "Pathetic Human {} ({})".format(Human.population, self.sex)
        if self.sex:
            pass
            #self.add_ability(CreateLifeAbility())
            #self.add_ability(GiveBirthAbility())

        #self.add_ability(AgeAbility())
        self.add_ability(ConverseAbility())
        #self.add_ability(CopulateAbility())

    def model_goals(self):
        """
        add goals that are inherent to humans
        """

        if self.sex:
            baby_goal = SimpleGoal(has_baby=True)
            self.add_goal(baby_goal)

        if self.traits.chatty > 0:
            chatter_goal = SimpleGoal(chatter=True)
            self.add_goal(chatter_goal)

        if self.traits.touchy > .50:
            copulate_goal = SimpleGoal(had_sex=True)
            self.add_goal(copulate_goal)

    def birth(self):
        pass


def random_human():
    h = Human()
    h.sex = random.randint(0, 1)
    h.traits = Traits.random()
    h.model()
    return h