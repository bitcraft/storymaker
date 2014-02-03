from pygoap.memory import MemoryManager
from heapq import heappop, heappush
import logging

debug = logging.debug



def get_children(parent0, parent, contexts):
    def get_used_class(node):
        while node.parent is not None:
            yield node.context
            node = node.parent

    used_class = set(get_used_class(parent))

    for context in contexts:
        if context in used_class:
            continue

        for action in context(parent0, parent.memory):
            yield PlanningNode(parent, context, action)

def calcG(node):
    cost = node.cost
    while not node.parent == None:
        node = node.parent
        cost += node.cost 
    return cost


class PlanningNode(object):
    def __init__(self, parent, context, action, memory=None):
        self.parent = parent
        self.context = context
        self.action = action
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        #self.cost = action.calc_cost()
        self.cost = 1
        self.g = calcG(self)
        self.h = 1

        if parent:
            self.memory.update(parent.memory)

        elif memory:
            self.memory.update(memory)

        if action:
            cor, effects = action
            [ i.touch(self.memory) for i in effects ]
            [ i.touch(self.delta) for i in effects ]

    def __eq__(self, other):
        if isinstance(other, PlanningNode):
            return self.delta == other.delta
        else:
            return False

    def __repr__(self):
        if self.parent:
            return "<PlanningNode: '%s', cost: %s, p: %s>" % \
            (self.action.__class__.__name__,
                self.cost,
                self.parent.action.__class__.__name__)

        else:
            return "<PlanningNode: '%s', cost: %s, p: None>" % \
            (self.action.__class__.__name__,
                self.cost)


def plan(parent, contexts, start_action, start_memory, goal):
    """
    Return a list of contexts that could be called to satisfy the goal.
    Cannot duplicate contexts in the plan
    """
    #this works around a 'bug' in python 3.x where the next value in a tuple is compared
    #compared if the current set are equal.  this ensures that the planning nodes will never
    #be compared.
    key_node = PlanningNode(None, None, start_action, start_memory)
    heap_index = 0
    openlist = [(0, heap_index, key_node)]
    closedlist = []

    debug("[plan] solve %s starting from %s", goal, start_action)
    debug("[plan] memory supplied is %s", start_memory)

    while openlist:
        key_node = heappop(openlist)[2]

        if goal.test(key_node.memory):
            debug("[plan] successful %s", key_node.action)
            break

        closedlist.append(key_node)
        for child in get_children(parent, key_node, contexts):
            if child in closedlist:
                continue
            g = key_node.g + child.cost

            if child not in openlist or g < child.g:
                child.parent = key_node
                child.g = g
                if child not in openlist:
                    heappush(openlist, (child.g + child.h, heap_index, child))
                    heap_index += 1
    else:
        return []

    path = [key_node.action]
    while key_node.parent is not None:
        key_node = key_node.parent
        path.append(key_node.action)
    return path

