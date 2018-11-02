import random
from collections import OrderedDict

import numpy as np


def select(names, seed=None, max_iter=100, verbose=False):
    """
    Given a list of names, randomly select one for the
    other for gifting purpose.
    """
    if seed is not None:
        random.seed(seed)

    i = 0
    n = len(names)
    arr = np.asarray(names)
    choices = np.asarray(random.sample(names, k=n))
    found = not np.any(choices == arr)

    if verbose:
        print(i, choices)

    while not found and i < max_iter:
        choices = np.asarray(random.sample(names, k=n))
        found = not np.any(choices == arr)
        i += 1

        if verbose:
            print(i, choices)

    if not found:
        raise ValueError('Unable to find match after '
                         '{} tries'.format(max_iter))

    return OrderedDict(zip(names, choices))


def test_select():
    d = select(['Frodo', 'Sam', 'Merry', 'Pippins'], seed=1234)
    assert d['Frodo'] == 'Merry'
    assert d['Sam'] == 'Frodo'
    assert d['Merry'] == 'Pippins'
    assert d['Pippins'] == 'Sam'
