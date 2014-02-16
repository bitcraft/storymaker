__author__ = 'Leif'

def test():
    class DummyAction(Action):
        pass

    class Ability0(Ability):
        def get_contexts(self, caller, memory=None):
            prereqs = [PreceptGoal(DatumPrecept(caller, "action1", True))]
            effects = [PreceptGoal(DatumPrecept(caller, "action0", True))]
            action = DummyAction()
            context = ActionContext(caller, action, prereqs, effects)
            yield context

    class Ability1(Ability):
        def get_contexts(self, caller, memory=None):
            effects = [PreceptGoal(DatumPrecept(caller, "action1", True))]
            action = DummyAction()
            context = ActionContext(caller, action, None, effects)
            yield context

    class Ability2(Ability):
        def get_contexts(self, caller, memory=None):
            effects = [PreceptGoal(DatumPrecept(caller, "action2", True))]
            action = DummyAction()
            context = ActionContext(caller, action, None, effects)
            yield context

    class Ability3(Ability):
        def get_contexts(self, caller, memory=None):
            prereqs = [PreceptGoal(DatumPrecept(caller, "action0", True)),
                       PreceptGoal(DatumPrecept(caller, "action2", True))]
            effects = [PreceptGoal(DatumPrecept(caller, "action3", True))]
            action = DummyAction()
            context = ActionContext(caller, action, None, effects)
            yield context

    agent = GoapAgent()
    agent.abilities.add(Ability0())
    agent.abilities.add(Ability1())
    agent.abilities.add(Ability2())
    agent.abilities.add(Ability3())

    goal0 = PreceptGoal(DatumPrecept(agent, "action3", True))
    agent.goals.add(goal0)

    goal1 = PreceptGoal(DatumPrecept(agent, "action1", True))
    agent.goals.add(goal1)

    agent.find_plan()


if __name__ == '__main__':
    from pygoap.actions import *
    from pygoap.goals import *
    import timeit

    # 36.641830583586376 initial benchmark
    # 36.063973993301175
    # 35.40025543824159
    # 35.84698477870948 # added pushback and heap checking
    print(min(timeit.repeat("test()", number=10000, setup="from __main__ import test")))
