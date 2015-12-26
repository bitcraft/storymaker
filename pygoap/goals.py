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
__all__ = ['GoalBase',
           'WeightedGoal',
           'PreceptGoal',
           'EvalGoal',
           'AlwaysValidGoal',
           'NeverValidGoal']

import logging
import re

from pygoap.environment2d import distance
from pygoap.precepts import *


debug = logging.debug

eval_re = re.compile("(.+?)(>=|<=|>|<|!=|==)(.+)")


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

        self.required_types = frozenset()

        self.weight = kwargs.get('weight', None)
        if self.weight is None:
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

    def __repr__(self):
        try:
            return "<Goal: {}>".format(self.name)
        except AttributeError:
            return "<Goal: {}>".format(self.__class__.__name__)


class WeightedGoal(GoalBase):
    """
    Goal will only use the weight to determine its relevancy
    """

    def test(self, memory):
        return 1.0

    def get_relevancy(self, memory):
        return self.weight


class PreceptGoal(GoalBase):
    """
    Uses Precepts as a test
    """
    valid = (PositionPrecept, TimePrecept, DatumPrecept, ActionPrecept,
             SpeechPrecept, MoodPrecept)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.args) == 0:
            raise ValueError

        for a in self.args:
            if not any(isinstance(a, i) for i in self.valid):
                raise ValueError

        self.required_types = frozenset(type(i) for i in self.args)

    def pretest(self, precepts):
        """
        A pretest is a quicker test that should be called on a Memory delta
        """
        return not self.required_types.isdisjoint(list(map(type, precepts)))

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

    def __init__(self, condition, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.condition = condition
        m = eval_re.match(condition)
        if m is None:
            raise ValueError

    def test(self, memory):
        return eval(self.condition)

    def touch(self, memory):
        def do_it(expr, d):
            try:
                exec(expr in d)
            except NameError as detail:
                name = detail[0].split()[1].strip('\'')
                d[name] = 0
                do_it(expr, d)

            return d

        d = dict()
        d['__builtins__'] = None

        for k, v in list(d.items()):
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


