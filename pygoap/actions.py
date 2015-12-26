from . import easing


test_fail_msg = "some goal is returning None on a test, this is a bug."


class ActionException(Exception):
    pass


class Action:
    """
    Actions are performed over time
    they have prerequisites that must be satisfied
    they have effects that occur when action is finished
    they have easing functions that modify how 'complete' the action is
    """
    default_duration = 1.0
    default_easing = easing.linear
    provides = list()
    requires = list()
    domain = None

    def __init__(self, parent, prereqs=None, effects=None, memory=None,
                 **kwargs):
        self.parent = parent

        self.prereqs = prereqs
        if self.prereqs is None:
            self.prereqs = list()

        self.effects = effects
        if self.effects is None:
            self.effects = list()

        self.memory = memory
        if self.memory is None:
            self.memory = set()

        self._duration = self.default_duration
        self.easing = self.default_easing
        self._elapsed_time = 0.0
        self._progress = 0.0
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
        self._interval = dt
        self._generator = None
        self._progress += dt
        return self

    def update(self, dt):
        """
        must be a generator that yields precepts
        """
        raise StopIteration

    def get_actions(self, parent, memory=None):
        """
        Return a generator of child abilities, or empty list if this can make
        changes to world state
        """
        return list()

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
            print((list(zip(values, self.prereqs))))
            print(test_fail_msg)
            raise

    def touch(self, memory=None):
        """
        Convenience function to touch a Memory with all effects
        """
        if memory is None:
            memory = self.parent.memory

        for i in self.effects:
            i.touch(memory)

    @property
    def progress(self):
        return self.easing(self._elapsed_time / self._duration)

    @property
    def finished(self):
        return self.progress >= 1.0

    @property
    def duration(self):
        return self._duration

    @property
    def elapsed_teme(self):
        return self._elapsed_time
