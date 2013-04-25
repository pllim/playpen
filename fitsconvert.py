"""Unconventional FITS manipulation."""

# THIRD-PARTY
from astropy.io import fits


def remove_pixvalue(infits, outfits):
    """Convert ``PIXVALUE`` to real extension.

    CFITSIO (used by CALXXX) writes out null extension when
    it is a constant array. This is useful to conserve
    disk space. Instead the data is stored in its header
    using special keywords like ``PIXVALUE`` and ``NPIX*``.

    Subsequent processing on such extension causes confusion
    when used with `pyfits` (as of v3.2.dev), IRAF ``catfits``,
    and DS9. Situation arises where the data is no longer a
    constant array but the special keywords are still present,
    causing the extension to erroneously be interpreted still
    as a constant array.

    To fix this, this function:

        * Removes ``PIXVALUE``, ``NPIX*``, and ``NAXIS`` entries.
        * Repopulates ``NAXIS*`` keywords with actual data values.

    .. note:: RAW data with real NULL extensions are unaffected.

    Parameters
    ----------
    infits : str
        Input FITS file to fix.

    outfits : str
        Output FITS file. Existing file is overwritten.

    Examples
    --------
    >>> from fitsconvert import remove_pixvalue
    >>> remove_pixvalue('jc4b11ouq_flt.fits', 'jc4b11ouq_flt_fixed.fits')

    """
    with fits.open(infits) as pf_in:
        for ext in pf_in:
            if 'PIXVALUE' in ext.header and ext.data is not None:
                del ext.header['PIXVALUE']
                del ext.header['NPIX1']
                del ext.header['NPIX2']
                del ext.header['NAXIS']
                ext.header['NAXIS'] = ext.data.ndim
                ext.header['NAXIS1'] = ext.data.shape[1]
                ext.header['NAXIS2'] = ext.data.shape[0]

        pf_in.writeto(outfits, clobber=True)
