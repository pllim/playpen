"""
Python implementation of IRAF `blkavg` task.

Examples
--------
>>> import blkavg_rewrite
>>> blkavg_rewrite.test()

"""

from __future__ import division

import numpy as np
from numpy.lib.stride_tricks import as_strided


def blkavg2d(in_arr, blockshape):
    """
    Simple block average on 2-D array.

    .. notes::

        #. This is the slow version.
        #. Only works when array is even divided by block size.

    Parameters
    ----------
    in_arr: array_like
        2-D input array.

    blockshape: tuple of int
        Blocking factors for Y and X.

    Returns
    -------
    out_arr: array_like
       Block averaged array with smaller size.

    TODO
    ----
    Perry Greenfield: To avoid loops, can use Numpy + filter
    and then only take certain pix from filtered array as
    final result.

    """
    yblock, xblock = blockshape

    # Calculate new dimensions
    x_bin = in_arr.shape[1] / xblock
    y_bin = in_arr.shape[0] / yblock
    out_arr = np.zeros((y_bin,x_bin))

    # Average each block
    for j, y1 in enumerate(range(0, in_arr.shape[0], yblock)):
        y2 = y1 + yblock
        for i, x1 in enumerate(range(0, in_arr.shape[1], xblock)):
            x2 = x1 + xblock
            out_arr[j, i] = in_arr[y1:y2, x1:x2].mean()

    return out_arr


# Written by Erik Bray using codes from
# https://svn.stsci.edu/trac/ssb/stsci_python/browser/stsci.image/branches/blkavg-rewrite/stsci/image/_image.py


def blkavg(array, blockshape):
     blocks = blockview(array, blockshape)
     axes = range(len(blocks.shape) - 1,
                  len(blocks.shape) - len(array.shape) - 1, -1)
     means = np.apply_over_axes(np.mean, blocks, axes)
     # Drop the extra dimensions
     return means.reshape(blocks.shape[:len(array.shape)])[:-1, :-1]


def blockview(array, blocks):
    if len(blocks) < len(array.shape):
        # Extend the block list so that any dimensions not explicitly given are
        # 1 by default
        blocks = blocks + ((1,) * (len(array.shape) - len(blocks)))
    elif len(blocks) > len(array.shape):
        raise ValueError('more blocks specified than dimensions in the '
                         'input array')

    original_shape = array.shape
    expanded_shape = tuple(a + b - (a % b)
                           for a, b in zip(original_shape, blocks))
    if expanded_shape != original_shape:
        # We have to make a new expanded array that can be evenly divided by
        # the block size.  The expanded array has NaNs on the borders and will
        # be returned as a masked array
        new_array = np.empty(expanded_shape)
        new_array.fill(np.nan)
        new_array[tuple(slice(dim) for dim in original_shape)] = array
        array = new_array

    # Number of blocks in each axis
    nblocks = tuple(array.shape[n] / blocks[n] for n in range(len(blocks)))

    shape = nblocks + blocks
    strides = (tuple(array.strides[n] * blocks[n]
               for n in range(len(blocks))) + array.strides)

    blocked = as_strided(array, shape, strides)

    if original_shape != expanded_shape:
        return np.ma.masked_invalid(blocked)
    else:
        return blocked


def test():
    import matplotlib.pyplot as plt
    import time

    naxis1 = 2070
    naxis2 = 2046
    blockshape = (6, 6)

    a = np.arange(naxis1 * naxis2).reshape(naxis2, naxis1)

    t1 = time.time()
    b = blkavg(a, blockshape)
    t2 = time.time()
    print 'blkavg took {} s'.format(t2 - t1)

    t1 = time.time()
    c = blkavg2d(a, blockshape)
    t2 = time.time()
    print 'blkavg2d took {} s'.format(t2 - t1)

    np.testing.assert_array_almost_equal(c, b)

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.imshow(a)
    ax1.set_title('Original')

    ax2.imshow(b)
    ax2.set_title('Block averaged by {}x{}'.format(*blockshape))

    plt.draw()
