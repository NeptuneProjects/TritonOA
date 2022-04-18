#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_TL_2d(
        p,
        z=None,
        r=None,
        title=None,
        xlabel=None,
        ylabel=None,
        clabel=None,
        vmin=-40,
        vmax=0,
        interpolation=None,
        cmap="jet",
        ax=None,
        **kwargs
    ):

    if ax is None:
        ax = plt.gca()

    if (r is not None) and (z is not None):
        extent = (
            r.min(),
            r.max(),
            z.min(),
            z.max()
        )
    else:
        extent = None

    ax.imshow(
        p,
        extent=extent,
        aspect="auto",
        origin="lower",
        vmin=vmin,
        vmax=vmax,
        interpolation=interpolation,
        cmap=cmap,
        **kwargs
    )
    ax.invert_yaxis()
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap))
    cbar.set_label(clabel)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    return ax


def plot_SSP(
        z,
        c,
        xlabel=None,
        ylabel=None,
        ax=None,
        **kwargs
    ):
    if ax is None:
        ax = plt.gca()

    ax.plot(c, z)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return ax


def plot_TL_1d():
    pass

