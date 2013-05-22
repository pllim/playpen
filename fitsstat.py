"""Functions for FITS image stats and display.

Examples
--------
>>> import fitsstat

Print all *CORR* header values in *raw.fits primary header:

>>> fitsstat.pretty_hdr('*raw.fits', 'CORR')

Calculate statistics for SCI and ERR, and save to file:

>>> with open('stat.log', 'w') as fout:
...     fitsstat.imstat('im.fits', extname=('SCI','ERR'), fout=fout)

Plot histograms for ext=('sci',1) for 2 images between 0.1 and 10.0 counts:

>>> fitsstat.imhist('im1.fits', 'im2.fits', z1=0.1, z2=10.0)

"""
from __future__ import print_function, division

# STDLIB
import glob
import os
import sys

# THIRD-PARTY
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits as pyfits


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def pretty_hdr(files_str, hdr_str, ext='PRIMARY', fout=sys.stdout):
    """Print header keywords and values to screen.

    Values will be truncated to match column widths.
    This is for quick check only.

    Parameters
    ----------
    files_str : string
        File(s) to print. Can have wildcards.

    hdr_str : string
        Header keyword(s) to print.
        No need for wildcards. Partial match will yield result.
        Use first image as template to get pretty table.

    ext : int or string or tuple
        FITS extension.

    fout : output stream
        Print info to screen by default.

    """
    all_im = glob.glob(files_str)
    assert len(all_im) > 0, 'No files found.'

    line = '{:15s} '.format('IMAGE')

    im = all_im[0]
    all_keys = []
    for key in pyfits.getheader(im, ext):
        if hdr_str in key:
            all_keys.append(key)
            line += '{:10s} '.format(key[:10])

    fout.write(line[:-1] + '\n')

    for im in all_im:
        im_hdr = pyfits.getheader(im, ext)

        line = '{:15s} '.format(os.path.basename(im[:15]))

        for key in all_keys:
            if key in im_hdr:
                val = str(im_hdr[key])
            else:
                val = '--'

            line += '{:10s} '.format(val[:10])

        fout.write(line[:-1] + '\n')


def imstat(image1, extname_filter=None, extver_filter=None, fout=sys.stdout):
    """Compute image statistics for each extension.

    Parameters
    ----------
    image1 : string
        Input FITS image.

    extname_filter : list of string
        Only consider EXTNAME listed here.
        Case sensitive.

    extver_filter : list of int
        Only consider EXTVER listed here.

    fout : output stream
        Print info to screen by default.

    """
    im_name = os.path.basename(image1)

    fout.write(
        '{:9s} {:7s} {:3s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s}\n'.format(
        'IMAGE', 'EXTNAME', 'VER', 'NPIX', 'MEAN', 'STDDEV', 'MIN', 'MAX'))

    with pyfits.open(image1) as pf:
        for ext in pf:
            imdata = ext.data
            im_extname = ext.name
            im_extver = ext._extver

            if ((imdata is not None) and
                    (extname_filter is None or im_extname in extname_filter) and
                    (extver_filter is None or im_extver in extver_filter)):
                im_npix = imdata.size
                im_mean = imdata.mean()
                stddev = imdata.std()
                im_min = imdata.min().astype('float')
                im_max = imdata.max().astype('float')

                fout.write('{:9s} {:7s} {:3d} {:10d} {:10.3E} {:10.3E} '
                           '{:10.3E} {:10.3E}\n'.format(
                    im_name[:9], im_extname[:7], im_extver, im_npix, im_mean,
                    stddev, im_min, im_max))


def imhist(*args, **kwargs):
    """Display histogram of FITS image.

    If multiple images are given, all histograms appear in the same plot.

    +-----------+-------------------------------------------------------+
    | Keyword   | Explanation                                           |
    +-----------+-------------------------------------------------------+
    |ext        | Extension ID as accepted by PyFITS. Default is SCI,1. |
    +-----------+-------------------------------------------------------+
    |bins       | Number of bins in histogram. Default is 512.          |
    +-----------+-------------------------------------------------------+
    |z1         | Lower limit of data to consider. Default is min.      |
    +-----------+-------------------------------------------------------+
    |z2         | Upper limit of data to consider. Default is max.      |
    +-----------+-------------------------------------------------------+
    |log        | Plot Y in log scale. Default is False.                |
    +-----------+-------------------------------------------------------+
    |legend_loc | Legend loc as accepted by Matplotlib. Default is best.|
    +-----------+-------------------------------------------------------+
    |save_plot  | Save plot in given file name. Default is None.        |
    +-----------+-------------------------------------------------------+
    |show_plot  | Show plot on screen. Default is True.                 |
    +-----------+-------------------------------------------------------+

    Parameters
    ----------
    *args:
        FITS image(s).

    **kwargs:
        Keywords as defined in the table above.

    """
    assert len(args) > 0, 'No input image given.'

    ext  = kwargs.get('ext', ('SCI',1))
    bins = kwargs.get('bins', 512)
    log  = kwargs.get('log', False)

    min_z1 =  999999
    max_z2 = -999999

    fig, ax = plt.subplots()

    for image1 in args:
        im_name = os.path.basename(image1)
        im_data = pyfits.getdata(image1, ext)

        z1 = kwargs.get('z1', im_data.min())
        z2 = kwargs.get('z2', im_data.max())

        min_z1 = min(min_z1, z1)
        max_z2 = max(max_z2, z2)

        mask = np.where((im_data >= z1) & (im_data <= z2))
        assert len(mask[0]) > 0, '{} has no data within [{}, {}]'.format(
            im_name, z1, z2)

        ax.hist(im_data[mask], bins=bins, histtype='step', log=log,
                label=im_name)

    ax.set_xlim(min_z1, max_z2)

    if log:
        ax.set_ylim(ymin=1)

    ax.set_xlabel('Pixel values')
    ax.set_ylabel('# Pixels')
    ax.set_title('EXT = {}'.format(ext))
    ax.legend(loc=kwargs.get('legend_loc', 'best'))

    plt.draw()

    if kwargs.get('save_plot', None):
        plt.savefig(save_plot)

    if not kwargs.get('show_plot', True):
        plt.close()


def has_nan(image, verbose=True):
    """Check for invalid numbers in FITS image data.
    Extensions with no data (e.g., primary header) are skipped.

    Parameters
    ----------
    image : str
        FITS image name.

    verbose : bool, optional
        Print information to screen.

    Returns
    -------
    status : bool
        True if any of the data extensions has nan or inf, else False.

    Examples
    --------
    This file has nan values in EXT 5:

    >>> has_nan('/grp/hst/cdbs/jref/tam17023j_drk.fits')
    /grp/hst/cdbs/jref/tam17023j_drk.fits EXT (ERR,2)
        nan/inf found at
        IRAF X,Y =   1312,   189
        IRAF X,Y =   1312,   190
        IRAF X,Y =   1312,   191
        IRAF X,Y =   1312,   192
        IRAF X,Y =   1312,   193
        IRAF X,Y =   1312,   194
        IRAF X,Y =   1312,   195
        IRAF X,Y =   1312,   196
        IRAF X,Y =   1312,   197
        IRAF X,Y =   1312,   198
        IRAF X,Y =   1312,   199
        IRAF X,Y =   2589,   367
        IRAF X,Y =   1057,   830
        IRAF X,Y =   1057,  1116
        IRAF X,Y =   1457,  1754
    True

    This file does not have nan or inf in all data extensions:

    >>> has_nan('/grp/hst/cdbs/jref/tam17023j_drk.fits')
    /grp/hst/cdbs/jref/tam17023j_drk.fits OK
    False

    """
    status = found = False
    with pyfits.open(image) as pf:
        for ext in pf:
            if ext.data is not None:
                mask = ~np.isfinite(ext.data)
                found = np.any(mask)
            if found:
                if not status:
                    status = found
                if verbose:
                    print('{0} EXT ({1},{2})'.format(
                            image, ext.name, ext._extver))
                    print('    nan/inf found at')
                    for y, x in zip(*np.where(mask)):
                        print('    IRAF X,Y = {0:6d},{1:6d}'.format(x+1, y+1))
                else:
                    break
    if not status and verbose:
        print(image, 'OK')
    return status
