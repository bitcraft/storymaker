"""
Goals in the context of a pyGOAP agent give the planner some direction when
planning.  Goals are known to the agent and are constantly monitored and
evaluated.  The agent will attempt to choose the most relevant goal for it's
state (determined by the blackboard) and then the planner will determine a
plan for the agent to follow that will (possibly) satisfy the chosen goal.

*** Goals, Effects, Prereqs and ActionBuilders are the same thing ***

test() should return a float from 0-1 on how successful the action would be
if carried out with the given state of the memory.

touch() should modify a memory in some meaningful way as if the action was
finished successfully.
"""

from pygoap.memory import MemoryManager
from pygoap.environment2d import distance
from pygoap.precepts import *
import logging

debug = logging.debug


class GoalBase:
    """
    Goals:
        can be relevant
        can be tested
        has a touch
    """
    def __init__(self, *args, **kwargs):
        try:
            self.condition = args[0]
        except IndexError:
            self.condition = None

        self.weight = 1.0
        self.args = args
        self.kw = kwargs

    def touch(self, memory):
        raise NotImplementedError

    def test(self, memory):
        raise NotImplementedError

    def get_relevancy(self, memory):
        """
        will return the "relevancy" value for this goal/prereq.
        """
        score = 1 - self.test(memory)
        return self.weight * score

    def self_test(self):
        """
        make sure the goal is sane
        """
        memory = MemoryManager()
        self.touch(memory)
        assert not self.test(memory) == 0

    def __repr__(self):
        try:
            return "<Goal: {}>".format(self.name)
        except AttributeError:
            return "<Goal: {}>".format(self.__class__.__name__)


class SimpleGoal(GoalBase):
    """
    Shorthand for creating simple DatumPrecept Goals
    """
    def test(self, memory):
        total = 0.0
        for precept in memory.of_class(DatumPrecept):
            for item in self.kw.items():
                if (precept.name, precept.value) == item:
                    total += 1
        return total / len(self.kw)

    def touch(self, memory):
        for item in self.kw.items():
            memory.add(DatumPrecept(self.args[0], *item))


class PreceptGoal(GoalBase):
    """
    Uses Precepts as a test
    """
    valid = (PositionPrecept, TimePrecept, DatumPrecept, ActionPrecept, SpeechPrecept, MoodPrecept)

    def __init__(self, *args, **kwargs):
        super(PreceptGoal, self).__init__(*args, **kwargs)
        assert (len(self.args) > 0)
        for a in self.args:
            assert (isinstance(a, PreceptGoal.valid))
        if kwargs.get("name", None):
            self.name = kwargs['name']

    def test(self, memory):
        total = 0.0
        for precept in self.args:
            if precept in memory:
                total += 1
        return total / len(self.args)

    def touch(self, memory):
        memory.update(self.args)


class EvalGoal(GoalBase):
    """
    uses what i think is a somewhat safe way of evaluating python statements.
    feel free to contact me if you have a better way
    """
    def test(self, memory):
        condition = self.args[0]

        # this only works for simple expressions
        cmpop = (">", "<", ">=", "<=", "==")

        i = 0
        index = 0
        expr = condition.split()
        while index == 0:
            try:
                index = expr.index(cmpop[i])
            except:
                i += 1
                if i > 5:
                    break

        try:
            side0 = float(eval(" ".join(expr[:index]), memory))
            side1 = float(eval(" ".join(expr[index+1:]), memory))
        except NameError:
            return 0.0

        cmpop = cmpop[i]

        if (cmpop == ">") or (cmpop == ">="):
            if side0 == side1:
                return 1.0
            elif side0 > side1:
                v = side0 / side1
            elif side0 < side1:
                if side0 == 0:
                    return 0.0
                else:
                    v = 1 - ((side1 - side0) / side1)

        if v > 1: v = 1.0
        if v < 0: v = 0.0

        return v

    def touch(self, memory):
        def do_it(expr, d):
            try:
                exec(expr in d)
            except NameError as detail:
                name = detail[0].split()[1].strip('\'')
                d[name] = 0
                do_it(expr, d)

            return d

        d = {}
        d['__builtins__'] = None

        for k, v in d.items():
            if k == '__builtins__':
                continue

            memory.add(DatumPrecept(k, v))

        return True


class AlwaysValidGoal(GoalBase):
    """
    Will always be valid.
    """
    def test(self, memory):
        return 1.0


class NeverValidGoal(GoalBase):
    """
    Will never be valid.
    """
    def test(self, memory):
        return 0.0


class PositionGoal(GoalBase):
    """
    This validator is for finding the position of objects.
    """
    def test(self, memory):
        """
        search memory for last known position of the target
        if target is not in agent's memory then return 0.0.

        do pathfinding and determine if the target is accessible
        if not return 0.0

        Determine the distance required to travel to the target
        return 1.0 if the target is reachable
        """

        target = self.args[0]
        target_position = None

        debug("[PositionGoal] testing %s", self.args)

        # find where the target is, according to the memory
        for precept in memory.of_class(PositionPrecept):
            if precept.entity is target:
                target_position = precept.position
                break

        if target_position == self.args[1]:
            return 1.0

        else:
            d = distance(position, target_position)
            if d > self.dist:
                return (float(self.dist / d)) * float(self.dist)
            elif d <= self.dist:
                return 1.0
            else:
                return 0.0

    def touch(self, memory):
        memory.add(PositionPrecept(self.args[0], self.args[1]))


class HasItemGoal(GoalBase):
    """
    returns true if item is in inventory (according to memory)

    when creating instance, 'owner' must be passed as a keyword.
    its value can be any game object that is capable of holding an object

    NOTE: testing can be true to many different objects,
          but touching requires a specific object to function

    any other keyword will be evaluated against precepts in the memory passed.
    """
    def test(self, memory):
        for precept in memory.of_class(PositionPrecept):
            if precept.position[0] == 'self' and precept.entity == self.args[0]:
                return 1.0
        
        return 0.0

    def touch(self, memory):
        memory.add(PositionPrecept(self.args[0], ('self', 0)))