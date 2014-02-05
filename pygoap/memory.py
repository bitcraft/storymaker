"""
Memories are stored precepts.
"""


class MemoryManager(set):
    """
    Store and manage precepts.
    """

    max_size = 20

    def add(self, other):
        if len(self) > MemoryManager.max_size:
            self.pop()
        super(MemoryManager, self).add(other)

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i
