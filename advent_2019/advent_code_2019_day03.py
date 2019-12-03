import operator


def manhattan_distance(p, q):
    return sum(map(abs, map(operator.sub, p, q)))


def path_to_coord(path_list):
    coord_list = []
    origin = (0, 0)  # y, x

    for path in path_list:
        direction = path[0]
        length = int(path[1:])

        if direction == 'U':  # y+
            for i in range(1, length + 1):
                coord_list.append((origin[0] + i, origin[1]))
            origin = coord_list[-1]
        elif direction == 'D':  # y-
            for i in range(1, length + 1):
                coord_list.append((origin[0] - i, origin[1]))
            origin = coord_list[-1]
        elif direction == 'R':  # x+
            for i in range(1, length + 1):
                coord_list.append((origin[0], origin[1] + i))
            origin = coord_list[-1]
        elif direction == 'L':  # x-
            for i in range(1, length + 1):
                coord_list.append((origin[0], origin[1] - i))
            origin = coord_list[-1]
        else:
            raise ValueError(f'Invalid direction={direction}')

    return coord_list


def min_wires_distance(paths_wire1, paths_wire2):
    origin = (0, 0)
    c1 = set(path_to_coord(paths_wire1))
    c2 = set(path_to_coord(paths_wire2))
    intersections = c1 & c2
    min_dist = 1e6  # Arbitrarily large number

    for c in intersections:
        dist = manhattan_distance(origin, c)
        if dist < min_dist:
            min_dist = dist

    return min_dist


def main_part1(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    wire1 = lines[0].split()[0].split(',')
    wire2 = lines[1].split()[0].split(',')
    return min_wires_distance(wire1, wire2)


def main_part2(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    wire1 = lines[0].split()[0].split(',')
    wire2 = lines[1].split()[0].split(',')
    c1 = path_to_coord(wire1)
    c2 = path_to_coord(wire2)
    intersections = set(c1) & set(c2)
    min_steps = 1e6  # Arbitrarily large number
    for c in intersections:
        n_steps = c1.index(c) + c2.index(c) + 2
        if n_steps < min_steps:
            min_steps = n_steps
    return min_steps


if __name__ == '__main__':
    # Part 1
    # print(main_part1('wires.txt'))

    # Part 2
    print(main_part2('wires.txt'))
