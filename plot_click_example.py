"""Test to get mouse position in plot.

Examples
========
>>> from plot_click_example import plot_click
>>> plot_click()

References
==========
http://bmi.bmt.tue.nl/~philbers/8C080/matplotlibtutorial.html

"""
# THIRD PARTY
import matplotlib.pyplot as plt
import numpy as np


def plot_click(data=None):
    """Plot dummy data and handle user clicks."""

    # Generate data
    if data is None:
        data = np.arange(10000).reshape(100, 100)

    # Show data
    plt.imshow(data)

    # Register click events
    plt.connect('button_press_event', _on_click)

    # Show plot
    plt.show()


def _on_click(event):
    """Print and mark clicked coordinates."""

    # Print data coordinates to screen
    print 'X, Y:', event.xdata, event.ydata

    # Mark them on plot too
    plt.plot(event.xdata, event.ydata, 'rx')
