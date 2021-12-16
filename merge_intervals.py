import numpy as np
import pytest


def merge_intervals(all_intervals):
    """Given a list of intervals, merge the overlapping ones
    and return merged intervals.

    Parameters
    ----------
    all_intervals : list of tuple of int
        List of ``(min, max)`` intervals.
        Assumption: ``max >= min``

    Returns
    -------
    merged_intervals : list of tuple of int
        List of ``(min, max)`` of merged intervals.

    """
    if len(all_intervals) == 0:
        return []

    all_intervals = sorted(all_intervals)
    flat_intervals = np.asarray(all_intervals).ravel()
    decisions = (flat_intervals[1:] - flat_intervals[:-1])[1::2]
    merged_intervals = [list(all_intervals[0])]
    i = 1

    while i < len(all_intervals):
        if decisions[i - 1] <= 0:
            merged_intervals[-1][1] = all_intervals[i][1]
        else:
            merged_intervals.append(list(all_intervals[i]))
        i += 1

    return list(map(tuple, merged_intervals))


@pytest.mark.parametrize(
    ('inlist', 'ans'),
    [([(4, 8), (6, 10), (11, 12), (15, 20), (20, 25)],
      [(4, 10), (11, 12), (15, 25)]),
     ([(20, 25), (4, 8), (11, 12), (6, 10), (15, 20)],
      [(4, 10), (11, 12), (15, 25)]),
     ([(0, 0), (0, 0)], [(0, 0)]),
     ([(-1, 0), (0, 2), (1, 4)], [(-1, 4)]),
     ([(2, 4), (8, 9), (1, 1)], [(1, 1), (2, 4), (8, 9)]),
     ([], [])])
def test_merge_intervals(inlist, ans):
    assert merge_intervals(inlist) == ans
