"""
In a holiday party, if each attendee can only gift to one other,
this might help.
"""

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

    # NOTE: dict is insertion-ordered for Python 3.6+ so usage of
    #       OrderedDict here is for Python<=3.5 compatibility.
    return OrderedDict(zip(names, choices))


# NOTE: Simple profiling with test case indicated that this is 4-5x faster.
def lazy_select(names, seed=None):
    """
    Only shuffle once. But using this, when there are
    more than 2 names, a combo like ``A->C`` and ``C->A``
    cannot happen simultaneously.
    """
    if seed is not None:
        random.seed(seed)

    choices = random.sample(names, k=len(names))
    matches = dict(zip(choices, [choices[-1]] + choices[:-1]))

    # Insist on sorting by input order.
    return OrderedDict([(name, matches[name]) for name in names])


def test_select():
    d = select(['Frodo', 'Sam', 'Merry', 'Pippins'], seed=1234)
    assert d['Frodo'] == 'Merry'
    assert d['Sam'] == 'Frodo'
    assert d['Merry'] == 'Pippins'
    assert d['Pippins'] == 'Sam'


def test_lazy_select():
    d = lazy_select(['Frodo', 'Sam', 'Merry', 'Pippins'], seed=1234)
    assert d['Frodo'] == 'Pippins'
    assert d['Sam'] == 'Merry'
    assert d['Merry'] == 'Frodo'
    assert d['Pippins'] == 'Sam'
