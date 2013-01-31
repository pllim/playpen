"""Simpler version of `PSF_GAUSSIAN` in IDL.

Examples
--------
>>> from psf_gaussian import gauss2d
>>> import matplotlib.pyplot as plt
>>> psf = gauss2d(50, 2.5)
>>> plt.imshow(psf, cmap=plt.cm.gray)

"""

# THIRD-PARTY
import numpy as np


def gauss2d(npix, fwhm, normalize=True):
    """
    Parameters
    ----------
    npix : int
        Number of pixels for each dimension.
        Just one number to make all sizes equal.

    fwhm : float
        FWHM (pixels) in each dimension.
        Single number to make all the same.

    normalize : bool, optional
        Normalized so total PSF is 1.

    Returns
    -------
    psf : array_like
        Gaussian point spread function.

    """
    # Initialize PSF params
    cntrd = (npix - 1.0) * 0.5
    st_dev = 0.5 * fwhm / np.sqrt(2.0 * np.log(2))

    # Make PSF (Rene Breton 2011-10-20)
    # https://groups.google.com/group/astropy-dev/browse_thread/thread/5ee6cd662236e382
    x, y = np.indices([npix, npix]) - (npix - 1) * 0.5
    psf = np.exp(-0.5 * ((x**2 + y**2) / st_dev**2))

    # Normalize
    if normalize:
        psf /= psf.sum()

    return psf
