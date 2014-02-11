from pygoap.memory import MemoryManager
from heapq import heappop, heappush
import logging

debug = logging.debug


def get_children(parent0, parent, abilities):
    for ability in abilities:
        for context in ability.get_contexts(parent0, parent.memory):
            if context.test(parent.memory) > 0.0:
                yield PlanningNode(parent, ability, context)


def calc_g(node):
    cost = node.cost
    while not node.parent is None:
        node = node.parent
        cost += node.cost
    return cost


class PlanningNode(object):
    def __init__(self, parent, ability, context, memory=None):
        self.parent = parent
        self.ability = ability
        self.context = context
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        #self.cost = action.calc_cost()
        self.cost = 1
        self.g = calc_g(self)
        self.h = 1

        if parent:
            self.memory.update(parent.memory)

        elif memory:
            self.memory.update(memory)

        if context:
            context.touch(self.memory)
            context.touch(self.delta)

    def __eq__(self, other):
        if isinstance(other, PlanningNode):
            return self.delta == other.delta
        else:
            return False

    def __repr__(self):
        if self.parent:
            return "<PlanningNode: '%s', cost: %s, p: %s>" % \
                   (self.context.__class__.__name__,
                    self.cost,
                    self.parent.action.__class__.__name__)

        else:
            return "<PlanningNode: '%s', cost: %s, p: None>" % \
                   (self.context.__class__.__name__,
                    self.cost)


def plan(parent, contexts, start_action, start_memory, goal):
    """
    Return a list of contexts that could be called to satisfy the goal.
    Cannot duplicate contexts in the plan
    """

    # heap_index works around a 'bug' in python 3.x where the next value in a tuple
    # is compared if the current set are equal.  using heap_index ensures that the
    # planning nodes will never be compared (which raises a different exception!)
    key_node = PlanningNode(None, None, start_action, start_memory)
    heap_index = 0
    open_list = [(0, heap_index, key_node)]
    closed_list = []

    debug("[plan] solve %s starting from %s", goal, start_action)
    debug("[plan] memory supplied is %s", start_memory)

    while open_list:
        key_node = heappop(open_list)[2]

        if goal.test(key_node.memory):
            debug("[plan] successful %s", key_node.context.action)
            break

        closed_list.append(key_node)
        for child in get_children(parent, key_node, contexts):
            if child in closed_list:
                continue
            g = key_node.g + child.cost

            if child not in open_list or g < child.g:
                child.parent = key_node
                child.g = g
                if child not in open_list:
                    heappush(open_list, (child.g + child.h, heap_index, child))
                    heap_index += 1
    else:
        return []

    # sometime in the future, the planner will be able to resolve contexts that can run concurrently.
    # until then, simply add each step as a single-element list
    path = [[key_node.context]]
    while key_node.parent is not None:
        key_node = key_node.parent
        path.append([key_node.context])
        #return list(reversed(path))
    return path

