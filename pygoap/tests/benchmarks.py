__author__ = 'Leif'

from pygoap.agent import GoapAgent
from pygoap.actions import Action
from pygoap.goals import *


def test():
    class DummyAction(Action):
        pass

    class Action0(Action):
        domain = None

        def get_actions(self, caller, memory=None):
            prereqs = [PreceptGoal(DatumPrecept(caller, "action1", True))]
            effects = [PreceptGoal(DatumPrecept(caller, "action0", True))]
            action = DummyAction(caller, prereqs, effects)
            yield action

    class Action1(Action):
        domain = None

        def get_actions(self, caller, memory=None):
            effects = [PreceptGoal(DatumPrecept(caller, "action1", True))]
            action = DummyAction(caller, None, effects)
            yield action

    class Action2(Action):
        domain = None

        def get_actions(self, caller, memory=None):
            effects = [PreceptGoal(DatumPrecept(caller, "action2", True))]
            action = DummyAction(caller, None, effects)
            yield action

    class Action3(Action):
        domain = None

        def get_actions(self, caller, memory=None):
            prereqs = [PreceptGoal(DatumPrecept(caller, "action0", True)),
                       PreceptGoal(DatumPrecept(caller, "action2", True))]
            effects = [PreceptGoal(DatumPrecept(caller, "action3", True))]
            action = DummyAction(caller, prereqs, effects)
            yield action

    agent = GoapAgent()
    agent.abilities.add(Action0(agent))
    agent.abilities.add(Action1(agent))
    agent.abilities.add(Action2(agent))
    agent.abilities.add(Action3(agent))

    goal0 = PreceptGoal(DatumPrecept(agent, "action3", True))
    agent.goals.add(goal0)

    goal1 = PreceptGoal(DatumPrecept(agent, "action1", True))
    agent.goals.add(goal1)

    return agent.find_plan()


if __name__ == '__main__':
    import timeit

    # .58   initial // no action instanced
    # .61   action / operation change
    # .68   pretests

    print(test())
    print(min(timeit.repeat("test()", number=1000, repeat=10, setup="from __main__ import test")))
