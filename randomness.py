import numpy as np


def find_seeds(prob_range=(0.5, 0.55), seed_range=(0, 1000)):
    """
    Find seeds where :func:`numpy.random.rand` would
    return probability within the given range.

    Parameters
    ----------
    prob_range : tuple of float
        Range of desired probabilities in the form of
        ``[min, max)``. Limit is ``[0, 1)``.

    seed_range : tuple of int
        Range of seeds to search in the form of
        ``[min, max)``.

    Returns
    -------
    good_seeds : dict
        Map of seeds that would generate desired randomness
        to their respective results.

    """
    good_seeds = {}

    for seed in range(*seed_range):
        s = np.random.RandomState(seed)
        x = s.rand()
        if x >= prob_range[0] and x < prob_range[1]:
            good_seeds[seed] = x

    return good_seeds
