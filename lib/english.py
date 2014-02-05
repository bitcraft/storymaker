__author__ = 'Leif'

from pygoap.precepts import *


def make_english(caller, p):
    """
    create an english phrase from a precept
    :rtype : str
    """

    if isinstance(p, DatumPrecept):
        if p.name == "self":
            return "My name is {}.".format(p.value.name)

        return "I am {} {}!".format(p.name, p.value)

    elif isinstance(p, ActionPrecept):
        if p.entity is caller:
            if p.object is None:
                return "I did {}!".format(p.action)
            else:
                return "I did {} with {}!".format(p.action, p.object)
        else:
            if p.object is None:
                return "I saw {} doing {}!".format(p.entity.name, p.action)
            else:
                return "I saw {} doing {} with {}!".format(p.entity.name, p.action, p.object)

    elif isinstance(p, TimePrecept):
        return "The time is now {}.".format(p.time)

    else:
        return "I don't know how to express [{}].".format(p)