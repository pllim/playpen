"""
CDBS FITS verification.

Requires
--------
#. CDBS `fitsverify`
#. CDBS `certify`

"""
# STDLIB
import os
import subprocess

# THIRD-PARTY
import pyfits


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def is_fits(fitsFile):
    """
    Run CDBS `fitsverify` and extract success code.
    Also run `pyfits.verify` that will throw Exception on failure.

    .. note::

        Special setup needed to run `fitsverify`.
        Instructions available from CDBS.

    Parameters
    ----------
    fitsFile: string
        FITS image to verify.

    Returns
    -------
    isFits: bool
        `True` if ok.

    Raises
    ------
    Exception
        On some verification failure.

    """
    isFits = False

    # ----- PYFITS VERIFY -----
    # Exception on failure. Else nothing happens.
    with pyfits.open(fitsFile) as pf:
        pf.verify(option='exception')

    # ----- CDBS FITSVERIFY -----
    # If no error, returns 0:
    #     Verification found 0 warning(s) and 0 error(s).
    # Else, returns 1:
    #     Abort Verification: Fatal Error.
    s = subprocess.check_output(['fitsverify', fitsFile])
    if 'FAIL' not in s:
        isFits = True

    return isFits


def pass_certify(fitsFile):
    """
    Run CDBS `certify` and extract success code.

    .. note::

        Special SETENV required. Contact CDBS.

    Parameters
    ----------
    fitsFile: string
        FITS image to certify.

    Returns
    -------
    isPassed: bool
        `True` if ok.

    """
    isPassed = False

    # If no error, returns 0:
    #     == Checking xxx.fits ==
    #     (blank line)
    # Else, returns 1:
    #     == Checking xxx.fits ==
    #     (one error on each line)
    s = subprocess.call(['certify', fitsFile])
    if s == 0:
        isPassed = True

    return isPassed
