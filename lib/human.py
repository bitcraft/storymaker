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
        effects = [SimpleGoal(has_baby=True), SimpleGoal(ready_to_birth=False)]
        prereqs = [SimpleGoal(ready_to_birth=True)]
        action = GiveBirthAction()
        context = ActionContext(caller, action, prereqs, effects)
        yield context


class GiveBirthAction(Action):
    def update(self, dt):
        return ActionPrecept(self.context.caller, "birth", None)


class GestationAbility(Ability):
    """
    simulate child gestation
    """
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(ready_to_birth=True)]
        prereqs = [SimpleGoal(had_sex=True)]
        action = GestationAction()
        context = ActionContext(caller, action, prereqs, effects)
        yield context


class GestationAction(Action):
    default_duration = 5

    def update(self, dt):
        pass


class CopulateAbility(Ability):
    """
    simulate sex

    TODO: make it with a partner!
    """
    def get_contexts(self, caller, memory=None):
        effects = [SimpleGoal(had_sex=True)]
        action = CopulateAction()
        context = ActionContext(caller, action, None, effects)
        yield context


class CopulateAction(Action):
    def update(self, dt):
        return ActionPrecept(self.context.caller, "sex", None)


class SpeakAbility(Ability):
    """
    examine caller's memory and create some things to say
    """

    # this will be moved in to another class someday
    def __init__(self):
        super(SpeakAbility, self).__init__()
        self.perception_map = defaultdict(list)

    def get_contexts_(self, caller, memory=None):
        if memory is not None:
            p = random.choice(list(memory))
            if p not in self.perception_map[caller]:
                effects = [SimpleGoal(chatter=True)]
                action = SpeakAction(self, caller, p)

                # assume when speaking, all other actors will receive the message
                self.perception_map[caller].append(p)

                yield ActionContext(caller, action, None, effects)

    def get_contexts(self, caller, memory=None):
        p = SpeechPrecept(caller, "context!!!{}".format(caller.name))
        effects = [SimpleGoal(chatter=True)]
        action = SpeakAction(p)
        yield ActionContext(caller, action, None, effects)


class SpeakAction(Action):
    def __init__(self, p, *arg, **kwarg):
        super(SpeakAction, self).__init__(*arg, **kwarg)
        self.p = p

    def update(self, dt):
        msg = '[{}]\t\t{}'.format(self.context.caller.name, make_english(self.context.caller, self.p))
        p = SpeechPrecept(self.context.caller, msg)
        return p


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
        return p

    r = [p]

    if p.action == "sex":
        value = .25
        p = MoodPrecept(agent, 'content', value)
        r.append(p)
        print(agent, value)

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
            self.add_ability(GestationAbility())
            self.add_ability(GiveBirthAbility())

        self.add_ability(AgeAbility())
        self.add_ability(SpeakAbility())
        self.add_ability(CopulateAbility())

        self.filters.append(copulate_filter)

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