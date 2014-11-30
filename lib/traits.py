import random


class Trait:
    def __init__(self, name, kind):
        self.name = name
        self.value = kind()

    def __eq__(self, other):
        return self.value == other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __mul__(self, other):
        return self.value * other

    def __add__(self, other):
        return self.value + other

    def __repr__(self):
        return '<Trait: {} {}>'.format(self.name, self.value)


class Traits:
    """
    Traits are generally not modified, and goals should not normally be
    triggered by changes or the state of a trait.
    """
    default = [
        "strength",
        "perception",
        "endurance",  # endurance is used to modify hunger
        "charisma",
        "intelligence",
        "agility",
        "luck",
        "chatty",
        "moral",
        "tradition",
        "alignment",
        "touchy",
        "esteem",
        "karma",
        "report"
    ]

    def __init__(self):
        self.__traits = dict()
        for name in self.default:
            self.__traits[name] = Trait(name, float)

    def __getattr__(self, item):
        try:
            return self.__traits[item]
        except KeyError:
            raise AttributeError

    def __iter__(self):
        return iter(self.__traits)

    @classmethod
    def random(cls):
        t = cls()
        for key, value in t.__traits.items():
            t.__traits[key].value = random.random()
        return t
