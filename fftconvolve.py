"""FFT convolution for 2D arrays.

Examples
--------
>>> import fftconvolve
>>> fftconvolve.test()

References
----------
http://www.rzuser.uni-heidelberg.de/~ge6/Programing/convolution.html

"""
# THIRD-PARTY
import numpy as np
from numpy.fft import fft2, ifft2


def fftconvolve2d(inData, inKernel):
    """
    Parameters
    ----------
    inData: array_like
        Image to be convolved.

    inKernel: array_like
        Convolution kernel. Odd size preferred.

    Returns
    -------
    outData: array_like
        Convolved image.

    """
    # Input sizes
    y1, x1 = inData.shape
    y2, x2 = inKernel.shape
    x2_half = x2 * 0.5
    y2_half = y2 * 0.5

    # Padded size must be power of 2
    l2_fac = np.log(2.0)
    x_pad = 2**(int(np.log(x1 + x2) / l2_fac + 1.0))
    y_pad = 2**(int(np.log(y1 + y2) / l2_fac + 1.0))
    xp_half = x_pad * 0.5
    yp_half = y_pad * 0.5

    # Padded arrays for FFT
    arr1 = np.zeros((y_pad, x_pad))
    arr2 = arr1.copy()

    # Pad image
    xx1 = int(xp_half)
    yy1 = int(yp_half)
    arr1[yy1:yy1+y1, xx1:xx1+x1] = inData

    # Pad kernel. PSF center must line up with image[0,0].
    xx1 = int(xp_half - x2_half)
    yy1 = int(yp_half - y2_half)
    arr2[yy1:yy1+y2, xx1:xx1+x2] = inKernel

    # 2D FFT and inverse. Discard imaginary component.
    im_fft = fft2(arr1) * fft2(arr2[::-1, ::-1])
    outData = (ifft2(im_fft))[:y1,:x1].real

    return outData


def test():
    import matplotlib.pyplot as plt

    image = np.zeros((512, 512))
    image[::50, ::50] = 1.0
    psf = np.ones((5, 5))
    outim = fftconvolve2d(image, psf)

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.imshow(image, cmap=plt.cm.gray)
    ax1.set_title('Original')

    ax2.imshow(outim, cmap=plt.cm.gray)
    ax2.set_title('Convolved')

    plt.draw()
