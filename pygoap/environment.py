"""
Since a pyGOAP agent relies on cues from the environment when planning, having
a stable and efficient virtual environment is paramount.

When coding your game or simulation, you can think of the environment as the
conduit that connects your actors on screen to their simulated thoughts.  This
environment simply provides enough basic information to the agents to work.  It
is up to you to make it useful.
"""

from pygoap.precepts import *
from itertools import chain
import logging
import queue

debug = logging.debug



class ObjectBase(object):
    """
    class for objects that agents can interact with
    """

    name = 'noname'

    def __init__(self):
        self._condition = {}

    def get_actions(self, other):
        """
        generate a list of actions that could be used with this object
        """
        return []        

    def condition(self, name):
        try:
            return self._condition[name]
        except KeyError:
            return False

    def set_condition(self, name, value):
        self._condition[name] = value

    def __repr__(self):
        return "<Object: {}>".format(self.name)


class Environment(object):
    """
    Abstract class representing an Environment.
    'Real' Environment classes inherit from this
    """

    def __init__(self):
        self.time = 0
        self._agents = []
        self._entities = []
        self._positions = {}
        self._action_queue = queue.Queue()

    @property
    def agents(self):
        return iter(self._agents)

    @property
    def entities(self):
        return chain(self._entities, self._agents)

    def get_position(self, entity):
        raise NotImplementedError

    # this is a placeholder hack.  proper handling will go through model_precept()
    def look(self, caller):
        for i in chain(self._entities, self._agents):
            caller.process(PositionPrecept(i, self._positions[i]))

    def add(self, entity, position=None):
        """
        Add an entity to the environment
        """

        from pygoap.agent import GoapAgent

        debug("[env] adding %s", entity)

        # hackish way to force agents to re-evaluate their environment
        for a in self._agents:
            to_remove = []

            for p in a.memory.of_class(DatumPrecept):
                if p.name == 'aware':
                    to_remove.append(p)

            [a.memory.remove(p) for p in to_remove]

        # add the agent
        if isinstance(entity, GoapAgent):
            self._agents.append(entity)
            entity.environment = self
            self._positions[entity] = (None, (0, 0))

            # clever hack to let the planner know who the memory belongs to
            entity.process(DatumPrecept('self', entity))
        else:
            self._entities.append(entity)

    def update(self, td):
        """
        * Update our time
        * Let agents know time has passed
        * Update actions that may be running
        * Add new actions to the que
        """

        # update time in the simulation
        self.time += td

        # let all the agents know that time has passed
        t_precept = TimePrecept(self.time)

        # get all the running actions for the agents
        for agent in self.agents:
            for action in agent.process(t_precept):
                self._action_queue.put(action)

        self.handle_queue(td)

    def handle_queue(self, td):
        """
        process all of the actions in the queue
        """
        
        while 1:
            try:
                context = self._action_queue.get(False)
                context.action.send(td)    # give the coroutine a chance to operate
            except queue.Empty:    # raised when queue is empty
                break
            except StopIteration:  # raised when action is finished
                context.touch()
            else:                  # action isn't finished, so re-add it to the queue
                self._action_queue.put(context)

    def model_action(self, action):
        """
        Used to model how an action interacts with the environment.
        Environment can ability to silence actions if they are not able to run.
        """
        return True

    def broadcast_precepts(self, precepts, agents=None):
        """
        for efficiency, please use this for sending a list of precepts
        """
        if agents is None:
            agents = self.agents

        model = self.model_precept
        for p in precepts:
            [a.process(model(p, a)) for a in agents]

    def model_precept(self, precept, other):
        """
        override this to model the way that precept objects move in the
        simulation.  by default, all precept objects will be distributed
        indiscriminately to all agents.
        """
        return precept