from pygoap.precepts import *


def name(p):
    try:
        return p.name
    except AttributeError:
        return p


def make_english(caller, p):
    """
    create an english phrase from a precept
    very simple!!
    :rtype : str
    """

    if isinstance(p, DatumPrecept):
        if p.entity is caller:
            if p.name == "name":
                return "My name is {}.".format(p.value)

            return "I {} is {}.".format(p.name, name(p.value))

        elif p.entity is None:
            return "Did you know that {} is {}?".format(p.name,
                                                        name(p.value))

        else:
            if p.name == "name":
                return "His name is {}.".format(p.value)

            return "Did you know that {}\'s {} is {}?".format(
                name(p.entity), p.name, name(p.value))

    elif isinstance(p, ActionPrecept):
        if p.entity is caller:
            if p.object is None:
                return "I did {}!".format(p.action)
            else:
                return "I did {} with {}!".format(p.action, name(p.object))
        else:
            if p.object is None:
                return "I saw {} doing {}!".format(p.entity.name, p.action)
            else:
                return "I saw {} doing {} with {}!".format(p.entity.name,
                                                           p.action,
                                                           name(p.object))

    elif isinstance(p, SpeechPrecept):
        if p.entity is caller:
            return 'I said "{}"'.format(p.message)

        else:
            return 'I heard {} say "{}"'.format(p.entity.name, p.message)

    elif isinstance(p, TimePrecept):
        return "The time is now {}.".format(p.time)

    elif isinstance(p, MoodPrecept):
        if p.entity is caller:
            if p.value < .5:
                return 'I am not {}.'.format(p.name)
            else:
                return 'I am {}.'.format(p.name)

        else:
            if p.value < .5:
                return '{} is feeling not {}.'.format(name(p.entity),
                                                      p.name)
            else:
                return '{} is feeling {}.'.format(name(p.entity), p.name)
    else:
        return "I don't know how to express [{}].".format(p)
