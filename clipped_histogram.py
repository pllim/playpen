"""Calculates mean and standard deviation of clipped distribution.

Examples
--------
>>> import clipped_histogram
>>> clipped_histogram.test()

References
----------
http://www.roe.ac.uk/~rsc/wsa/Epy_Wsa/wsatools.Statistics-pysrc.html#clippedHistogram

"""
# THIRD-PARTY
import numpy as np


def clippedHistogram(xx, clip=0, Niter=10, imean=0.0, isd=0.0):
    """
    Parameters
    ----------
    xx : array
        Input array.

    clip : float, optional
        Clipping sigma.

    Niter : int
        Number of iterations.

    imean, isd : float
        Initial mean and sigma to use at the start of clipping.

    Returns
    -------
    mean, sd : float
        Clipped mean and sigma.

    """
    xx = np.array(xx)

    if xx.size < 2:
        return 0.0, 0.0

    if clip == 0.0:
        mean = xx.mean()
        sd = xx.std()
    else:
        not_test = True
        it = 0

        if imean == 0.0 and isd == 0.0:
            mean = xx.mean()
            sd = xx.std()
        else:
            mean, sd = imean, isd

        while not_test and it < Niter:
            meanold, sdold = mean, sd
            minV = mean - clip * sd
            maxV = mean + clip * sd
            xx_mask = xx[(xx >= minV) & (xx <= maxV)]
            mean = xx_mask.mean()
            sd = xx_mask.std()
            if mean == meanold and sd == sdold:
                not_test = False
            it += 1

    return mean, sd


def test():
    import matplotlib.pyplot as plt

    xx = np.random.normal(0, 0.1, 1000)
    mean, sd = clippedHistogram(xx, clip=3.0)

    print 'Orig mean, sig =', xx.mean(), xx.std()
    print 'Clipped mean, sig =', mean, sd

    plt.hist(xx.ravel())

    plt.axvline(mean, color='r', ls='-')
    plt.axvline(sd, color='r', ls='--')
    plt.axvline(-sd, color='r', ls='--')

    plt.draw()
