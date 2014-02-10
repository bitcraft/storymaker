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
import collections

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
        self._context_queue = queue.Queue()
        self._precept_queue = queue.Queue()

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
            # acquiring the planning lock here prevents the entity from forming a plan.
            # this is ** required ** since we are not handling return actions here.
            with entity.planning_lock:
                entity.process(DatumPrecept(entity, 'name', entity.name))
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

        # speedier version of broadcast_precepts(); just send out time precepts
        for agent in self.agents:
            for context in agent.process(t_precept):
                self._context_queue.put(context)

        self.handle_precepts()
        self.handle_actions(td)

    def handle_precepts(self):
        """
        process all of the precepts in the queue
        """

        l = []
        while 1:
            try:
                precept = self._precept_queue.get(False)
                l.append(precept)
            except queue.Empty:
                self.broadcast_precepts(l)
                break

    def handle_actions(self, td):
        """
        process all of the actions in the queue
        """

        next_queue = queue.Queue()
        touched = []
        while 1:
            try:
                context = self._context_queue.get(False)

            except queue.Empty:
                self._context_queue = next_queue
                break

            else:
                if context in touched or context.action.finished:
                    continue

                #print("{} doing {}".format(context.caller, context))
                precept = context.action.next(self.time)
                if precept:
                    self._precept_queue.put(precept)

                if context.action.finished:
                    #print("{} {} finished".format(context.caller, context))
                    touched.append(context)
                    context.touch()
                    context.caller.next_action()
                    for action in context.caller.current_action:
                        self._context_queue.put(action)

                else:
                    next_queue.put(context)


    def model_context(self, context):
        """
        Used to model how an action interacts with the environment.
        Environment can ability to silence actions if they are not able to run.
        """
        return context

    def broadcast_precepts(self, precepts):
        """
        broadcast and model a list of precepts
        """
        model_precept = self.model_precept
        model_context = self.model_context
        enqueue_context = self._context_queue.put

        for p in precepts:

            self.broadcast_hook(p)

            for agent in self._agents:
                for context in agent.process(model_precept(p, agent)):
                    context = model_context(context)
                    if context:
                        enqueue_context(context)

    def broadcast_hook(self, p):
        if isinstance(p, SpeechPrecept):
            msg = '{:>12} {}'.format('{}:'.format(p.entity.name), p.message)
            print(msg)

    def model_precept(self, precept, other):
        """
        override this to model the way that precept objects move in the
        simulation.  by default, all precept objects will be distributed
        indiscriminately to all agents.
        """
        return precept