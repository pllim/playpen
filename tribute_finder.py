"""Pick a tribute to run a meeting or whatever."""

import random
from collections import Counter


def pick_tribute(population, previous_tributes, seed=None):
    """Pick a tribute. May the odds be ever in your favor.

    Parameters
    ----------
    population : list
        List of all the choices to choose from.

    previous_tributes : list
        List of previous tributes to be considered.
        Duplicates are allowed. In fact, the more duplicates are detected
        for a choice, the lower the chance that choice is picked.

    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    tribute
        Selected tribute from ``population``.

    """
    population = list(set(population))  # Ensure uniqueness
    c = Counter(previous_tributes)
    max_weight = len(population)

    if max_weight == 0:
        raise ValueError('Empty population')

    weights = [max_weight if c[name] == 0 else 1 / c[name]
               for name in population]

    if seed is not None:
        random.seed(seed)

    # NOTE: k > 1 can return duplicate, so just return one
    return random.choices(population, weights=weights)[0]


def test_pick_tribute():
    population = ['Robb Stark', 'Jon Snow', 'Sansa Stark', 'Arya Stark',
                  'Bran Stark', 'Rickon Stark', 'Theon Greyjoy']
    # Arya Stark should be the least likely, followed by Robb Stark,
    # then Jon/Theon. Dolores left. The rest is fair game.
    previous_tributes = ['Robb Stark', 'Jon Snow', 'Robb Stark',
                         'Arya Stark', 'Theon Greyjoy', 'Arya Stark',
                         'Arya Stark', 'Dolores']
    assert pick_tribute(population, previous_tributes, seed=1234) == 'Sansa Stark'  # noqa
    assert pick_tribute(population, previous_tributes, seed=4321) == 'Bran Stark'  # noqa
