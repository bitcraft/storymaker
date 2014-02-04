"""
Memories are stored precepts.
"""

class MemoryManager(set):
    """
    Store and manage precepts.
    """

    def add(self, other):
        if len(self) > 20:
            self.pop()
        super(MemoryManager, self).add(other)

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i
