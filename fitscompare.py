"""Multi-extension FITS image comparisons.

Examples
--------
>>> from fitscompare import imcalc

Subtract im2.fits from im1.fits:

>>> imcalc('im1.fits', 'im2.fits', 'diff.fits')

Divide im1.fits by im2.fits:

>>> imcalc('im1.fits', 'im2.fits', 'diff.fits', op='/')

"""
# STDLIB
import logging
import os

# THIRD-PARTY
import pyfits


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'

module_logger = logging.getLogger('fitscompare')


def imcalc(image1, image2, out_im, op='-'):
    """Compute difference or ratio between 2 FITS images.

    Each output extension stores the result of the
    corresponding input extension.

    Data format must be::

        0. Primary header
        1. Data
        2. Data
        ...
        N. Data

    Parameters
    ----------
    image1, image2 : string
        Input FITS images.

    out_im : string
        Output FITS image.

    op : {'-', '/'}
        Supports the following operations:
            * '-' = image1 - image2 (default)
            * '/' = image1 / image2

    """
    min_ext = 2

    pf_1 = pyfits.open(image1)
    pf_2 = pyfits.open(image2)

    next_1 = len(pf_1)
    next_2 = len(pf_2)

    # Inputs must have at least 1 primary header and 1 data ext
    if next_1 < min_ext:
        pf_1.close()
        pf_2.close()
        raise ValueError('image1 has {} ext but expect >={}.'.format(
            next_1, min_ext))

    # Inputs must have same number of extensions
    if next_1 != next_2:
        pf_1.close()
        pf_2.close()
        raise ValueError('image1 has {} ext but image2 has {}.'.format(
            next_1, next_2))

    out_phdr = pyfits.PrimaryHDU()
    out_phdr.header.add_history('IMAGE1 {}'.format(os.path.basename(image1)))
    out_phdr.header.add_history('IMAGE2 {}'.format(os.path.basename(image2)))
    out_phdr.header.add_history('IMAGE1 {} IMAGE2'.format(op))

    out_hdu  = pyfits.HDUList([out_phdr])

    for i in xrange(1, next_1):
        data_1 = pf_1[i].data
        data_2 = pf_2[i].data

        if data_1 is None or data_2 is None:
            module_logger.warn('input(s) has NoneType data.')
            hdu = pyfits.ImageHDU()

        else:
            if data_1.dtype != data_2.dtype:
                module_logger.warn(
                    'In ext {}, image1 is {} but image2 is {}'.format(
                    i, data_1.dtype, data_2.dtype))

            if op == '/':
                out_data = data_1 / data_2
            else:
                out_data = data_1 - data_2

            hdu = pyfits.ImageHDU(out_data)

        # Inherit EXTNAME and EXTVER from image1
        hdu.update_ext_name(pf_1[i].name)
        hdu.update_ext_version(pf_1[i]._extver)

        out_hdu.append(hdu)

    out_hdu.writeto(out_im, clobber=True)

    pf_1.close()
    pf_2.close()
