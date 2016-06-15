"""Module to replace IRAF's ``ofilt`` sky fitting algorithm."""
from __future__ import absolute_import, division, print_function

# THIRD-PARTY
import numpy as np
from astropy.stats import sigma_clip
from astropy.stats.funcs import gaussian_sigma_to_fwhm
from scipy import signal
from scipy.stats import skew

__all__ = ['fitsky_ofilter']


def fitsky_ofilter(data, k1=3.0, binsize=0.1, losigma=3.0,
                   hisigma=3.0, maxiter=10, hwidth=None, smooth=False,
                   sigclip_sigma=None, sigclip_iters=10):
    """Procedure to fit the peak and width of the histogram using
    repeated convolutions and a triangle function.

    Parameters
    ----------
    data : array-like (float)
        Array of sky pixels.

    k1 : float, optional
        Extent of the histogram in sky sigma.

    binsize : float, optional
        The size of the histogram in sky sigma.

    losigma, hisigma : float, optional
        Upper and lower sigma rejection limits.

    maxiter : int, optional
        Maximum number of rejection cycles.

    hwidth : float or `None`, optional
        Width of histogram.

    smooth : bool, optional
        Smooth the histogram before fitting.

    sigclip_sigma : float or `None`, optional
        The number of standard deviations to use as the clipping limit
        when sigma-clipping the data *before* constructing the histogram.
        If `None`, no clipping is done.

    sigclip_iters : int, optional
        The number of iterations to use when sigma-clipping the data
        *before* constructing the histogram. This is only used if
        ``sigclip_sigma`` is given.

    Returns
    -------
    sky_mode : float
        Computed sky value.

    sky_sigma : float
        Computed sigma of the sky pixels.

    sky_skew : float
        Skew of sky pixels.

    Raises
    ------
    ValueError
        Invalid inputs or calculation failed.

    """
    data = np.asarray(data).flatten()

    # Sigma clipping
    if sigclip_sigma is not None:
        skypix = sigma_clip(data, sigma=sigclip_sigma, iters=sigclip_iters)
        skypix = skypix.data[~skypix.mask]
    else:
        skypix = data

    if skypix.size < 1:
        raise ValueError('No sky pixels provided')

    # Compute a first guess for the parameters.
    sky_zero = skypix.mean()
    dmin = skypix.min()
    dmax = skypix.max()
    sky_sigma = skypix.std()
    sky_skew = skew(skypix)
    sky_mean = max(dmin, min(np.median(skypix), dmax))

    # Compute the width and bin size of histogram.
    if hwidth is None or hwidth <= 0:
        cut = min(sky_mean - dmin, dmax - sky_mean, k1 * sky_sigma)
        hmin = sky_mean - cut
        hmax = sky_mean + cut
        dh = binsize * cut / k1
    else:
        hmin = sky_mean - k1 * hwidth
        hmax = sky_mean + k1 * hwidth
        dh = binsize * hwidth

    # Compute the number of histogram bins and the resolution filter.
    if dh > 0:
        nbins = 2 * int((hmax - sky_mean) / dh)
        dh  = (hmax - hmin) / (nbins - 1)
    else:
        nbins = 1
        dh = 0.0

    # Test for a valid histogram.
    if (nbins < 2 or k1 <= 0 or sky_sigma <= 0 or dh <= 0 or sky_sigma <= dh):
        raise ValueError('Unable to construct histogram')

    # Accumulate the histogram.
    hgm = np.histogram(skypix, bins=nbins, range=(hmin, hmax))[0]

    # Toss out bad data
    skypix = skypix[(skypix >= hmin) & (skypix <= hmax)]

    # Recalculate after initial rejection.
    sky_mean = skypix.mean()
    sky_sigma = skypix.std()
    sky_skew = skew(skypix)

    # Fit the peak of the histogram.
    hist_lo = hmin + 0.5 * dh
    hist_hi = hmax + 0.5 * dh
    center = apmapr((hmin + hmax) * 0.5, hist_lo, hist_hi,
                    1.0, nbins)

    if smooth:
        nker = max(1, int(sky_sigma / dh))
        ker = signal.boxcar(nker)
        shgm = signal.convolve(hgm, ker)
        hgm = signal.convolve(shgm, ker)  # Smoothed twice

    center, iter = aptopt(hgm, center, sky_sigma / dh, maxiter=maxiter)

    if iter < 0:
        raise ValueError('Histogram centering failed, no convergence')

    sky_mode = apmapr(center, 1.0, nbins, hist_lo, hist_hi)
    sky_mode = max(dmin, min(sky_mode, dmax))

    # No need to continue, return results.
    if sky_sigma <= dh or maxiter < 1:
        return sky_mode, sky_sigma, sky_skew

    dhh = (nbins - 1) / (hmax - hmin)

    # Fit the histogram with pixel rejection.
    for i in range(maxiter):
        # Compute new histogram limits.
        locut = sky_mode - losigma * sky_sigma
        hicut = sky_mode + hisigma * sky_sigma

        # Detect and reject the pixels.
        badmask = (skypix < locut) | (skypix > hicut)
        if not np.any(badmask):
            break

        # Remove them from histogram and data.
        ibad_hist = ((skypix[badmask] - hmin) * dhh).astype(np.int)
        hgm[ibad_hist] -= 1
        skypix = skypix[~badmask]
        if skypix.size <= 0:
            raise ValueError(
                'No good sky pixels left (niter={0})'.format(i + 1))

        # Recompute the data limits.
        sky_mean = skypix.mean()
        sky_sigma = skypix.std()
        sky_skew = skew(skypix)

        if sky_sigma <= dh:
            break

        # Refit the sky.
        if smooth:
            nker = max(1, int(sky_sigma / dh))
            ker = signal.boxcar(nker)
            shgm = signal.convolve(hgm, ker)
            hgm = signal.convolve(shgm, ker)  # Smoothed twice

        center, iter = aptopt(hgm, center, sky_sigma / dh, maxiter=maxiter)

        if iter < 0:
            raise ValueError('Histogram centering failed, no convergence')

        sky_mode = apmapr(center, 1.0, nbins, hist_lo, hist_hi)
        sky_mode = max(dmin, min(sky_mode, dmax))

    if sky_sigma <= 0:
        sky_sigma = 0.0
        sky_skew = 0.0

    return sky_mode, sky_sigma, sky_skew


def apmapr(a, a1, a2, b1, b2):
    """Vector linear transformation.

    Map the range of pixel values ``a1, a2`` from ``a``
    into the range ``b1, b2`` into ``b``.
    It is assumed that ``a1 < a2`` and ``b1 < b2``.

    Parameters
    ----------
    a : float
        The value to be mapped.

    a1, a2 : float
        The numbers specifying the input data range.

    b1, b2 : float
        The numbers specifying the output data range.

    Returns
    -------
    b : float
        Mapped value.

    """
    scalar = (b2 - b1) / (a2 - a1)
    return max(b1, min(b2, (a - a1) * scalar + b1))


def ap_tprofder(npix, center, sigma, ampl=1.0):
    """Estimate the approximating triangle function and its derivatives.

    Parameters
    ----------
    npix : int
        Number of elements in output arrays.

    center, sigma : float
        Center and sigma of input Gaussian function.

    ampl : float, optional
        Amplitude.

    Returns
    -------
    data : array-like
        Output data.

    der : array-like
        Derivatives.

    """
    data = np.zeros(npix)
    der = np.zeros(npix)

    x = (np.arange(npix) - center) / (sigma * gaussian_sigma_to_fwhm)
    xabs = np.abs(x)

    mask = xabs <= 1
    data[mask] = ampl * (1 - xabs[mask])
    der[mask] = x[mask] * data[mask]

    return data, der


def apply_sign(x, y):
    """Return the absolute value of ``x`` multiplied by
    the sign (i.e., +1 or -1) of ``y``."""
    if y < 0:
        fac = -1.0
    else:
        fac = 1.0
    return abs(x) * fac


def apqzero(x, y, qtol=0.125):
    """Return the root of a quadratic function defined by three points."""
    if len(x) != 3 or len(y) != 3:
        raise ValueError('This function only accepts 3 points')

    # Compute the determinant.
    x2 = x[1] - x[0]
    x3 = x[2] - x[0]
    y2 = y[1] - y[0]
    y3 = y[2] - y[0]
    det = x2 * x3 * (x2 - x3)

    # Compute the shift in x.
    if abs(det) > 0:
        a = (x3 * y2 - x2 * y3) / det
        b = -(x3 * x3 * y2 - x2 * x2 * y3) / det
        c =  a * y[0] / (b * b)
        if abs(c) > qtol:
            dx = (-b / (2.0 * a)) * (1.0 - np.sqrt(1.0 - 4.0 * c))
        else:
            dx = -(y[0] / b) * (1.0 + c)
    elif abs(y3) > 0:
        dx = -y[0] * x3 / y3
    else:
        dx = 0.0

    return dx


def aptopt(data, center, sigma, maxiter=10, tol=0.001, max_search=3):
    """One-dimensional centering routine using repeated convolutions to
    locate image center.

    Parameters
    ----------
    data : array-like
        Initial data.

    center : float
        Initial guess at center.

    sigma : float
        Sigma of Gaussian.

    maxiter : int, optional
        Maximum number of iterations.

    tol : float, optional
        Gap tolerance for sigma.

    max_search : int, optional
        Max initial search steps.

    Returns
    -------
    result : float
        Calculated center.

    niter : int
        Number of iterations used.

    """
    if sigma <= 0:
        return np.nan, -1

    # Initialize.
    wgt = ap_tprofder(data.size, center, sigma)[1]
    s = np.zeros(3)
    s[0] = np.dot(wgt, data)
    if s[0] == 0:
        return center, 0

    x = np.zeros(3)
    x[0] = center
    s[2] = s[0]

    # Search for the correct interval.
    i = 0
    while (i < max_search) and (s[2] * s[0] >= 0):
        s[2] = s[0]
        x[2] = x[0]
        x[0] = x[2] + apply_sign(sigma, s[2])
        wgt = ap_tprofder(data.size, x[0], sigma)[1]
        s[0] = np.dot(wgt, data)

        if s[0] == 0:
            return x[0], 0

        i += 1

    # Location not bracketed.
    if s[2] * s[0] > 0:
        return np.nan, -1

    # Intialize the quadratic search.
    delx = x[0] - x[2]
    x[1] = x[2] - s[2] * delx / (s[0] - s[2])
    wgt = ap_tprofder(data.size, x[1], sigma)[1]
    s[1] = np.dot(wgt, data)
    if s[1] == 0:
        return x[1], 1

    # Search quadratically.
    for niter in range(1, maxiter):

        # Check for completion.
        if s[1] == 0 or np.any(abs(x[1:] - x[:-1]) <= tol):
            break

        # Compute new intermediate value.
        newx = x[0] + apqzero(x, s)
        wgt = ap_tprofder(data.size, newx, sigma)[1]
        news = np.dot(wgt, data)

        if s[0] * s[1] > 0:
            s[0] = s[1]
            x[0] = x[1]
            s[1] = news
            x[1] = newx
        else:
            s[2] = s[1]
            x[2] = x[1]
            s[1] = news
            x[1] = newx

    return x[1], niter + 1
