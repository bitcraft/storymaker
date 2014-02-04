from heapq import heappush, heappop


class Astar(object):
    pass


class Node(object):
    __slots__ = ['parent', 'x', 'y', 'g', 'h', 'f', 'is_closed']

    def __init__(self, pos=(0,0)):
        self.x, self.y = pos
        self.parent = None
        self.g = 0
        self.h = 0
        self.is_closed = 0

    def __eq__(self, other):
        try:
            return (self.x == other.x) and (self.y == other.y)
        except AttributeError:
            return False

    def __repr__(self):
        return "<Node: x={} y={}>".format(self.x, self.y)


def get_surrounding(node):
    return ((node.x-1, node.y-1), (node.x, node.y-1), (node.x+1, node.y-1),
            (node.x-1, node.y),   (node.x+1, node.y),
            (node.x-1, node.y+1), (node.x, node.y+1), (node.x+1, node.y+1))


def dist(start, finish):
    return abs(finish.x - start.x) + abs(finish.y - start.y)


def calc_g(node):
    score = 0
    score += node.g
    while not node.parent is None:
        node = node.parent
        score += node.g
    return score


def calc_h(node, finish):
    # somehow factor in the cost of other nodes
    return abs(finish.x - node.x) + abs(finish.y - node.y)


def search(start, finish, factory):
    """
    perform basic a* search on a 2d map.
   
    Args:
        start:      tuple that defines the starting position
        finish:     tuple that defined the finish
        factory:    function that will return a Node object from a position

    Factory can return None, which means the area is not passable.
    """

    finish_node = factory(finish)
    start_node = factory(start)
    start_node.h = calc_h(start_node, finish_node)

    # used to locate nodes in the heap and modify their f scores
    heap_index = {}
    entry = [start_node.g + start_node.h, start_node]
    heap_index[start_node] = entry

    open_list = [entry]

    node_hash = {}
    node_hash[start] = start_node

    while open_list:
        try:
            f, key_node = heappop(open_list)
            while key_node is None:
                f, key_node = heappop(open_list)
        except IndexError:
            break
        else:
            del heap_index[key_node]

        if key_node == finish_node:
            path = [(key_node.x, key_node.y)]
            while key_node.parent is not None:
                key_node = key_node.parent
                path.append((key_node.x, key_node.y))
            return path

        key_node.is_closed = 1

        for neighbor in get_surrounding(key_node):
            try:
                node = node_hash[neighbor]
            except KeyError:
                node = factory(neighbor)
                if node:
                    node_hash[neighbor] = node
                    score = key_node.g + dist(key_node, node)
                    node.parent = key_node
                    node.g = score
                    node.h = calc_h(node, finish_node)
                    entry = [node.g + node.h, node]
                    heap_index[node] = entry
                    heappush(open_list, entry)
            else:
                if not node.is_closed:
                    score = key_node.g + dist(key_node, node)
                    if score < node.g:
                        node.parent = key_node
                        node.g = score
                        entry = heap_index.pop(node)
                        entry[1] = None
                        new_entry = [node.g + node.h, node]
                        heap_index[node] = new_entry
                        heappush(open_list, new_entry)

    return []


def search_test(tests=1000):
    area = [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]

    def factory(p):
        x, y = p
        if x < 0 or y < 0:
            return None

        try:
            if area[y][x] == 0:
                node = Node((x, y))
                return node
            else:
                return None
        except IndexError:
            return None

    return search((0, 0), (5, 9), factory)


if __name__ == "__main__":
    print(search_test())

