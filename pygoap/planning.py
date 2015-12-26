from heapq import heappop, heappush, heappushpop, heapify
import logging

from pygoap.memory import MemoryManager


debug = logging.debug


class PlanningNode:
    __slots__ = 'parent action abilities memory agent delta time cost g h'.split()

    def __init__(self, parent, action, abilities, memory=None, agent=None):
        self.parent = parent
        self.action = action
        self.abilities = abilities
        self.memory = MemoryManager()
        self.agent = agent
        self.delta = MemoryManager()
        self.time = 0
        self.cost = 1
        self.g = -1
        self.h = 1

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
        if parent.agent is None:
            debug("parent.agent is None?")
            continue

        for action in ability.get_actions(parent.agent, parent.memory):
            if action.pretest(parent.memory):
                if action.test(parent.memory) > 0.0:
                    abilities = parent.abilities.copy()
                    abilities.remove(ability)
                    yield PlanningNode(parent, action, abilities)
            else:
                debug("[plan] action %s fail pretest", action)


def plan(goal, agent, start_action, abilities, start_memory):
    node = PlanningNode(None, start_action, abilities, start_memory, agent)
    return _plan(node, goal)


def _plan(key_node, goal):
    """
    Return a list of contexts that could be called to satisfy the goal.
    Cannot duplicate contexts in the plan
    """
    # heap_counter works around a 'bug' in python 3.x where the next value in a
    # tuple is compared if the current set are equal.  using heap_counter
    # ensures that the planning nodes will never be compared.
    heap = list()
    heap_counter = 0
    heap_index = dict()
    open_list = set()
    closed_list = set()

    # deref for speed
    open_list_add = open_list.add
    open_list_remove = open_list.remove
    closed_list_add = closed_list.add
    heap_remove = heap.remove

    # the pushback minimizes heap use and provides a modest speed improvement
    pushback = (0, heap_counter, key_node)
    open_list_add(key_node)

    debug("[plan] memory supplied is %s", key_node.memory)

    while heap or pushback:
        if pushback:
            key_node = heappushpop(heap, pushback)[2]
            pushback = None
        else:
            key_node = heappop(heap)[2]
        if goal.test(key_node.memory):
            break
        open_list_remove(key_node)
        closed_list_add(key_node)
        children = [i for i in get_children(key_node) if not i in closed_list]
        for child in children:
            g = key_node.g + child.cost
            if child not in open_list or g < child.g:
                heap_counter += 1
                child.parent = key_node
                child.g = g
                if child in open_list:
                    heap_remove(heap_index[child])
                    heapify(heap)
                else:
                    open_list_add(child)
                entry = (child.g + child.h, heap_counter, child)
                heap_index[child] = entry
                if pushback:
                    heappush(heap, pushback)
                pushback = entry

    # else is reached when while() test becomes false
    # under normal circumstances, the loop should break when path is found
    else:
        return list()

    debug("[plan] successful %s %s", key_node.action, key_node.action)
    path = [[key_node.action]]
    while key_node.parent is not None:
        key_node = key_node.parent
        path.append([key_node.action])
    return path
