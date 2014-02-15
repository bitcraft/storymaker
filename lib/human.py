__author__ = 'Leif'

from pygoap.agent import GoapAgent
from pygoap.actions import *
from pygoap.goals import *
from pygoap.precepts import *
from lib.english import make_english
from lib.society import *
from lib.traits import *
from collections import defaultdict
import random


def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start


# get all known entities at this point
# do this by checking for "name" DatumPrecepts
def get_known_agents(agent):
    for p in agent.memory.of_class(DatumPrecept):
        if p.name == "name":
            if p.entity is not agent:
                yield p.entity


def opposite_sex(agent, others):
    for other in others:
        if not agent.sex == other.sex:
            yield other


class AgeAbility(Ability):
    def get_contexts(self, caller, memory=None):
        effects = []
        prereqs = []
        action = AgeAction()
        context = ActionContext(caller, action, prereqs, effects)
        yield context


class AgeAction(Action):
    """
    simulate human aging
    """
    def __init__(self, *arg, **kwarg):
        super(AgeAction, self).__init__(*arg, **kwarg)
        self.age = 0

    def update(self, dt):
        self.age += dt


class GiveBirthAbility(Ability):
    """
    simulate birth
    """
    def get_contexts(self, caller, memory=None):
        effects = [PreceptGoal(DatumPrecept(caller, "has baby", True)),
                   PreceptGoal(DatumPrecept(caller, "ready to birth", False))]
        prereqs = [PreceptGoal(DatumPrecept(caller, "ready to birth", True))]
        action = GiveBirthAction()
        context = ActionContext(caller, action, prereqs, effects)
        yield context


class GiveBirthAction(Action):
    def update(self, dt):
        yield SpeechPrecept(self.context.caller, "my baby is here!")
        yield ActionPrecept(self.context.caller, "birth", None)


class GestationAbility(Ability):
    """
    simulate child gestation
    """
    def get_contexts(self, caller, memory=None):
        effects = [PreceptGoal(DatumPrecept(caller, "ready to birth", True))]
        prereqs = [PreceptGoal(DatumPrecept(caller, "had sex", True))]
        action = GestationAction()
        context = ActionContext(caller, action, prereqs, effects)
        yield context


class GestationAction(Action):
    default_duration = 5

    def update(self, dt):
        yield None


class CopulateAbility(Ability):
    """
    simulate sex
    """
    def get_contexts(self, caller, memory=None):
        for other in opposite_sex(caller, get_known_agents(caller)):
            if not other.sex == caller.sex:
                effects = [PreceptGoal(ActionPrecept(caller, "sex", other)),
                           PreceptGoal(DatumPrecept(caller, "had sex", True))]
                action = CopulateAction(other)
                context = ActionContext(caller, action, None, effects)
                yield context


class CopulateAction(Action):
    def __init__(self, other, *arg, **kwarg):
        super(CopulateAction, self).__init__(*arg, **kwarg)
        self.other = other

    def update(self, dt):
        yield ActionPrecept(self.context.caller, "sex", self.other)


class SpeakAbility(Ability):
    """
    examine caller's memory and create some things to say

    any agent who "hears" the action will have the precept added to their memory
    """
    # perception will be moved in to another class someday
    def __init__(self):
        super(SpeakAbility, self).__init__()
        self.perception_map = defaultdict(list)

    def get_contexts(self, caller, memory=None):
        if memory is not None:
            p = random.choice(list(memory))
            if p not in self.perception_map[caller]:
                effects = [PreceptGoal(DatumPrecept(caller, "chatter", True))]
                action = SpeakAction(p)

                # assume when speaking, all other actors will receive the message
                self.perception_map[caller].append(p)

                yield ActionContext(caller, action, None, effects)


class SpeakAction(Action):
    """
    communicate a precept
    """
    def __init__(self, p, *arg, **kwarg):
        super(SpeakAction, self).__init__(*arg, **kwarg)
        self.p = p
        self._sp = None

    def update(self, dt):
        if self._sp is None:
            msg = make_english(self.context.caller, self.p)
            self._sp = SpeechPrecept(self.context.caller, msg)
        yield self._sp  # return a speech precept
        yield self.p    # return a the original precept (simulates passing of information through speech)


class Preferences:
    """
    Preferences are a map that determines the effects actions have on behaviour
    """
    pass


# filters should modify the agent's traits or mood
def copulate_filter(agent, p):
    try:
        assert(isinstance(p, ActionPrecept))
        assert(p.entity is agent)
    except AssertionError:
        return [p]

    r = [p]

    value = 0

    to_remove = []
    for mp in agent.memory.of_class(MoodPrecept):
        if mp.entity is agent and mp.name == 'content':
            value += mp.value
            to_remove.append(mp)

    for mp in to_remove:
        agent.memory.remove(mp)

    if p.action == "sex":
        value += .01
        p = MoodPrecept(agent, 'content', value)
        r.append(p)

    return r


class Human(GoapAgent):
    mood_names = (
        "content",     # low values cause agent to seek another activity
        "hunger",      # negative requires food
        "rested",      # negative requires sleep
        "agitated",    # high values affect behaviour
        "stress",      # high values affect behaviour
        "overload",    # high values affect behaviour
    )

    population = 0

    def __init__(self, **kwarg):
        super(Human, self).__init__()
        self.traits = Traits()
        self.sex = kwarg.get("sex", 0)

        name = kwarg.get("name", None)
        if not name:
            name = "Pathetic Human {} ({})".format(Human.population, self.sex)
        self.name = name

        self.reset_moods()

        Human.population += 1

    def reset_moods(self):
        with self.planning_lock:
            for name in Human.mood_names:
                p = MoodPrecept(self, name, float())
                self.process(p)

    def reset(self):
        super(Human, self).reset()
        self.traits = Traits()
        self.sex = 0
        self.reset_moods()
        self.model()

    def model(self):
        self.model_abilities()
        self.model_goals()

    def model_abilities(self):
        """
        add abilities that are inherent to humans
        """
        if self.sex:
            self.abilities.add(GestationAbility())
            self.abilities.add(GiveBirthAbility())

        self.abilities.add(AgeAbility())
        self.abilities.add(SpeakAbility())
        self.abilities.add(CopulateAbility())

        self.filters.append(copulate_filter)

    def model_goals(self):
        """
        add goals that are inherent to humans
        """
        if self.sex:
            baby_goal = PreceptGoal(DatumPrecept(self, "has baby", True))
            self.goals.add(baby_goal)

        if self.traits.touchy > 0:
            copulate_goal = PreceptGoal(DatumPrecept(self, "had sex", True))
            self.goals.add(copulate_goal)

        if self.traits.chatty > 0:
            chatter_goal = PreceptGoal(DatumPrecept(self, "chatter", True))
            self.goals.add(chatter_goal)

    def birth(self):
        pass


def random_human():
    h = Human()
    h.sex = random.randint(0, 1)
    h.traits = Traits.random()
    h.model()
    return h