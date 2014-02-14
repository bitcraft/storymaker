import sys

test_fail_msg = "some goal is returning None on a test, this is a bug."


class ActionException(Exception):
    pass


class Ability:
    """
    Abilities evaluate a blackboard and generate actions for an agent to use.
    """
    provides = []
    requires = []

    def get_contexts(self, caller, memory=None):
        """
        Return a generator of all the actions valid in this context
        """
        raise NotImplementedError


class Action:
    """
    duration should be at least 1.  if it is 0 (or less), then the agent will
    make a new plan on each precept during a time step.  this will kill
    performance and there seems to be no real advantages to this design.
    """
    default_duration = 1

    def __init__(self):
        self.duration = self.default_duration
        self.context = None
        self.finished = False
        self._interval = None
        self._generator = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._generator is None:
            self._generator = self.update(self._interval)
        return next(self._generator)

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
        must be a generator that returns precepts
        """
        raise NotImplementedError


class ActionContext:
    """
    Used by planner
    """
    def __init__(self, caller, action, prereqs=None, effects=None, **kwargs):
        self.__dict__.update(kwargs)

        self.caller = caller
        self.action = action
        action.context = self

        self.prereqs = prereqs
        if self.prereqs is None: self.prereqs = []

        self.effects = effects
        if self.effects is None: self.effects = []

    def test(self, memory=None):
        """
        Determine whether or not this context is valid

        return a float from 0-1 that describes how valid this action is.

        validity of an action is a measurement of how effective the action will
        be if it is completed successfully.

        if any of the prereqs are not partially valid ( >0 ) then will return 0

        for many actions a simple 0 or 1 will work.  for actions which
        modify numerical values, it may be useful to return a fractional value.
        """
        if not self.prereqs:
            return 1.0

        if memory is None:
            raise Exception

        values = (i.test(memory) for i in self.prereqs)

        try:
            return float(sum(values)) / len(self.prereqs)
        except TypeError:
            print(zip(values, self.prereqs))
            print(test_fail_msg)
            sys.exit(1)

    def touch(self, memory=None):
        """
        Convenience function to touch a blackboard with all the effects
        """
        if memory is None: memory = self.caller.memory
        [i.touch(memory) for i in self.effects]

    def __repr__(self):
        return '<ActionContext: {}>'.format(self.action.__class__.__name__)