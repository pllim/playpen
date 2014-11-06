"""Matplotlib interactive test.

http://matplotlib.org/faq/usage_faq.html#what-is-interactive-mode

**Summary**

In interactive mode, pyplot functions automatically draw to the screen.

When plotting interactively, if using object method calls in addition to pyplot
functions, then call draw() whenever you want to refresh the plot.

Use non-interactive mode in scripts in which you want to generate one or more
figures and display them before ending or generating a new set of figures.
In that case, use show() to display the figure(s) and to block execution until
you have manually destroyed them.

"""
import matplotlib.pyplot as plt
import numpy as np

plt.ioff()  # Do not need ion()


def test():
    """Test iteractive and non-interactive plotting.

    Plots 1 and 3 show on screen and waits for user.
    Plots 2 and 4 saved automatically to files.

    """
    is_interactive = [True, False, True, False]

    for i, ion in enumerate(is_interactive, 1):
        a = np.random.rand(100, 100)
        plt.clf()
        plt.imshow(a)
        plt.title('Plot {0}'.format(i))
        plt.draw()

        if ion:
            plt.show()
        else:
            plt.savefig('test{0}.png'.format(i))
            plt.close()
