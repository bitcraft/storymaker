from pygoap.environment import ObjectBase
from pygoap.planning import plan
from pygoap.memory import MemoryManager
from pygoap.precepts import *
import logging
import threading

debug = logging.debug

NullAction = None


# required to reduce memory usage
def time_filter(precept):
    return None if isinstance(precept, TimePrecept) else precept


class GoapAgent(ObjectBase):
    """
    AI Agent
    """
    # not implemented yet
    idle_timeout = 30

    def __init__(self):
        super(GoapAgent, self).__init__()
        self.memory = MemoryManager()
        self.planner = plan

        # if acquired, this lock will prevent this agent from planning
        self.planning_lock = threading.Lock()

        self.current_goal = None

        self.goals = set()          # all goals this instance can use
        self.abilities = set()      # all actions this agent can perform (defined by action contexts!)
        self.filters = []           # list of methods to use as a filter
        self.plan = []              # list of actions to perform

        # this special filter will prevent time precepts from being stored
        #self.filters.append(time_filter)

    def reset(self):
        self.memory = MemoryManager()
        self.planner = plan
        self.current_goal = None
        self.goals = set()
        self.abilities = set()
        self.filters = []
        self.plan = []

    def filter_precept(self, precept):
        """
        precepts can be put through filters to change them.
        this can be used to simulate errors in judgement by the agent.
        """
        for f in self.filters:
            for p in f(self, precept):
                yield p

    def process(self, precept):
        """
        used by the environment to feed the agent precepts.
        agents can respond by sending back an action to take.
        """
        for precept in self.filter_precept(precept):
            debug("[agent] %s recv'd precept %s", self, precept)
            if not isinstance(precept, TimePrecept):
                self.memory.add(precept)

        # threads or the environment may lock the planner for performance or data
        # integrity reasons.  if the planner is locked, then silently return []
        if self.planning_lock.acquire(False):
            a = self.running_contexts()
            if not a:
                self.replan()
            self.planning_lock.release()
            return self.running_contexts()

        return []

    def replan(self):
        """
        force agent to re-evaluate goals and to formulate a plan
        """
        # get the relevancy of each goal according to the state of the agent
        s = ((g.get_relevancy(self.memory), g) for g in self.goals)

        # remove goals that are not important (relevancy == 0)
        s = [g for g in s if g[0] > 0.0]

        # sort goals so that highest relevancy are first
        s.sort(reverse=True, key=lambda i: i[0])

        debug("[agent] %s has goals %s", self, s)

        # starting from the most relevant goal, attempt to make a plan
        start_action = NullAction
        self.plan = []
        for score, goal in s:
            tentative_plan = self.planner(self, self.abilities, start_action, self.memory, goal)

            if tentative_plan:
                tentative_plan.pop(-1)
                self.plan = tentative_plan
                self.current_goal = goal
                debug("[agent] %s has planned to %s", self, goal)
                debug("[agent] %s has plan %s", self, self.plan)
                break

    def running_contexts(self):
        return self.current_context

    @property
    def current_context(self):
        """
        get the current action of the current plan
        """
        try:
            return self.plan[-1]
        except IndexError:
            return []

    def next_context(self):
        """
        force the agent to stop the current action (context) and start the next one

        used by the environment.
        """
        try:
            self.plan.pop(-1)
        except IndexError:
            pass
