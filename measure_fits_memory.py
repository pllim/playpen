"""Profile memory usage of different kinds of data structure.
My results as follow.

FITS with memory mapping:

Line #    Mem usage    Increment   Line Contents
================================================
     9     44.2 MiB     44.2 MiB   @profile
    10                             def measure_fits_memory(memmap):
    11                                 ...
    12     44.5 MiB      0.2 MiB       with fits.open(filename, memmap=memmap) as hdul:
    13    220.6 MiB      0.0 MiB           for hdu in hdul:
    14    220.6 MiB      0.0 MiB               if hdu.data is None:
    15     44.5 MiB      0.0 MiB                   continue
    16    220.6 MiB      0.0 MiB               data = hdu.data
    17    220.6 MiB     64.0 MiB               test = data + 1  # noqa
    18    220.6 MiB      0.0 MiB               del data
    19    220.6 MiB      0.1 MiB               gc.collect()
    20    220.6 MiB      0.0 MiB           del hdu
    21     60.6 MiB      0.0 MiB           gc.collect()
    22     60.6 MiB      0.0 MiB       del hdul
    23     60.6 MiB      0.0 MiB       gc.collect()

FITS without memory mapping:

Line #    Mem usage    Increment   Line Contents
================================================
    80     44.2 MiB     44.2 MiB   @profile
    81                             def measure_fits_memory(memmap):
    82                                 ...
    83     44.4 MiB      0.2 MiB       with fits.open(filename, memmap=memmap) as hdul:
    84    220.6 MiB      0.0 MiB           for hdu in hdul:
    85    236.6 MiB     32.1 MiB               if hdu.data is None:
    86     44.4 MiB      0.0 MiB                   continue
    87    236.6 MiB      0.0 MiB               data = hdu.data
    88    220.6 MiB     31.9 MiB               test = data + 1  # noqa
    89    220.6 MiB      0.0 MiB               del data
    90    220.6 MiB      0.1 MiB               gc.collect()
    91    220.6 MiB      0.0 MiB           del hdu
    92    220.6 MiB      0.0 MiB           gc.collect()
    93     76.6 MiB      0.0 MiB       del hdul
    94     76.6 MiB      0.0 MiB       gc.collect()

Numpy array:

Line #    Mem usage    Increment   Line Contents
================================================
    96     44.3 MiB     44.3 MiB   @profile
    97                             def measure_ndarray():
    98                                 ...
    99     51.7 MiB      7.4 MiB       a = np.arange(1_000_000).reshape((1000, 1000))
   100     59.5 MiB      7.7 MiB       b = a + 1  # noqa
   101     52.0 MiB      0.0 MiB       del b
   102     44.3 MiB      0.0 MiB       del a
   103     44.3 MiB      0.0 MiB       gc.collect()

Python list:

Line #    Mem usage    Increment   Line Contents
================================================
   106     44.3 MiB     44.3 MiB   @profile
   107                             def measure_pyarray():
   108                                 ...
   109     51.8 MiB      7.5 MiB       a = [1] * (10 ** 6)
   110    204.4 MiB    152.6 MiB       b = [2] * (2 * 10 ** 7)
   111     51.9 MiB      0.0 MiB       del b
   112     44.3 MiB      0.0 MiB       del a
   113     44.3 MiB      0.0 MiB       gc.collect()

"""
import gc
import numpy as np
from astropy.io import fits
from memory_profiler import profile

filename = 'your_fits_file.fits'  # noqa


@profile
def measure_fits_memory(memmap):
    """FITS with and without memory mapping."""
    with fits.open(filename, memmap=memmap) as hdul:
        for hdu in hdul:
            if hdu.data is None:
                continue
            data = hdu.data
            test = data + 1  # noqa
            del data
            gc.collect()
        del hdu
        gc.collect()
    del hdul
    gc.collect()


@profile
def measure_ndarray():
    """Pure Numpy arrays."""
    a = np.arange(1_000_000).reshape((1000, 1000))
    b = a + 1  # noqa
    del b
    del a
    gc.collect()


@profile
def measure_pyarray():
    """Memory profiler example. No Numpy."""
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    del a
    gc.collect()


if __name__ == '__main__':
    measure_fits_memory(True)
    #measure_fits_memory(False)
    #measure_ndarray()
    #measure_pyarray()
