"""Sky fitting.

These functions were ported from IDL codes used by
ACS/WFC reference files generation and statistics.

Examples
--------
>>> import matplotlib.pyplot as plt
>>> import pyfits
>>> import skyfit

Read EXT 1 of ACS/WFC superbias image:

>>> im = pyfits.getdata('x1o1958ej_bia.fits', 1)

Calculate clipped mean for each row and plot it:

>>> x = skyfit.total(im, 1)
>>> plt.plot(x)

Calculate mode and sigma of pixel distribution using
polynomial fitting:

>>> m, s = skyfit.msky(im, do_plot=True, verbose=True, ptitle='bias')

"""
from __future__ import print_function

# STDLIB
import logging

# THIRD-PARTY
import numpy as np
import scipy
from scipy import optimize


__organization__ = 'Space Telescope Science Institute'

module_logger = logging.getLogger('skyfit')


def robust_sigma(in_y, zero=0):
    """
    Calculate a resistant estimate of the dispersion of
    a distribution. For an uncontaminated distribution,
    this is identical to the standard deviation.

    Use the median absolute deviation as the initial
    estimate, then weight points using Tukey Biweight.
    See, for example, Understanding Robust and
    Exploratory Data Analysis, by Hoaglin, Mosteller
    and Tukey, John Wiley and Sons, 1983.

    .. note:: ROBUST_SIGMA routine from IDL ASTROLIB.

    Examples
    --------
    >>> result = robust_sigma(in_y, zero=1)

    Parameters
    ----------
    in_y : array_like
        Vector of quantity for which the dispersion is
        to be calculated

    zero : int
        If set, the dispersion is calculated w.r.t. 0.0
        rather than the central value of the vector. If
        Y is a vector of residuals, this should be set.

    Returns
    -------
    out_val : float
        Dispersion value. If failed, returns -1.

    """
    # Flatten array
    y = in_y.ravel()

    eps = 1.0E-20
    c1 = 0.6745
    c2 = 0.80
    c3 = 6.0
    c4 = 5.0
    c_err = -1.0
    min_points = 3

    if zero:
        y0 = 0.0
    else:
        y0 = np.median(y)

    dy    = y - y0
    del_y = abs( dy )

    # First, the median absolute deviation MAD about the median:

    mad = np.median( del_y ) / c1

    # If the MAD=0, try the MEAN absolute deviation:
    if mad < eps:
        mad = del_y.mean() / c2
    if mad < eps:
        return 0.0

    # Now the biweighted value:
    u  = dy / (c3 * mad)
    uu = u * u
    q  = np.where(uu <= 1.0)
    count = len(q[0])
    if count < min_points:
        module_logger.warn('ROBUST_SIGMA: This distribution is TOO WEIRD! '
                           'Returning {}'.format(c_err))
        return c_err

    numerator = np.sum( (y[q] - y0)**2.0 * (1.0 - uu[q])**4.0 )
    n    = y.size
    den1 = np.sum( (1.0 - uu[q]) * (1.0 - c4 * uu[q]) )
    siggma = n * numerator / ( den1 * (den1 - 1.0) )

    if siggma > 0:
        out_val = np.sqrt( siggma )
    else:
        out_val = 0.0

    return out_val


def meanclip(indata, clipsig=3.0, maxiter=5, converge_num=0.02, verbose=False):
    """
    Computes an iteratively sigma-clipped mean on a
    data set. Clipping is done about median, but mean
    is returned.

    .. note:: MYMEANCLIP routine from ACS library.

    Examples
    --------
    >>> mean, sigma = meanclip(indata)

    Parameters
    ----------
    indata : array_like
        Input data.

    clipsig : float
        Number of sigma at which to clip.

    maxiter : int
        Ceiling on number of clipping iterations.

    converge_num : float
        If the proportion of rejected pixels is less than
        this fraction, the iterations stop.

    verbose : bool
        Print messages to screen?

    Returns
    -------
    mean : float
        N-sigma clipped mean.

    sigma : float
        Standard deviation of remaining pixels.

    """
    # Flatten array
    skpix = indata.ravel()

    ct = indata.size
    iter = 0
    c1 = 1.0
    c2 = 0.0

    while (c1 >= c2) and (iter < maxiter):
        lastct = ct
        medval = np.median(skpix)
        sig = skpix.std().astype(np.float64)  # Bug - Need to recast
        wsm = np.where( abs(skpix - medval) < (clipsig * sig) )
        ct = len(wsm[0])
        if ct > 0:
            skpix = skpix[wsm]

        c1 = abs(ct - lastct)
        c2 = converge_num * lastct
        iter += 1

    mean  = skpix.mean()
    sigma = robust_sigma(skpix)

    if verbose:
        print('MEANCLIP: {:.1f}-sigma clipped mean\n'
              'MEANCLIP: Mean computed in {} iterations\n'
              'MEANCLIP: Mean = {:.6f}, sigma = {:.6f}'.format(
            clipsig, iter, mean, sigma))

    return mean, sigma


def total(inarray, axis, type='meanclip'):
    """
    Collapse 2-D array in one dimension.

    .. note:: MYTOTAL routine from ACS library.

    Examples
    --------
    >>> collapsed_array = total(inarray, 1, type='median')

    Parameters
    ----------
    inarray : array_like
        Input 2-D array.

    axis : {1, 2}
        Axis to collapse.
            * 1 - Return values along Y.
            * 2 - Return values along X.

    type : {'median', 'meanclip', 'stdev'}
        Algorithm to use.

    Returns
    -------
    out_arr : array_like
        1-D array collapsed along desired axis with desired
        algorithm.

    """
    out_arr = 0.0

    # Check inarray
    if inarray.ndim != 2:
        module_logger.warn('TOTAL: Input array must be 2D')
        return out_arr

    # Check axis
    if axis == 1:
        n_out = inarray.shape[0]
    elif axis == 2:
        n_out = inarray.shape[1]
    else:
        module_logger.warn('TOTAL: Axis not supported - {}'.format(axis))
        return out_arr

    # Check type
    if type not in ('median', 'meanclip', 'stdev'):
        module_logger.warn('TOTAL: Type not supported - {}'.format(type))
        return out_arr

    # Initialize output array
    out_arr = np.zeros(n_out)
    out_rng = range(n_out)

    if type == 'meanclip':
        for i in out_rng:
            if axis == 1:
                im_i = inarray[i,:]
            else:
                im_i = inarray[:,i]
            mmean, msigma = meanclip(im_i, maxiter=10, converge_num=0.001)
            out_arr[i] = mmean

    elif type == 'stdev':
        for i in out_rng:
            if axis == 1:
                im_i = inarray[i,:]
            else:
                im_i = inarray[:,i]
            mmean, msigma = meanclip(im_i, maxiter=10, converge_num=0.001)
            out_arr[i] = msigma

    elif type == 'median':
        for i in out_rng:
            if axis == 1:
                im_i = inarray[i,:]
            else:
                im_i = inarray[:,i]
            out_arr[i] = np.median(im_i)

    return out_arr


def gaussian(height, center_x, width_x):
    """
    Returns a gaussian function with the given parameters.
    This is used for least square fitting optimization.

    .. note:: This is used by `msky`.

    Parameters
    ----------
    height: float
        Peak amplitude.

    center_x: float
        Peak location.

    width_x: float
        Sigma of gaussian curve.

    Returns
    -------
    x: lambda function
        Function used for optimization.

    """
    return lambda x: height * np.exp(-(center_x - x)**2 / (2.0 * width_x**2))


def msky(inarray, do_plot=False, verbose=False, ptitle='', func=0):
    """
    Find modal sky on an array.

    First step is determination of median value and sigma.
    Histogram of the data and fit parabola to the
    logaritmic histogram. The coefficient of the parabola
    are used to get mode and sigma of the sky on the
    assumption that it is well fitted by a gaussian or
    2nd-degree polynomial.

    .. note:: MYSKY5 routine from ACS library.

    Parameters
    ----------
    inarray :  array_like
        Input data.

    do_plot : bool
        Do plot?

    verbose : bool
        Print info to screen?

    ptitle : string
        Title of plot. Only used if plotting is done.

    func : {0, 1}
        Function for fitting:
            * 0 - 2nd degree polynomial
            * 1 - Gaussian

    Returns
    -------
    mmean : float
        Mode of fitted function.

    sigma : float
        Sigma of fitted function.

    """
    nsig = 8.0
    c1 = 2.5  # was 2.8
    c2 = 0.8  # was 1.3

    # Min/max of input array
    arr_min = inarray.min()
    arr_max = inarray.max()

    # Get sigma
    mmean, sigma = meanclip(inarray, clipsig=5.0, maxiter=10, verbose=verbose)
    if sigma <= 0:
        module_logger.warn(
            'MSKY: Weird distribution\n'
            'MEAN:   {}\n'
            'STDDEV: {}\n'
            'MIN:    {}\n'
            'MAX:    {}'.format(mmean, sigma, arr_min, arr_max))
        return mmean, sigma

    # Print info
    if verbose:
        print('\nMSKY input array info\n'
              'MIN: {}\n'
              'MAX: {}'.format(arr_min, arr_max))

    # Flatten input array
    arr_1d = inarray.ravel()

    # Define min and max for the histogram
    x = nsig * sigma
    mmean = np.median(arr_1d)
    minhist = mmean - x
    maxhist = mmean + x
    ufi = inarray[ np.where((inarray > minhist) & (inarray < maxhist)) ]

    # Calculate 25% and 75% percentile to get the interquartile range
    # IRQ = pc75-pc25
    # zenman, A. J. 1991.
    sixd = np.argsort( ufi )
    ndata = ufi.size
    pc25 = ufi[ sixd[0.25 * ndata] ]
    pc75 = ufi[ sixd[0.75 * ndata] ]
    irq = pc75 - pc25
    step = 2.0 * irq * ndata**(-1.0 / 3.0)

    # Calculate number of bins to use
    nbin = round(2 * x / step - 1)

    # Histogram
    # http://www.scipy.org/Tentative_NumPy_Tutorial
    yhist, hbin = np.histogram(arr_1d, range=(minhist, maxhist), bins=nbin)
    xhist = 0.5 * (hbin[1:] + hbin[:-1])

    # Define xmin and xmax for the 2-0rder fit
    x1 = mmean - c1 * sigma
    x2 = mmean + c2 * sigma

    # Select the points beween x1 and x2 for the fit
    w = np.where((xhist > x1) & (xhist < x2) & (yhist > 0))
    count = len(w[0])
    xwg  = xhist[w]
    nywg = yhist[w]
    if count < 2:
        module_logger.warn(
            'MSKY: Singular matrix\n'
            'X[W]: {}\n'
            'NY[W]: {}\n'
            'MEDIAN: {}'.format(xwg, nywg, mmean))
        return mmean, sigma

    # Change to log scale
    yhist = np.log10(yhist)
    iyh   = np.where( ~np.isinf(yhist) )
    xhist = xhist[iyh]
    yhist = yhist[iyh]
    nywg  = np.log10(nywg)

    # Calculate the fit coefficients
    ymax = nywg.max()

    # Gaussian
    # http://www.scipy.org/Cookbook/FittingData
    if func == 1:
        if verbose:
            print('MSKY: Fitting gaussian')

        # Initial guess
        ysum = np.sum(nywg)
        mmean = np.sum(xwg * nywg) / ysum
        sigma = np.sqrt(np.abs(np.sum((xwg - mmean)**2 * nywg)/ ysum))
        params = (ymax, mmean, sigma)

        # Error function to minimize
        errorfunction = lambda p: scipy.ravel(gaussian(*p)(xhist) - yhist)

        # Linear least square fitting
        a_opt, a_success = optimize.leastsq(errorfunction, params)
        ymax  = a_opt[0]
        mmean = a_opt[1]
        sigma = a_opt[2]

        # Fit to entire range
        yall = ymax * np.exp(-(xhist - mmean)**2/(2.0 * sigma**2))

    # 2nd degree polynomial
    else:
        if verbose:
            print('MSKY: Fitting 2nd deg polynomial')

        # Polynomial
        a_opt = np.polyfit(xwg, nywg, 2)
        mmean = -0.5 * a_opt[1] / a_opt[0]
        sigma = np.sqrt(-0.5 / ( a_opt[0] * np.log(10) ) )

        # Fit to entire range
        yall = a_opt[0] * xhist**2 + a_opt[1] * xhist + a_opt[2]

    # Print results
    if verbose:
        print('\nMSKY: Results\n'
              'MODE : {}\n'
              'SIGMA: {}'.format(mmean, sigma))

    # Plot results
    if do_plot:
        import matplotlib.pyplot as plt

        plot_y1 = 0
        plot_y2 = ymax + 0.1

        fig, ax = plt.subplots()

        # Data points
        ax.plot(xhist, yhist, 'ko')

        # Mark fitted region
        ax.plot(xwg, nywg, 'bo')

        # Draw fitted function
        ax.plot(xhist, yall, 'r--')
        ax.axvline(x=mmean, color='r')

        # Plot xmin xmax for the fit
        ax.axvline(x=x1, ymin=0, ymax=0.1, color='b')
        ax.axvline(x=x2, ymin=0, ymax=0.1, color='b')

        # Axis limits and labels
        ax.axis([minhist, maxhist, plot_y1, plot_y2])
        ax.set_xlabel('Pix value')
        ax.set_ylabel('Log num of pix')
        ax.set_title(ptitle)

        plt.draw()

    return mmean, sigma
