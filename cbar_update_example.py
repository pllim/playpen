"""Example of auto-update colorbar.

Examples
--------
>>> import cbar_update_example
>>> cbar_update_example.test()

"""
import matplotlib.pyplot as plt
import numpy as np
import time


__author__ = 'Someone from some Python mailing list'


def do_plots(fig, ax, cbar, pos, i):
   """
   Pretend this is a long calculation that outputs
   a plot every few seconds.

   """
   inds = np.indices((20, 20))
   cax = ax.imshow(inds[pos] * i)
   ax.set_title('{} plot # {}'.format(['some', 'other'][pos], i))
   cbar.update_bruteforce(cax)
   plt.draw()
   time.sleep(1)


def test():
   fig = plt.figure()
   dummy = np.zeros((20, 20))

   ax, cbar = [], []
   for i in xrange(2):
       ax.append( fig.add_subplot(2, 1, i) )
       cax = ax[i].imshow(dummy)
       cbar.append( fig.colorbar(cax) )

   for i in xrange(5):
       do_plots(fig, ax[0], cbar[0], 0, i + 1)
       do_plots(fig, ax[1], cbar[1], 1, i + 1)
