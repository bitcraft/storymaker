from heapq import heappush, heappop, heappushpop


#diagonals allowed
def get_surrounding(node):
    return ((node[0]-1, node[1]-1), (node[0], node[1]-1), (node[0]+1, node[1]-1),
            (node[0]-1, node[1]),   (node[0]+1, node[1]),
            (node[0]-1, node[1]+1), (node[0], node[1]+1), (node[0]+1, node[1]+1))


def dist(start, finish):
    return abs(finish[0] - start[0]) + abs(finish[1] - start[1])


def clip(coords, lowest, highest):
    for v in coords:
        if lowest[0] <= v[0] <= highest[0] and lowest[1] <= v[1] <= highest[1]:
            yield v


def calc_h(start, finish):
    return abs(finish[0] - start[0]) + abs(finish[1] - finish[1])


def search(start, finish, low, high):
    """
    perform basic a* search on a 2d map.
    """
    heap = []
    open_list = set()
    closed_list = set()
    parent = {}
    g = {}
    heap_index = {}

    pushback = (0, start)
    g[start] = 0
    open_list.add(start)

    while heap or pushback:
        if pushback:
            f, node = heappushpop(heap, pushback)
            pushback = None
        else:
            f, node = heappop(heap)
        if node == finish:
            path = [node]
            while parent.get(node, None) is not None:
                node = parent[node]
                path.append(node)
            return path
        open_list.remove(node)
        closed_list.add(node)
        for neighbor in clip(get_surrounding(node), low, high):
            if neighbor in closed_list:
                continue
            _g = g[node] + dist(node, neighbor)
            if neighbor not in open_list or _g < g[neighbor]:
                parent[neighbor] = node
                g[neighbor] = _g
                _f = _g + calc_h(neighbor, finish)
                if neighbor in open_list:
                    heap.remove(heap_index[neighbor])
                    entry = (_f, neighbor)
                    heap_index[neighbor] = entry
                    if pushback:
                        heappush(heap, pushback)
                    pushback = entry
                else:
                    open_list.add(neighbor)
                    entry = (_f, neighbor)
                    heap_index[neighbor] = entry
                    if pushback:
                        heappush(heap, pushback)
                    pushback = entry
    return []


def test():
    return search((0, 0), (5, 9), (0, 0), (10, 10))


if __name__ == '__main__':
    import timeit

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

    # 1.53 non pushback
    # 1.50 pushback...small improvement
    print(test())
    print(min(timeit.repeat("test()", number=10000, setup="from __main__ import test")))

