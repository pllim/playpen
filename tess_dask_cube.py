import glob
import os
import time

import dask.array as da
import numpy as np
from astropy.io import fits


# https://zenodo.org/record/1244673
class DelayedIO:
    def __init__(self, filename, shape, dtype):
        self.filename = filename
        self.shape = shape
        self.ndim = len(self.shape)
        self.dtype = dtype

    def __getitem__(self, slc):
        with fits.open(self.filename, memmap=True) as hdul:
            return hdul[1].data[slc]


# Have to provide array info manually because peeking at the first file
# to grab that info results in MemoryError from Dask later.
def assimilate_cube(dirname, cubename, filepattern='*ffic.fits', ext=1,
                    data_shape=(2078, 2136), data_dtype=np.float32,
                    verbose=True):
    t_start = time.time()
    filenames = sorted(glob.glob(os.path.join(dirname, filepattern)))
    naxis3 = len(filenames)

    if naxis3 == 0:
        raise ValueError('No files found')

    ny, nx = data_shape

    # meta and name are given for increased performance in Dask.
    meta = np.zeros((0, ), dtype=data_dtype)
    da_arr = da.stack([da.from_array(DelayedIO(f, data_shape, data_dtype),
                                     name=f, chunks=(ny, nx), meta=meta)
                       for f in filenames])
    t_start_comp = time.time()
    np_arr = da_arr.compute()  # Need: ulimit -n <num files or more>
    t_end_comp = time.time()
    hdu = fits.PrimaryHDU(np_arr.reshape((1, naxis3, ny, nx)))
    hdu.writeto(cubename)
    t_end = time.time()

    # Local timing was as follows:
    # Compute took 172.0s (2.9 mins)
    # Total run took 291.8s (4.8 mins)
    if verbose:  # Rough wall time of expensive compute
        print(f'Compute took {t_end_comp - t_start_comp:.1f}s')
        print(f'Total run took {t_end - t_start:.1f}s')


if __name__ == '__main__':
    assimilate_cube('s0001_1_1', 'tess-s0001-1-1-correct-cube.fits')
