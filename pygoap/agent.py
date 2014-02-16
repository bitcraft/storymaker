from pygoap.environment import ObjectBase
from pygoap.planning import PlanningNode, plan
from pygoap.memory import MemoryManager
from pygoap.precepts import *
import logging
import threading

debug = logging.debug


class GoapAgent(ObjectBase):
    """
    AI Agent
    """
    idle_timeout = 30  # not implemented yet

    def __init__(self):
        super(GoapAgent, self).__init__()
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        self.lock = threading.Lock()
        self.current_goal = None
        self.goals = set()          # all goals this instance can use
        self.abilities = set()      # all actions this agent can perform (defined by action contexts!)
        self.filters = []           # list of methods to use as a filter
        self.plan = []              # list of actions to perform

    def __repr__(self):
        return "<Agent: {}>".format(self.name)

    def reset(self):
        self.memory = MemoryManager()
        self.current_goal = None
        self.goals = set()
        self.abilities = set()
        self.filters = []
        self.plan = []

    def filter_precept(self, precept):
        """
        precepts can be put through filters to change them.
        this can be used to simulate errors in judgement by the agent dropping the precept,
        or maybe a condition or limitation of the agent
        """

        for f in self.filters:
            for p in f(self, precept):
                yield p

    def process_list(self, all_precepts):
        """
        feed the agent precepts.  do not send a single precept otherwise strange errors will occur.
        """
        if not isinstance(all_precepts, (tuple, list, set)):
            all_precepts = [all_precepts]

        for precept in all_precepts:
            self.process(precept)

    def process(self, precept):
        """
        feed the agent one single precept.
        """
        for this_precept in self.filter_precept(precept):
            debug("[agent] %s recv'd precept %s", self, this_precept)
            if not isinstance(precept, TimePrecept):
                self.delta.add(precept)

    # hack
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
        s = sorted(((g.get_relevancy(self.memory), g) for g in self.goals), reverse=True, key=lambda i: i[0])
        s = [i for i in s if i[0] > 0]

        debug("[agent] %s has goals %s", self, s)

        start_action = None
        self.plan = []
        for score, goal in s:
            node = PlanningNode(None, start_action, self.abilities, self.delta, agent=self)
            tentative_plan = plan(node, goal)

            if tentative_plan:
                tentative_plan.pop(-1)
                self.plan = tentative_plan
                self.current_goal = goal
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
            return []

    def next_action(self):
        """
        force the agent to stop the current action (context) and start the next one
        """
        try:
            self.plan.pop(-1)
        except IndexError:
            pass
