from __future__ import division, print_function

import numpy as np
import pytest

__all__ = ['MazeRunner']


class Node(object):
    """
    Node in the maze.

    Parameters
    ----------
    coord : tuple of int
        ``(y, x)`` 0-indexed coordinate of the node.

    path : list
        A list of ``(y, x)`` 0-indexed coordinates
        of the path taken since the start up to this node.

    """
    def __init__(self, coord, predecessors=[]):
        self.coord = coord
        self.predecessors = predecessors


class MazeRunner(object):
    """
    Class to handle maze.

    Parameters
    ----------
    maze : array_like
        2D array consisting of 0 (path) and 1 (wall).

    """
    PATH = 0

    def __init__(self, maze):
        self.maze = np.asarray(maze)
        self.ny, self.nx = self.maze.shape

    def shortest_path(self, start_pt, end_pt):
        """
        Find shortest path in the given maze from
        starting point to ending point.

        Parameters
        ----------
        start_pt, end_pt : tuple of int
            ``(y, x)`` 0-indexed coordinates of starting
            and ending points.

        Returns
        -------
        shortest_path : list
            List of ``(y, x)`` 0-indexed coordinates of
            the shortest path.

        """
        q = [Node(start_pt)]  # Breadth-first search queue

        while len(q) > 0:
            cur_node = q.pop(0)
            if cur_node.coord != end_pt:
                q += self._find_connected_paths(cur_node)
            else:  # Found
                return cur_node.predecessors + [cur_node.coord]

        return []

    def _find_connected_paths(self, node):
        """Find connected paths for a given point in maze."""
        y, x = node.coord
        paths = []

        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            y2 = y + dy
            x2 = x + dx
            if y2 < 0 or x2 < 0 or y2 >= self.ny or x2 >= self.nx:  # Outside
                continue
            if (y2, x2) in node.predecessors:  # Only go forward
                continue
            if self.maze[y2, x2] != self.PATH:  # A wall
                continue
            p = node.predecessors + [node.coord]
            paths.append(Node((y2, x2), predecessors=p))

        return paths


@pytest.mark.parametrize(
    ('maze', 'start', 'end', 'answer'),
    [([[0, 0, 0, 0],
       [0, 1, 0, 1],
       [0, 1, 0, 0],
       [0, 1, 1, 1]], (2, 0), (2, 2),
      [(2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]),
     ([[0, 1, 0],
       [0, 1, 0],
       [1, 1, 1]], (1, 0), (1, 2), []),
     ([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0]], (1, 1), (1, 2), [(1, 1), (1, 2)]),
     ([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0]], (1, 1), (2, 2), [(1, 1), (2, 1), (2, 2)])])
def test_maze(maze, start, end, answer):
    """Test the :class:`MazeRunner`."""
    m = MazeRunner(maze)
    shortest_path = m.shortest_path(start, end)
    assert shortest_path == answer
