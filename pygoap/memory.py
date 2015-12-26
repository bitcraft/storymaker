"""
Memories are stored precepts.
"""


class MemoryManager(set):
    """
    Store and manage precepts.
    """

    max_size = 300

    def add(self, other):
        assert (other is not None)
        if len(self) > MemoryManager.max_size:
            self.pop()
        super().add(other)

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i
