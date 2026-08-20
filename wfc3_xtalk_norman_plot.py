"""Crosstalk checks.

Examples
--------
>>> from wfc3_xtalk_norman_plot import plot_diff
>>> plot_diff(703)
>>> plot_diff(705, xmax=1000, ymax=0.1)
"""

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

__all__ = ["plot_diff"]

gain = 1.56


def get_data_diff(new_out, old_out):
    with fits.open(new_out) as hdulsim, fits.open(old_out) as hdulorig:
        diff_1 = (hdulsim[1].data - hdulorig[1].data) * gain
        diff_4 = (hdulsim[4].data - hdulorig[4].data) * gain

        # Signal on A, corr on B
        xa = diff_4[881, :2048]
        yb = diff_4[881, 2048:]

        # Signal on B, corr on A
        xb = diff_4[1081, 2048:]
        ya = diff_4[1081, :2048]

        # Signal on C, corr on D
        xc = diff_1[900, :2048]
        yd = diff_1[900, 2048:]

        # Signal on D, corr on C
        xd = diff_1[1100, 2048:]
        yc = diff_1[1100, :2048]

    return xa, xb, xc, xd, ya, yb, yc, yd


def get_corr(x, amp, pr_num):
    slope = {
        "A": -6.0494304e-5,
        "B": -2.0746221e-4,
        "C": -7.9701178e-5,
        "D": -2.3177171e-4
    }

    if pr_num == 703:
        intercept = defaultdict(int)  # 0
    else:  # 705
        intercept = {
            "A": 0.0180206,
            "B": 0.15501201,
            "C": -0.038376406,
            "D": 0.19124641
        }

    y = intercept[amp] + x * slope[amp]
    if pr_num == 705:  # Clamp
        y[y > 0] = 0

    return -y


def plot_diff(pr_num, xmin=0, xmax=41000, ymin=-0.005, ymax=10):
    ext = "blv_tmp"  # or "flt"
    old_out = f"pr{pr_num}/iflv38a1q_{ext}.fits"
    new_out = f"pr{pr_num}/simtest_{ext}.fits"

    xa, xb, xc, xd, ya, yb, yc, yd = get_data_diff(new_out, old_out)

    # Initialize a 2-row, 2-column multi-panel layout
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))

    # Panel 1: A→B
    ax00 = axs[0, 0]
    ax00.scatter(
        xa, yb[::-1], color='crimson', alpha=0.7, marker="x",
        label="Result"
    )
    yb_theo = get_corr(xa, "B", pr_num)
    ax00.scatter(
        xa, yb_theo, color='royalblue', marker=".",
        label="Theoretical"
    )
    ax00.set_title(f'A→B Crosstalk (Simulated;PR{pr_num})')
    ax00.set_ylabel('Crosstalk (ADU)')
    ax00.legend()

    # Panel 2: B→A
    ax01 = axs[0, 1]
    xbb = xb[::-1]
    ax01.scatter(
        xbb, ya, color='crimson', alpha=0.7, marker="x"
    )
    ya_theo = get_corr(xbb, "A", pr_num)
    ax01.scatter(
        xbb, ya_theo, color='royalblue', marker="."
    )
    ax01.set_title('B→A Crosstalk (Simulated)')
    ax01.set_xlabel('Signal (ADU)')

    # Panel 3: C→D
    ax10 = axs[1, 0]
    ax10.scatter(
        xc, yd[::-1], color='crimson', alpha=0.7, marker="x"
    )
    yd_theo = get_corr(xc, "D", pr_num)
    ax10.scatter(
        xc, yd_theo, color='royalblue', marker="."
    )
    ax10.set_title('C→D Crosstalk (Simulated)')

    # Panel 4: D→C
    ax11 = axs[1, 1]
    xdd = xd[::-1]
    ax11.scatter(
        xdd, yc, color='crimson', alpha=0.7, marker="x"
    )
    yc_theo = get_corr(xdd, "C", pr_num)
    ax11.scatter(
        xdd, yc_theo, color='royalblue', marker="."
    )
    ax11.set_title('D→C Crosstalk (Simulated)')

    # Set plot axis limits
    ax00.set_xlim(xmin, xmax)
    ax01.set_xlim(xmin, xmax)
    ax10.set_xlim(xmin, xmax)
    ax11.set_xlim(xmin, xmax)
    ax00.set_ylim(ymin, ymax)
    ax01.set_ylim(ymin, ymax)
    ax10.set_ylim(ymin, ymax)
    ax11.set_ylim(ymin, ymax)

    # Clean up layout and display
    plt.tight_layout()
    plt.show()
