#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def plot_ambiguity_surface(
    B,
    rvec,
    zvec,
    ax=None,
    imshow_kwargs={},
    plot_kwargs={},
):
    IMSHOW_DEFAULTS = {
        "aspect": "auto",
        "origin": "lower",
        "interpolation": "none",
        "cmap": "viridis",
        "vmin": -10,
        "vmax": 0,
    }
    PLOT_DEFAULTS = {
        "marker": "*",
        "markersize": 15,
        "markeredgewidth": 1.5,
        "markeredgecolor": "k",
        "markerfacecolor": "w",
    }

    if ax is None:
        ax = plt.gca()

    src_z_ind, src_r_ind = np.unravel_index(np.argmax(B), (len(zvec), len(rvec)))

    im = ax.imshow(
        B,
        extent=[min(rvec), max(rvec), min(zvec), max(zvec)],
        **{**IMSHOW_DEFAULTS, **imshow_kwargs}
    )
    ax.plot(rvec[src_r_ind], zvec[src_z_ind], **{**PLOT_DEFAULTS, **plot_kwargs})
    ax.invert_yaxis()
    return ax, im


def plot_spectrogram(
    Sxx: np.ndarray, t: np.ndarray, f: np.ndarray, ax=None, kwargs: dict = {}
) -> tuple:
    IMSHOW_DEFAULTS = {
        "aspect": "auto",
        "origin": "lower",
        "interpolation": "none",
        "cmap": "viridis",
        "vmin": -40,
        "vmax": 0,
    }
    if ax is None:
        ax = plt.gca()

    im = ax.imshow(
        Sxx, extent=[min(t), max(t), min(f), max(f)], **{**IMSHOW_DEFAULTS, **kwargs}
    )
    return ax, im


def plot_SSP(z, c, boundaries=None, xlabel=None, ylabel=None, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    # Insert NaN where discontinuities exist - makes cleaner plot.
    ind = np.atleast_1d(np.argwhere(np.diff(z) == 0).squeeze())
    if len(ind) >= 1:
        if np.diff(c)[ind] != 0:
            z = np.insert(z, ind + 1, np.nan)
            c = np.insert(c, ind + 1, np.nan)

    ax.plot(c, z, **kwargs)
    if boundaries is not None:
        boundaries = np.atleast_1d(boundaries)
        for boundary in boundaries:
            ax.axhline(y=boundary, color="k", linestyle=(0, (5, 10)))

    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_ylabel(ylabel)

    try:
        if c.max() < 1500:
            xlimhi = 1500
        else:
            xlimhi = 10 * np.ceil(c.max() / 10)

        xlimlo = 10 * np.floor(c.min() / 10)
        ax.set_xlim((xlimlo, xlimhi))
        ax.set_xticks(np.arange(xlimlo, xlimhi, 10), minor=True)
    except:
        pass
    ax.grid()

    return ax


def plot_TL_2d(
    p,
    z=None,
    r=None,
    boundaries=None,
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
        extent = (r.min(), r.max(), z.min(), z.max())
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

    if boundaries is not None:
        boundaries = np.atleast_1d(boundaries)
        for boundary in boundaries:
            ax.axhline(y=boundary, color="w", linestyle=(0, (5, 10)))

    ax.invert_yaxis()
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap))
    cbar.set_label(clabel)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    return ax


def plot_TL_1d():
    pass
