"""
set of actions and functions related to human abilities
"""
from collections import defaultdict

from pygoap.agent import GoapAgent
from pygoap.actions import Action
from pygoap.goals import *
from pygoap.precepts import *
from lib.english import make_english
from lib.traits import *


# get all known entities at this point
# do this by checking for "name" DatumPrecepts
def get_known_agents(agent):
    for p in agent.memory:
        try:
            if p.entity is not agent:
                yield p.entity
        except AttributeError:
            continue


def opposite_sex(agent, others):
    for other in others:
        if not agent.sex == other.sex:
            yield other


class AgeAbility(Action):
    def get_actions(self, parent, memory=None):
        effects = list()
        prereqs = list()
        action = AgeAction()
        context = ActionContext(parent, action, prereqs, effects)
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
        yield None


class GiveBirthAbility(Action):
    """
    simulate birth
    """

    def get_actions(self, parent, memory=None):
        effects = [PreceptGoal(DatumPrecept(parent, "has baby", True)),
                   PreceptGoal(DatumPrecept(parent, "ready to birth", False))]
        prereqs = [PreceptGoal(DatumPrecept(parent, "ready to birth", True))]
        yield GiveBirthAction(parent, prereqs, effects)


class GiveBirthAction(Action):
    def update(self, dt):
        yield SpeechPrecept(self.parent, "my baby is here!")
        yield ActionPrecept(self.parent, "birth", None)


class GestationAbility(Action):
    """
    simulate child gestation
    """

    def get_actions(self, parent, memory=None):
        effects = [PreceptGoal(DatumPrecept(parent, "ready to birth", True))]
        prereqs = [PreceptGoal(DatumPrecept(parent, "had sex", True))]
        yield GestationAction(parent, prereqs, effects)


class GestationAction(Action):
    default_duration = 5


class CopulateAbility(Action):
    """
    simulate sex
    """

    def get_actions(self, parent, memory=None):
        for other in opposite_sex(parent, get_known_agents(parent)):
            if not other.sex == parent.sex:
                effects = [PreceptGoal(ActionPrecept(parent, "sex", other)),
                           PreceptGoal(DatumPrecept(parent, "had sex", True))]
                yield CopulateAction(parent, None, effects, other=other)


class CopulateAction(Action):
    def __init__(self, *args, **kwargs):
        super(CopulateAction, self).__init__(*args, **kwargs)
        self.other = kwargs.get('other', None)
        assert (self.other is not None)

    def update(self, dt):
        yield ActionPrecept(self.parent, "sex", self.other)


class SpeakAbility(Action):
    """
    examine parent's memory and create some things to say
    """

    def __init__(self, *args, **kwargs):
        super(SpeakAbility, self).__init__(*args, **kwargs)
        self.perception_map = defaultdict(list)

    def get_actions(self, parent, memory=None):
        if memory is not None:
            if len(memory) == 0:
                raise StopIteration
            p = random.choice(list(memory))
            if p not in self.perception_map[parent]:
                # assume when speaking all actors will receive the message
                self.perception_map[parent].append(p)
                effects = [PreceptGoal(DatumPrecept(parent, "chatter", True))]
                yield SpeakAction(parent, None, effects, precept=p)


class SpeakAction(Action):
    def __init__(self, *args, **kwargs):
        super(SpeakAction, self).__init__(*args, **kwargs)
        self.p = kwargs.get('precept', None)
        assert (self.p is not None)

    def update(self, dt):
        msg = SpeechPrecept(self.parent, make_english(self.parent, self.p))
        yield msg  # return a speech precept
        # return the original precept (simulates passing of info through speech)
        yield self.p


class TeleSend(Action):
    """
    Telepathic Communication (a joke!)
    """

    def __init__(self, p, *arg, **kwarg):
        super(TeleSend, self).__init__(*arg, **kwarg)
        self.p = p

    def update(self, dt):
        yield self.p


class Preferences:
    """
    Preferences are a map that determines the effects actions have on behaviour
    """
    pass


# filters should modify the agent's traits or mood
def copulate_filter(agent, p):
    try:
        assert (isinstance(p, ActionPrecept))
        assert (p.entity is agent)
    except AssertionError:
        return [p]

    r = [p]

    value = 0

    to_remove = list()
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


def conversation_filter(agent, p):
    try:
        assert (isinstance(p, SpeechPrecept))
    except AssertionError:
        yield p
        raise StopIteration

    agent.moods.content.value -= .1
    if agent.moods.content.value < 0:
        agent.moods.content.value = 0.0

    yield p


class Moods(Traits):
    default = (
        "content",  # low values cause agent to seek another activity
        "hunger",  # negative requires food
        "rested",  # negative requires sleep
        "stressed",  # high values affect behaviour
    )


class Human(GoapAgent):
    population = 0

    def __init__(self, **kwarg):
        super(Human, self).__init__()
        self.traits = Traits()
        self.moods = None
        self.sex = kwarg.get("sex", 0)

        name = kwarg.get("name", None)
        if not name:
            name = "Pathetic Human #{:03d}".format(Human.population)
        self.name = name

        self.model_moods()

        Human.population += 1

    def model_moods(self):
        m = Moods()
        m.content.value = 1.0

        self.moods = m
        for name in self.moods:
            p = MoodPrecept(self, name, float())
            self.process(p)

    def reset(self):
        super(Human, self).reset()
        self.traits = Traits()
        self.sex = 0
        self.model()

    def model(self):
        self.model_moods()
        self.model_abilities()
        self.model_goals()

    def model_abilities(self):
        """
        add abilities that are inherent to humans
        """
        if self.sex:
            self.abilities.add(GestationAbility(self))
            self.abilities.add(GiveBirthAbility(self))

        # self.abilities.add(AgeAbility(self))
        self.abilities.add(SpeakAbility(self))
        self.abilities.add(CopulateAbility(self))

        self.filters.append(copulate_filter)
        self.filters.append(conversation_filter)

    def model_goals(self):
        """
        add goals that are inherent to humans
        """
        if self.sex:
            goal = PreceptGoal(DatumPrecept(self, "has baby", True),
                               name="baby")
            self.goals.add(goal)

        if self.traits.touchy > 0:
            goal = PreceptGoal(DatumPrecept(self, "had sex", True), name="sex")
            self.goals.add(goal)

        if self.traits.chatty > 0:
            goal = AVPreceptGoal(DatumPrecept(self, "chatter", True),
                                 name="chatty", weight=self.moods.content)
            # goal = WeightedGoal(weight=self.moods.content)
            self.goals.add(goal)

    def birth(self):
        pass


def random_human():
    h = Human()
    h.sex = random.randint(0, 1)
    h.traits = Traits.random()
    h.model()
    return h
