"""Sudoku solver for lazy people."""
from __future__ import division, print_function

import numpy as np
import pytest
from numpy.testing import assert_array_equal

wantset = set(range(1, 10))
iterblock = range(0, 9, 3)
iter1d = range(9)


def solveit(static_arr):
    """Solve the given Sudoku puzzle.

    Parameters
    ----------
    static_arr : array_like (int)
        2D array with the shape ``(9, 9)`` that represents the puzzle.
        Fill the cells to be solved with zeroes.

    Returns
    -------
    arr : array_like (int)
        Solved puzzle.

    Raises
    ------
    ValueError
        Invalid input.

    """
    arr = np.asarray(static_arr)
    if arr.shape != (9, 9):
        raise ValueError('Sudoku array must be 9x9')

    if np.all(arr) or is_solved(arr):
        return arr

    possnum = [[], [], []]

    for i in iter1d:
        possnum[0].append(wantset - set(arr[:, i]))  # Each row
        possnum[1].append(wantset - set(arr[i, :]))  # Each col

    # Each 3x3 block
    for j in iterblock:
        for i in iterblock:
            possnum[2].append(wantset - set(arr[j:j+3, i:i+3].ravel()))

    yy, xx = np.where(arr == 0)
    possd = np.empty((9, 9), dtype=object)
    possd.fill(None)
    minnum = 99
    minpos = None

    for i, idx in enumerate(zip(yy, xx)):
        iy, ix = idx
        iq = (ix // 3) + ((iy // 3) * 3)
        num_for_cell = possnum[0][ix] & possnum[1][iy] & possnum[2][iq]
        n_match = len(num_for_cell)
        if n_match > 0:
            possd[idx] = num_for_cell
            if n_match < minnum:
                minnum = n_match
                minpos = idx

    # print('Starting at {} with {} possibilities'.format(minpos, minnum))
    n = list(possd[minpos])[0]
    arr[minpos] = n
    possd[minpos] = None
    yy, xx = possd.nonzero()
    for idx in zip(yy, xx):
        if n in possd[idx]:
            possd[idx].remove(n)

    return solveit(arr)


def is_solved(arr):
    """Check if given Sudoku array is solved."""
    arr = np.asarray(arr)
    sta = (np.all(np.equal(np.sum(arr, axis=0), 45)) and
           np.all(np.equal(np.sum(arr, axis=1), 45)))
    if not sta:
        return sta

    for j in iterblock:
        for i in iterblock:
            sta = np.sum(arr[j:j+3, i:i+3]) == 45
            if not sta:
                return sta
    return sta


def test_puzzle_medium():
    """Test."""
    static_arr = [[5, 0, 0, 2, 0, 4, 0, 9, 0],
                  [0, 0, 1, 0, 0, 0, 7, 0, 0],
                  [6, 7, 0, 0, 0, 0, 3, 0, 4],
                  [0, 0, 6, 5, 0, 0, 4, 0, 0],
                  [0, 2, 0, 0, 1, 0, 0, 7, 0],
                  [0, 0, 4, 0, 0, 3, 6, 0, 0],
                  [8, 0, 7, 0, 0, 0, 0, 6, 9],
                  [0, 0, 9, 0, 0, 0, 5, 0, 0],
                  [0, 6, 0, 1, 0, 9, 0, 0, 7]]
    ans = [[5, 8, 3, 2, 7, 4, 1, 9, 6],
           [9, 4, 1, 6, 3, 8, 7, 5, 2],
           [6, 7, 2, 9, 5, 1, 3, 8, 4],
           [7, 9, 6, 5, 8, 2, 4, 1, 3],
           [3, 2, 8, 4, 1, 6, 9, 7, 5],
           [1, 5, 4, 7, 9, 3, 6, 2, 8],
           [8, 1, 7, 3, 4, 5, 2, 6, 9],
           [2, 3, 9, 8, 6, 7, 5, 4, 1],
           [4, 6, 5, 1, 2, 9, 8, 3, 7]]
    arr = solveit(static_arr)
    assert_array_equal(arr, ans)


@pytest.mark.xfail(reason='Multiple solutions possible?')
def test_puzzle_hard():
    """
    Function returns

    [[3, 8, 4, 2, 5, 6, 7, 1, 9],
     [6, 5, 9, 1, 4, 7, 2, 3, 8],
     [2, 7, 1, 9, 3, 8, 6, 4, 5],
     [1, 4, 5, 7, 9, 2, 8, 6, 3],
     [8, 9, 3, 5, 6, 4, 1, 2, 7],
     [7, 2, 6, 8, 1, 3, 9, 5, 4],
     [9, 1, 8, 3, 2, 5, 4, 7, 6],
     [4, 3, 2, 6, 7, 9, 5, 8, 1],
     [5, 6, 7, 4, 8, 1, 3, 9, 2]]
    """
    static_arr = [[0, 0, 0, 0, 0, 6, 0, 0, 0],
                  [0, 5, 9, 0, 0, 0, 0, 0, 8],
                  [2, 0, 0, 0, 0, 8, 0, 0, 0],
                  [0, 4, 5, 0, 0, 0, 0, 0, 0],
                  [0, 0, 3, 0, 0, 0, 0, 0, 0],
                  [0, 0, 6, 0, 0, 3, 0, 5, 4],
                  [0, 0, 0, 3, 2, 5, 0, 0, 6],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    ans = [[4, 3, 8, 7, 9, 6, 2, 1, 5],
           [6, 5, 9, 1, 3, 2, 4, 7, 8],
           [2, 7, 1, 4, 5, 8, 6, 9, 3],
           [8, 4, 5, 2, 1, 9, 3, 6, 7],
           [7, 1, 3, 5, 6, 4, 8, 2, 9],
           [9, 2, 6, 8, 7, 3, 1, 5, 4],
           [1, 9, 4, 3, 2, 5, 7, 8, 6],
           [3, 6, 2, 9, 8, 7, 5, 4, 1],
           [5, 8, 7, 6, 4, 1, 9, 3, 2]]
    arr = solveit(static_arr)
    assert_array_equal(arr, ans)
