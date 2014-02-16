from pygoap.memory import MemoryManager
from heapq import heappop, heappush, heappushpop
import logging

debug = logging.debug


def get_children(parent_node, agent):
    for ability in parent_node.abilities:
        for context in ability.get_contexts(agent, parent_node.memory):
            if context.test(parent_node.memory) > 0.0:
                abilities = parent_node.abilities.copy()
                abilities.remove(ability)
                yield PlanningNode(parent_node, context, abilities)


class PlanningNode(object):
    __slots__ = (
        'parent',
        'context',
        'abilities',
        'memory',
        'delta',
        'time',
        'cost',
        'g',
        'h',
    )

    def __init__(self, parent, context, abilities, memory=None):
        self.parent = parent
        self.context = context
        self.abilities = abilities
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        self.time = 0
        self.cost = 1
        self.g = -1
        self.h = 1

        if parent:
            self.memory.update(parent.memory)

        elif memory:
            self.memory.update(memory)

        if context:
            context.touch(self.memory)
            context.touch(self.delta)

    def __repr__(self):
        if self.parent:
            return "<PlanningNode: '%s', cost: %s, p: %s>" % \
                   (self.context.__class__.__name__,
                    self.cost,
                    self.parent.context.__class__.__name__)

        else:
            return "<PlanningNode: '%s', cost: %s, p: None>" % \
                   (self.context,
                    self.cost)


def plan(agent, abilities, start_context, start_memory, goal):
    """
    Return a list of contexts that could be called to satisfy the goal.
    Cannot duplicate contexts in the plan
    """

    # heap_counter works around a 'bug' in python 3.x where the next value in a tuple
    # is compared if the current set are equal.  using heap_counter ensures that the
    # planning nodes will never be compared (which raises a an exception!)
    key_node = PlanningNode(None, start_context, abilities, start_memory)
    heap = []
    heap_index = {}
    heap_counter = 0
    open_list = set()
    closed_list = set()

    pushback = (0, heap_counter, key_node)
    open_list.add(key_node)

    debug("[plan] solve %s starting from %s", goal, start_context)
    debug("[plan] memory supplied is %s", start_memory)

    while heap or pushback:
        if pushback:
            key_node = heappushpop(heap, pushback)[2]
            pushback = None
        else:
            key_node = heappop(heap)[2]
        if goal.test(key_node.memory):
            break
        open_list.remove(key_node)
        closed_list.add(key_node)
        for child in get_children(key_node, agent):
            if child in closed_list:
                continue
            g = key_node.g + child.cost
            if child not in open_list or g < child.g:
                heap_counter += 1
                child.parent = key_node
                child.g = g
                if child in open_list:
                    heap.remove(heap_index[child])
                else:
                    open_list.add(child)
                entry = (child.g + child.h, heap_counter, child)
                heap_index[child] = entry
                if pushback:
                    heappush(heap, pushback)
                pushback = entry
    else:
        return []

    # sometime in the future, the planner will be able to resolve contexts that can run concurrently.
    # until then, simply add each step as a single-element list
    debug("[plan] successful %s %s", key_node.context, key_node.parent)
    path = [[key_node.context]]
    while key_node.parent is not None:
        key_node = key_node.parent
        path.append([key_node.context])
    return path

