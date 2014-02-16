from pygoap.memory import MemoryManager
from heapq import heappop, heappush, heappushpop
import logging

debug = logging.debug


class PlanningNode:
    __slots__ = 'parent action abilities memory delta time cost g h'.split()
    agent = None

    def __init__(self, parent, action, abilities, memory=None, agent=None):
        self.parent = parent
        self.action = action
        self.abilities = abilities
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        self.time = 0
        self.cost = 1
        self.g = -1
        self.h = 1

        if agent:
            PlanningNode.agent = agent

        if parent:
            self.memory.update(parent.memory)

        elif memory:
            self.memory.update(memory)

        if action:
            action.touch(self.memory)
            action.touch(self.delta)

    def __repr__(self):
        if self.parent:
            return "<PlanningNode: '%s', cost: %s, p: %s>" % \
                   (self.action.__class__.__name__,
                    self.cost,
                    self.parent.context.__class__.__name__)

        else:
            return "<PlanningNode: '%s', cost: %s, p: None>" % \
                   (self.action,
                    self.cost)


# TODO: make recursive
def get_children(parent):
    for ability in parent.abilities:
        for action in ability.get_actions(parent.agent, parent.memory):
            if action.pretest(parent.memory):
                if action.test(parent.memory) > 0.0:
                    abilities = parent.abilities.copy()
                    abilities.remove(ability)
                    yield PlanningNode(parent, action, abilities)
            else:
                debug("[plan] action %s fail pretest", action)


def plan(key_node, goal):
    """
    Return a list of contexts that could be called to satisfy the goal.
    Cannot duplicate contexts in the plan
    """

    # heap_counter works around a 'bug' in python 3.x where the next value in a tuple
    # is compared if the current set are equal.  using heap_counter ensures that the
    # planning nodes will never be compared (which raises a an exception!)
    heap = []
    heap_index = {}
    heap_counter = 0
    open_list = set()
    closed_list = set()

    pushback = (0, heap_counter, key_node)
    open_list.add(key_node)

    debug("[plan] memory supplied is %s", key_node.memory)

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
        for child in get_children(key_node):
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
    debug("[plan] successful %s %s", key_node.action, key_node.action)
    path = [[key_node.action]]
    while key_node.parent is not None:
        key_node = key_node.parent
        path.append([key_node.action])
    return path

