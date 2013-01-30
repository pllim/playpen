"""Example of coordinate matching two catalogs.

Brief outline:
    #. Read RA and DEC from the catalogs.
    #. Convert to X and Y using `pywcs` and a FITS file.
    #. Construct a `scipy.spatial.KDTree` of the coordinates from the
       first catalog.
    #. Query the tree for the nearest neighbor from the second catalog.

"""
# THIRD-PARTY
from astropy import io
from astropy import wcs as pywcs
from scipy.spatial import cKDTree as KDTree


__author__ = 'Harry Ferguson'
__organization__ = 'Space Telescope Science Institute'


def match(s, h, fits_image, tolerance=4):
    """
    Parameters
    ----------
    s, h : obj
        Catalog objects. Each must have `ra` and `dec` attributes
        as 1-D Numpy arrays.

    fits_image : string
        FITS image for conversion of RA,DEC to X,Y.

    tolerance : number
        Match tolerance in pixels.

    Returns
    -------
    xmatch, ymatch
        Matched X,Y from first catalog.

    xhmatch, yhmatch
        Matched X,Y from second catalog.

    """
    # Now use pywcs to put these on some sort of projection. I think as
    # long as you use the same for both data sets it's not really important
    # what the projection is. In my case I read in a fits image associated
    # with the first catalog and use that header info.
    hdu = io.fits.open(fits_image)
    wcs = pywcs.WCS(hdu['PRIMARY'].header)

    # Convert sky to x,y positions
    x, y = wcs.wcs_world2pix(s.ra, s.dec, 0)
    xh, yh = wcs.wcs_world2pix(h.ra, h.dec, 0)

    # Create a KD Tree
    tree = KDTree(zip(x.ravel(), y.ravel()))

    # Search it for the nearest neighbor
    # d = distance of the nearest neighbor
    # i = index in x,y arrays of the nearest neighbor for each source in xh,yh
    d, i = tree.query(zip(xh.ravel(), yh.ravel()), k=1)

    # Give me just the matchers within a tolerance
    j = d < tolerance
    ii = i[j]  # match within N pixels; tricker to do this in ra,dec
    xmatch, ymatch = x[ii], y[ii]
    xhmatch, yhmatch = xh[j], yh[j]

    return xmatch, ymatch, xhmatch, yhmatch
