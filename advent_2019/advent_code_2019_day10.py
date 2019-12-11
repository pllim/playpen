import math
import warnings
from collections import defaultdict

import numpy as np


def read_asteroid_file(filename):
    with open(filename) as fin:
        all_lines = fin.readlines()

    ny = len(all_lines)
    nx = len(all_lines[0].split()[0])
    mask = np.zeros((ny, nx), dtype=bool)  # True = asteroid

    for iy, line in enumerate(all_lines):
        row = line.split()[0]
        for ix, char in enumerate(row):
            if char == '#':
                mask[iy, ix] = True

    return mask


def calc_m_c(p1, p2):
    """Properties of a straight line."""
    y1, x1 = p1
    y2, x2 = p2
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')  # Ignore inf slope
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
    if ~np.isfinite(m):
        m = 'inf'
    if ~np.isfinite(c):
        c = 'inf'
    return m, c


# TODO: delete?
def _in_line_of_sight(m, c, orig, loc):
    y, x = loc
    if np.isfinite(m):
        y_fit = m * x + c
        if y == y_fit:
            ans = True
        else:
            ans = False
    else:  # Vertical line
        if x == orig[1]:
            ans = True
        else:
            ans = False
    return ans


def get_quadrant(station_loc, loc):
    """
    Origin on upper left:
    1 | 2
    --+--
    3 | 4
    """
    y0, x0 = station_loc
    y1, x1 = loc
    if y1 <= y0:
        if x1 < x0:
            quad = 1
        else:
            quad = 2
    else:
        if x1 < x0:
            quad = 3
        else:
            quad = 4
    return quad


def get_angle(station_loc, loc, debug=False):
    quad = get_quadrant(station_loc, loc)
    y0, x0 = station_loc
    y1, x1 = loc
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    hyp = math.sqrt((dx * dx) + (dy * dy))
    if quad == 2:
        angle = 90 - math.acos(dx / hyp) * 180 / math.pi  # deg
    elif quad == 4:
        angle = math.asin(dy / hyp) * 180 / math.pi + 90  # deg
    elif quad == 3:
        angle = 270 - (math.acos(dy / hyp) * 180 / math.pi)  # deg
    else:
        angle = 270 + math.asin(dy / hyp) * 180 / math.pi  # deg
    if np.allclose(angle, 360):
        angle = 0
    if debug:
        print(f'loc={loc}, quad={quad}, angle={angle}')
    return angle, quad, hyp


def n_detections(station_loc, orig_asteroid_locs):
    asteroid_locs = orig_asteroid_locs.copy()
    asteroid_locs.remove(station_loc)
    mc_by_quad = defaultdict(list)
    for cur_loc in asteroid_locs:
        quad = get_quadrant(station_loc, cur_loc)
        mc_by_quad[quad].append(calc_m_c(station_loc, cur_loc))
    n = 0
    for mc_list in mc_by_quad.values():
        n += len(set(mc_list))
    return n


def array_of_mc(filename, station_loc):
    mask = read_asteroid_file(filename)
    i_asteroids = np.where(mask)
    asteroid_locs = list(zip(*i_asteroids))
    arr = np.zeros(mask.shape, dtype=tuple)
    for loc in asteroid_locs:
        mc = calc_m_c(station_loc, loc)
        arr[loc[0], loc[1]] = mc
    return arr


def part_1(filename):
    mask = read_asteroid_file(filename)
    i_asteroids = np.where(mask)
    checksum = np.zeros(mask.shape)
    asteroid_locs = list(zip(*i_asteroids))  # list of (y, x)
    max_detection = 0
    d = defaultdict(list)
    for station_loc in asteroid_locs:
        n = n_detections(station_loc, asteroid_locs)
        d[n].append(station_loc[::-1])  # They want (x, y)
        checksum[station_loc[0], station_loc[1]] = n
        if n > max_detection:
            max_detection = n
    return d[max_detection], checksum


def part_2(filename, station_loc, debug=True):
    """station_loc is (y, x)

    Clockwise means quadrants 2, 4, 3, 1
    """
    mask = read_asteroid_file(filename)
    i_asteroids = np.where(mask)
    asteroid_locs = list(zip(*i_asteroids))  # list of (y, x)
    asteroid_locs.remove(station_loc)  # Remove self
    loc_by_angle = defaultdict(list)
    for loc in asteroid_locs:
        angle, _, dist = get_angle(station_loc, loc)
        loc_by_angle[angle].append((dist, loc))
    for angle in loc_by_angle:
        loc_by_angle[angle].sort()
    i_count = 0
    i_angle = 0
    all_angles = sorted(loc_by_angle.keys())
    n_angles = len(all_angles)
    n_target = len(asteroid_locs)
    while i_count < n_target:
        if i_angle == n_angles:
            i_angle = 0
        angle = all_angles[i_angle]
        if len(loc_by_angle[angle]) == 0:
            i_angle += 1
            continue
        _, loc = loc_by_angle[angle].pop(0)
        if debug and loc == (2, 8):
            print(f'*** angle={angle} loc={loc}')
        i_count += 1
        i_angle += 1

        if debug:
            if i_count in (1, 2, 3, 10, 20, 50, 100, 199, 200, 201, 299):
                print(f'The {i_count}th asteroid at {loc[1],loc[0]}')
            elif loc in ((2, 8), (0, 16)):
                print(f'{loc[1]},{loc[0]} has i_count={i_count}')
        elif i_count = 202:  # BUG: Off by 2
            print(f'i={i_count} ans={loc[1] * 100 + loc[0]}')
            break


def test_angles():
    station_loc = (3, 8)
    print(get_angle(station_loc, (1, 8)))
    print(get_angle(station_loc, (0, 9)))
    print(get_angle(station_loc, (1, 9)))
    print(get_angle(station_loc, (0, 10)))
    print(get_angle(station_loc, (2, 9)))
    print(get_angle(station_loc, (1, 11)))
    print(get_angle(station_loc, (3, 12)))
    print(get_angle(station_loc, (4, 16)))
    print(get_angle(station_loc, (4, 15)))
    print(get_angle(station_loc, (4, 10)))
    print(get_angle(station_loc, (4, 4)))
    print(get_angle(station_loc, (4, 2)))
    print(get_angle(station_loc, (3, 2)))
    print(get_angle(station_loc, (2, 0)))
    print(get_angle(station_loc, (2, 1)))
    print(get_angle(station_loc, (1, 0)))
    print(get_angle(station_loc, (1, 1)))
    print(get_angle(station_loc, (2, 5)))
    print(get_angle(station_loc, (0, 1)))
    print(get_angle(station_loc, (1, 5)))
    print(get_angle(station_loc, (1, 6)))
    print(get_angle(station_loc, (0, 6)))
    print(get_angle(station_loc, (0, 7)))
    print(get_angle(station_loc, (0, 8)))


if __name__ == '__main__':
    # Debug
    # print(array_of_mc('asteroids_test1.txt', (2, 2)))
    # test_angles()

    # Part 1
    # best_loc, checksum = part_1('asteroids.txt')
    # print(checksum)
    # print(best_loc, checksum.max())

    # Part 2
    # part_2('asteroids_test5.txt', (13, 11), debug=True)
    part_2('asteroids.txt', (19, 11), debug=False)
