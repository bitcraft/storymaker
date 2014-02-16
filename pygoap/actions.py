import sys

test_fail_msg = "some goal is returning None on a test, this is a bug."


class ActionException(Exception):
    pass


class Action:
    """
    Action / Operator

    I just don't even know anymore
    """
    default_duration = 1
    provides = []
    requires = []
    domain = None

    def __init__(self, parent, prereqs=None, effects=None, name=None, memory=None, **kwargs):
        self.parent = parent
        self.name = name

        self.prereqs = prereqs
        if self.prereqs is None:
            self.prereqs = []

        self.effects = effects
        if self.effects is None:
            self.effects = []

        self.memory = memory
        if self.memory is None:
            self.memory = set()

        self.duration = self.default_duration
        self.finished = False
        self._interval = None
        self._generator = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._generator is None:
            self._generator = self.update(self._interval)
        return next(self._generator)

    def __repr__(self):
        return '<ActionContext: {}>'.format(self.__class__.__name__)

    def step(self, dt):
        """
        called by the environment.  do not override.  use update instead.
        return a generator of update()
            the generator will repeat until self._duration is <= 0
        """
        self.duration -= dt
        self._interval = dt
        self._generator = None

        if self.duration <= 0:
            self.finished = True

        return self

    def update(self, dt):
        """
        must be a generator that yields precepts
        """
        raise StopIteration

    def get_actions(self, parent, memory=None):
        """
        Return a generator of child abilities, or [] if this can make changes to world state
        """
        return []

    def pretest(self, memory):
        """
        Convenience function to pretest a Memory with all prereqs

        A pretest is a quicker test that should be called on a Memory delta
        """
        for prereq in self.prereqs:
            if not prereq.pretest(memory):
                return 0.0

        return 1.0

    def test(self, memory):
        """
        Convenience function to test a Memory with all prereqs
        """
        if not self.prereqs:
            return 1.0

        values = (i.test(memory) for i in self.prereqs)

        try:
            return float(sum(values)) / len(self.prereqs)
        except TypeError:
            print(zip(values, self.prereqs))
            print(test_fail_msg)
            sys.exit(1)

    def touch(self, memory=None):
        """
        Convenience function to touch a Memory with all effects
        """
        if memory is None:
            memory = self.parent.memory

        for i in self.effects:
            i.touch(memory)
