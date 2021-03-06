import logging
from operator import itemgetter

from pygoap.memory import MemoryManager
from pygoap.environment import ObjectBase
from pygoap.planning import plan
from pygoap.precepts import *


debug = logging.debug


class GoapAgent(ObjectBase):
    """
    AI Agent
    """

    def __init__(self):
        super().__init__()
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        self.goals = set()          # all goals this instance can use
        self.abilities = set()      # all actions this agent can perform
        self.filters = list()       # list of methods to use as a filter
        self.plan = list()          # list of actions to perform

    def __repr__(self):
        return "<Agent: {}>".format(self.name)

    def filter_precept(self, precept):
        """
        precepts can be put through filters to change them.
        this can be used to simulate errors in judgement by the agent dropping
        the precept, or maybe a condition or limitation of the agent
        """
        for f in self.filters:
            for p in f(self, precept):
                yield p

    def process_list(self, precepts):
        """
        feed the agent precepts.
        """
        if not isinstance(precepts, (tuple, list, set)):
            precepts = [precepts]

        for precept in precepts:
            self.process(precept)

    def process(self, precept):
        """
        feed the agent one single precept.
        """
        for this_precept in self.filter_precept(precept):
            debug("[agent] %s recv'd precept %s", self, this_precept)
            if not isinstance(precept, TimePrecept):
                self.delta.add(precept)

    def plan_if_needed(self):
        if len(self.plan) == 0:
            self.find_plan()

    def find_plan(self):
        """
        force agent to re-evaluate goals and to formulate a plan
        """
        # get the relevancy of each goal according to the state of the agent
        # filter out goals that are not relevant (==0)
        # sort goals so that highest relevancy are first
        s = sorted(((g.get_relevancy(self.memory), g) for g in self.goals),
                   reverse=True, key=itemgetter(0))
        s = [i for i in s if i[0] > 0]

        debug("[agent] %s has goals %s", self, s)

        start_action = None
        self.plan = list()
        for score, goal in s:
            tentative = plan(goal, self, start_action, self.abilities,
                             self.delta)

            if tentative:
                tentative.pop(-1)
                self.plan = tentative
                debug("[agent] %s has planned to %s", self, goal)
                debug("[agent] %s has plan %s", self, self.plan)
                break

        self.memory.update(self.delta)
        self.delta.clear()

        return self.plan

    @property
    def running_actions(self):
        """
        get the current contexts of the current plan
        """
        try:
            return self.plan[-1]
        except IndexError:
            return list()

    def next_action(self):
        """
        force the agent to stop the current action (context) and start the next
        """
        try:
            self.plan.pop(-1)
        except IndexError:
            pass
