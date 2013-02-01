"""WFPC2 related functions."""
from __future__ import division, print_function

# STDLIB
import math


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'

GAIN = {'7': {'1': 7.12, '2': 7.12, '3': 6.9, '4': 7.10},
        '15': {'1': 13.99, '2': 14.5, '3': 13.95, '4': 13.95}}

RDNS = {'7': {'1': 5.24, '2': 5.51, '3': 5.22, '4': 5.19},
        '15': {'1': 7.02, '2': 7.84, '3': 6.99, '4': 8.32}}


def get_rdns_gain(g, c):
    """
    Determine WFPC2 readnoise and actual gain based
    on ``ATODGAIN`` and ``CHIP``.

    Parameters
    ----------
    g : {'7', '15'}
        ``ATODGAIN`` keyword value.

    c : {'1', '2', '3', '4'}
        ``CHIP`` keyword value.

    Returns
    -------
    rdns : float
        Readnoise (e).

    gain : float
        Actual gain (e/DN).

    Examples
    --------
    >>> from wfpc2_tools import get_rdns_gain
    >>> get_rdns_gain('7', '4')
    (5.19, 7.1)

    """
    return RDNS[g][c], GAIN[g][c]


def dolphin_cte(xcen, ycen, in_flux, in_sky, gain, mjd,
                n_image=1, verbose=True, cte_ver='may2009'):
    """Calculate CTE correction for WFPC2 with Dolphin formula.

    Parameters
    ----------
    xcen, ycen : int
        X and Y coordinates of the object.

    in_flux : float
        Measured counts in DN for 0.5 arcsec aperture.

    in_sky : float
        Measured sky value in DN.

    gain : float
        Actual gain of the CCD in electrons/DN.

    mjd : float
        Modified Julian Date of the exposure.
        Usually taken from EXPSTART in the image header.

    n_image : int, optional
        The number of exposures used prior to flux measurement.
        `in_flux` and `in_sky` are divided by this number
        prior to CTE calculations.

    verbose : bool, optional
        Print extra information.

    cte_ver : {'dec2004', 'may2009'}
        Version of Dolphin's formula to use.

    Returns
    -------
    m_cte : float
      CTE correction to be ADDED to the uncorrected magnitude.

    f_cte : float
      CTE correction to be MULTIPLIED to the uncorrected counts.

    Examples
    --------
    >>> from wfpc2_tools import dolphin_cte
    >>> dolphin_cte(400.0, 450.0, 20.0, 1.5, 6.9, 53333.4)
    (-0.34921579486399745, 1.3793876011556538)
    >>> dolphin_cte(400.0, 450.0, 20.0, 1.5, 6.9, 53333.4, n_image=2)
    (-0.5747569566067925, 1.6978635410640832)
    >>> dolphin_cte(400.0, 450.0, 20.0, 1.5, 6.9, 53333.4, cte_ver='dec2004')
    (-0.3850557437373997, 1.4256807888544563)

    References
    ----------
    http://purcell.as.arizona.edu/wfpc2_calib/

    """
    m_cte, f_cte = 0.0, 1.0

    # Check coordinate values. WFPC2 CCD is 800x800.
    ccd_min, ccd_max = 1, 800
    assert xcen >= ccd_min and xcen <= ccd_max, 'xcen is out of bounds'
    assert ycen >= ccd_min and ycen <= ccd_max, 'ycen is out of bounds'

    # For combined images from 2 exposures, flux and background
    # are halved for CTE calc (J. Biretta).
    # Converted to electrons prior to CTE calculations.
    msky_cte = in_sky  * gain / n_image
    flux_cte = in_flux * gain / n_image

    # ---------------
    # CTE Correction on 0.5" aperture.
    # DOLPHIN WEBSITE, May 13, 2009.
    # ---------------

    if cte_ver == 'dec2004':
        # Calculate the following variable values.
        mm = math.sqrt(msky_cte**2.0 + 1.0)
        bg = mm - 10.0
        lbg = math.log(mm) - 1.0
        yr = (mjd - 50193.0) / 365.25

        # Correct for the CTE loss in X readout (mag).
        xcte = 0.0021 * math.exp(-0.234 * bg) * xcen / 800.0

        # Recalculate lct.
        lct = math.log(flux_cte) - 7.0 + 0.921 * xcte

        # Correct for the CTE loss in Y readout (mag).
        c1 = (0.0114 *
              (0.670 * math.exp(-0.246*lbg) + 0.330 * math.exp(-0.0359*bg)) *
              (1.0 + 0.335 * yr - 0.0074 * yr * yr) * ycen / 800.0)
        c2 = 3.55 * math.exp(-0.474 * lct)
        ycte = math.log(math.exp(c1) * (1 + c2) - c2) / 0.436

    else:
        cte_ver = 'may2009'

        # Calculate the following variable values.
        lbg = math.log(math.sqrt(msky_cte**2.0 + 1.0)) - 1.0
        yr = (mjd - 49461.9) / 365.25

        # Correct for the CTE loss in X readout (mag).
        xcte = 0.0077 * 10.0**(-0.50 * lbg) * (1.0 + 0.10 * yr) * xcen / 800.0

        # Calculate lct.
        lct = math.log(flux_cte) + 0.921 * xcte - 7.0

        # Correct for the CTE loss in Y readout (mag).
        c1 = max(1.0 - 0.201 * lbg + 0.039 * lbg * lct + 0.002 * lct, 0.15)
        c2 = 0.96 * (yr - 0.0255 * yr * yr) * math.exp(-0.450 * lct)
        ycte = 2.41 * math.log(
            math.exp(0.02239 * c1 * ycen / 800.0) * (1 + c2) - c2)

    # Calculate final corrections
    m_cte = -(xcte + ycte)
    f_cte = 10**(-0.4 * m_cte)

    # Print info to screen
    if verbose:
        print('\n***************************\n'
              'WFPC2 CTE VERSION: {}\n'
              'X, Y: {}, {}\n'
              'Uncorrected counts (DN): {}\n'
              'Sky value (DN): {}\n'
              'Gain (e-/DN): {}\n'
              'MJD: {:E}\n'
              'N_IMAGE: {}\n\n'
              'CTE CORRECTION: {:+.3f} mag, x{:.3f} counts\n'
              '***************************\n'.format(
            cte_ver, xcen, ycen, in_flux, in_sky, gain, mjd,
            n_image, m_cte, f_cte))

    return m_cte, f_cte
