"""Simple 2D interpolation.

Examples
--------
>>> import interpolate2d
>>> interpolate2d.example1()

References
----------
http://www.scipy.org/doc/api_docs/SciPy.interpolate.interpolate.interp2d.html

"""

# THIRD-PARTY
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate


def interp2d(x, y, z, outshape, verbose=True, doplot=True):
    """
    Parameters
    ----------
    x, y : int
        X and Y indices of `z`.

    z : float
        Values for given `x` and `y`.

    outshape : tuple of int
        Shape of 2D output array.

    verbose : bool, optional
        Print info to screen.

    doplot : bool, optional
        Plot results.

    Returns
    -------
    im : float array
        2-D array of interpolated data.

    """
    # Print the data to screen for checking
    if verbose:
        print 'DATA USED FOR INTERPOLATION:'
        for i, (xx, yy, zz) in enumerate(zip(x, y, z), start=1):
            print '{}: {} {} {}'.format(i, xx, yy, zz)

    # Perform 2D interpolation
    func = interpolate.interpolate.interp2d(x, y, z)
    im = func(np.mgrid[:outshape[1]], np.mgrid[:outshape[0]])

    if doplot:
        # Get min/max to use same colorbar on for base and overlay
        pmin = im.min()
        pmax = im.max()

        fig, ax = plt.subplots()

        # Show interpolated 2D image
        p = ax.imshow(im, vmin=pmin, vmax=pmax)

        # Overlay data points used for interpolation
        ax.scatter(x, y, s=100, c=z, vmin=pmin, vmax=pmax, marker='s')

        # Display colorbar.
        # Shrink to make it same width as display.
        c = fig.colorbar(p, orientation='horizontal', shrink=0.7)
        c.set_label('Pixel value')

        # Plot labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Interpolated image')

        plt.draw()

    return im


def example1():
    """Call `interp2d` for some fake data."""

    # Scattered data points to be interpolated.
    x = np.array([1, 1, 4, 7])
    y = np.array([7, 1, 5, 2])
    z = np.array([10.5, 3.0, 4.5, 30.0])

    im = interp2d(x, y, z, (8, 10))


if __name__ == '__main__':
    example1()
