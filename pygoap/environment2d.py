"""
Since a pyGOAP agent relies on cues from the environment when planning, having
a stable and efficient virtual environment is paramount.  This environment is
simply a placeholder and demonstration.

When coding your game or simulation, you can think of the environment as the
conduit that connects your actors on screen to their simulated thoughts.  This
environment simply provides enough basic information to the agents to work.  It
is up to you to make it useful.
"""

import random
import math

from pygoap.environment import Environment
from pygoap.precepts import *
from pathfinding.astar import search


def distance(a, b):
    """The distance between two (x, y) points."""
    return math.hypot((a[0] - b[0]), (a[1] - b[1]))


def distance2(a, b):
    """The square of the distance between two (x, y) points."""
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def clip(vector, lowest, highest):
    """Return vector, except if any element is less than the corresponding
    value of lowest or more than the corresponding value of highest, clip to
    those values.
    >>> clip((-1, 10), (0, 0), (9, 9))
    (0, 9)
    """
    raise NotImplementedError


class Pathfinding2D:
    @staticmethod
    def get_surrounding(position):
        """
        Return all positions around this one.
        """
        x, y = position

        return ((x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1),
                (x, y + 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1))

    @staticmethod
    def calc_h(position1, position2):
        return distance(position1, position2)

    # @staticmethod
    # def factory(position):
    #     # fix this when position conventions are standardized
    #     try:
    #         if len(position[1]) == 2:
    #             x, y = position[1]
    #         else:
    #             x, y = position
    #     except TypeError:
    #         x, y = position
    #
    #     return Node((x, y))


class Environment2D(Environment, Pathfinding2D):
    """Environments on a 2D plane.

    This class is featured enough to run a simple simulation.
    """
    def __init__(self, width=10, height=10):
        super().__init__()
        self._positions = dict()
        self.width = width
        self.height = height

    def add(self, entity, position=None):
        super().add(entity)
        self.set_position(entity, self.default_position())

    def set_position(self, entity, position):
        self._positions[entity] = position

    def get_position(self, entity):
        return self._positions[entity]

    def model_vision(self, precept, origin, terminus):
        return precept

    def model_sound(self, precept, origin, terminus):
        return precept

    def look(self, parent, direction=None, distance=None):
        """
        Simulate vision by sending precepts to the parent.
        """
        model = self.model_precept
        get_position = self.get_position

        for entity in self.entities:
            parent.process(
                model(
                    PositionPrecept(entity, get_position(entity)),
                    parent
                )
            )

    def objects_at(self, position):
        """
        Return all objects exactly at a given position.
        """
        return [obj for obj in self.entities if obj.position == position]

    def objects_near(self, position, radius):
        """
        Return all objects within radius of position.
        """
        radius2 = radius * radius
        return [obj for obj in self.entities
                if distance2(position, obj.position) <= radius2]

    def default_position(self):
        loc = (random.randint(0, self.width), random.randint(0, self.height))
        return self, loc

    def model_precept(self, precept, other):
        return precept

    def can_move_from(self, agent, dist=100):
        """
        return a list of positions that are possible for this agent to be
        in if it were to move [dist] spaces or less.
        """
        x, y = agent.environment.get_position(agent)[1]
        pos = list()

        for xx in range(x - dist, x + dist):
            for yy in range(y - dist, y + dist):
                if distance2((xx, yy), (x, y)) <= dist:
                    pos.append((self, (xx, yy)))

        return pos

    def pathfind(self, start, finish):
        """
        return a path from start to finish
        """
        return search(start, finish, self.factory)
