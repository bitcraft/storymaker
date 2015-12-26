from functools import partial
from collections import defaultdict

from pygoap.actions import Action
from pygoap.goals import *
from pygoap.precepts import *
from storymaker.english import make_english


def get_known_agents(agent):
    """get all known entities at this point
    do by checking for "name" DatumPrecepts
    """
    for p in agent.memory:
        try:
            if p.entity is not agent:
                yield p.entity
        except AttributeError:
            continue


def opposite_sex(agent, other):
    return not agent.sex == other.sex


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
        f = partial(opposite_sex, parent)
        for other in filter(f, get_known_agents(parent)):
            effects = [PreceptGoal(ActionPrecept(parent, "sex", other)),
                       PreceptGoal(DatumPrecept(parent, "had sex", True))]
            yield CopulateAction(parent, None, effects, other=other)


class CopulateAction(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.other = kwargs.get('other', None)
        assert (self.other is not None)

    def update(self, dt):
        yield ActionPrecept(self.parent, "sex", self.other)


class SpeakAbility(Action):
    """
    examine parent's memory and create some things to say
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.perception_map = defaultdict(list)

    def get_actions(self, parent, memory=None):
        import random

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
        super().__init__(*args, **kwargs)
        self.p = kwargs.get('precept', None)
        assert (self.p is not None)

    def update(self, dt):
        msg = SpeechPrecept(self.parent, make_english(self.parent, self.p))
        yield msg  # return a speech precept
        # return the original precept (simulates passing of info through speech)
        yield self.p


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
