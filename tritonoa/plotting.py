#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib as mpl
import matplotlib.pyplot as plt
# import numpy as np

def plot_TL_2d(
        p,
        z=None,
        r=None,
        title=None,
        xlabel="Range [km]",
        ylabel="Depth [m]",
        clabel="TL [dB]",
        figsize=(8, 6),
        vmin=-40,
        vmax=0,
        interpolation=None,
        cmap="jet",
        show=True
    ):
    fig = plt.figure(figsize=figsize, facecolor="w")

    # levs = np.linspace(np.min(p), np.max(p), 40) / 2

    if (r is not None) and (z is not None):
        extent = (
            r.min(),
            r.max(),
            z.min(),
            z.max()
        )
    else:
        extent = None

    plt.imshow(
        p,
        extent=extent,
        aspect="auto",
        origin="lower",
        vmin=vmin,
        vmax=vmax,
        interpolation=interpolation,
        cmap=cmap
    )
    plt.gca().invert_yaxis()
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap))
    cbar.set_label(clabel)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if show:
        plt.show()
    else:
        plt.close()
    return fig


def plot_SSP():
    pass


def plot_TL_1d():
    pass

