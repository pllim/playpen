"""Convert Nora's image to table.

Examples
--------
>>> import im2tab
>>> im2tab.convert('myimagetable.fits', 'nicetable.fits')
Copied the header
Converted 3 columns
nicetable.fits written
>>> from astropy.table import Table
>>> tab = Table.read('nicetable.fits', format='fits')
>>> tab
<Table length=8486>
    DATA    QUALITY     VAR
  float32   float32   float32
----------- ------- -----------
1.44789e+08     8.0 7.50891e+15
1.52335e+08     8.0 7.48747e+15
1.08334e+08     8.0 7.66241e+15
9.42806e+07     8.0 7.62161e+15
7.86007e+07  1032.0 7.45407e+15
9.22977e+07  1032.0 7.33011e+15
        ...     ...         ...
1.14301e+09     8.0 1.30819e+16
1.12099e+09     8.0 1.30816e+16
1.22831e+09     8.0 1.30568e+16
1.20423e+09     8.0 1.28731e+16
1.18228e+09     8.0 1.29867e+16
1.17793e+09     8.0 1.30699e+16
 1.1584e+09     8.0 1.31217e+16

"""
from __future__ import division, print_function

from astropy.io import fits


def convert(inputfile, outputfile, clobber=False, verbose=True):
    """Convert the following format to proper FITS table.

    Input format::

        No.    Name         Type      Cards   Dimensions
        0    PRIMARY     PrimaryHDU     293   ()
        1    DATA        ImageHDU        19   (8486,)
        2    QUALITY     ImageHDU        20   (8486,)
        3    VAR         ImageHDU        19   (8486,)

    Output format::

        No.    Name         Type      Cards   Dimensions
        0    PRIMARY     PrimaryHDU     293   ()
        1                BinTableHDU     14   8486R x 3C   [E, E, E]

    Parameters
    ----------
    inputfile, outputfile : str
        Input and output filenames.

    clobber : bool, optional
        Overwrite existing file.

    verbose : bool, optional
        Print extra info.

    """
    with fits.open(inputfile) as pf:

        # Primary header
        thdulist = fits.HDUList([pf[0]])
        if verbose:
            print('Copied the header')

        # Convert the rest to columns
        cols = [fits.Column(name=pfext.name, format='E', array=pfext.data)
                for pfext in pf[1:]]
        tbhdu = fits.BinTableHDU.from_columns(cols)
        thdulist.append(tbhdu)
        if verbose:
            print('Converted {0} columns'.format(len(cols)))

    thdulist.writeto(outputfile, clobber=clobber)

    if verbose:
        print(outputfile, 'written')
