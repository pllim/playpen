from collections import defaultdict


def insert_nodes(node_list):
    orbits = defaultdict(list)
    for node in node_list:
        x = node.split(')')
        if len(x) != 2:
            raise ValueError(f'Invalid orbit=f{node}')
        parent, child = x
        orbits[parent].append(child)
    return orbits


def orbits_from_file(filename):
    node_list = []
    with open(filename) as fin:
        for line in fin:
            node_list.append(line[:-1])
    return insert_nodes(node_list)


def _do_count(orbits, parent, depth):
    children = orbits[parent]
    n = len(children)
    # print(parent, n, depth, children)
    for child in children:
        n += depth + _do_count(orbits, child, depth + 1)
    return n


def count_orbits(filename):
    orbits = orbits_from_file(filename)
    return _do_count(orbits, 'COM', 0)


def find_parent(orbits, child):
    parent = None
    for key in orbits:
        if child in orbits[key]:
            parent = key
            break
    return parent


def get_path(orbits, end, start='COM'):
    path = [start]
    children = orbits[start]
    if end in children:
        return path
    for child in children:
        pp = get_path(orbits, end, start=child)
        if pp is not None:
            return path + pp


def count_orbit_transfers(filename, start='YOU', end='SAN'):
    orbits = orbits_from_file(filename)
    path1 = get_path(orbits, start)
    path2 = get_path(orbits, end)
    for p in path1[::-1]:
        if p in path2:
            common_parent = p
            break
    i1 = path1.index(common_parent)
    i2 = path2.index(common_parent)
    return (len(path1) - i1 - 1) + (len(path2) - i2 - 1)


if __name__ == '__main__':
    # Part 1
    # print(count_orbits('orbits.txt'))

    # Part 2
    print(count_orbit_transfers('orbits.txt'))
