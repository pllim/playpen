"""Unconventional FITS manipulation."""

# THIRD-PARTY
import numpy as np
from astropy.io import fits


def fill_empty_ext(infits, outfits, kw='PIXVALUE'):
    """Fill empty ERR and DQ extensions with PIXVALUE.

    CALXXX writes out null arrays on ERR and DQ when
    they are all constant. This is useful to conserve
    disk space. Instead their header has PIXVALUE
    keyword with that constant.

    But this also causes subsequent manual processing
    on those extensions to fail. The workaround is to
    fill the empty extension(s) with PIXVALUE in the shape
    of SCI extension(s).

    Parameters
    ----------
    infits : str
        Input FITS file with empty extension(s).
        SCI cannot be empty and must appear before
        corresponding ERR and DQ.

    outfits : str
        Output FITS file with empty extensions filled
        with zeros. Existing file is overwritten.

    kw : str
        Keyword containing PIXVALUE constant to
        populate extension with.

    Examples
    --------
    >>> from fitsconvert import fill_empty_ext
    >>> fill_empty_ext('jc4b11ouq_flt.fits', 'jc4b11ouq_flt_filled.fits')

    """
    out_shape = ()

    with fits.open(infits) as pf_in:
        for ext in pf_in:
            if ext.name == 'SCI':
                out_shape = ext.shape
            elif ext.name == 'ERR' and ext.shape == ():
                ext.data = np.zeros(out_shape, dtype='float32') + ext.header[kw]
            elif ext.name == 'DQ' and ext.shape == ():
                ext.data = np.zeros(out_shape, dtype='int16') + ext.header[kw]

        pf_in.writeto(outfits, clobber=True)
