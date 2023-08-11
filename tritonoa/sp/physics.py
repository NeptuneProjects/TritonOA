#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, Union

import numpy as np
from scipy.special import hankel1


def normalize_pressure(p: Union[float, np.ndarray], log: bool = False) -> np.ndarray:
    """Takes complex pressure and returns normalized pressure.

    Parameters
    ----------
    p : array
        Array of complex pressure values.
    log : bool, default=False
        Scale normalized pressure logarithmically (e.g., for dB scale)

    Returns
    -------
    pn : array
        Normalized pressure.
    """

    pn = np.abs(p)
    pn /= np.max(pn)
    if log:
        pn = 10 * np.log10(pn)
    return pn


def pressure_field(
    phi_src: np.ndarray,
    phi_rec: np.ndarray,
    k: np.ndarray,
    r: np.ndarray,
    r_offsets: Optional[Union[float, np.ndarray]] = None,
) -> np.ndarray:
    """Calculates pressure field given range-independent vertical mode
    functions.

    Parameters
    ----------
    phi_src : array
        Complex-valued mode shape function at the source depth.
    phi_rec : array
        Complex-valued mode shape function for specified depths (e.g.,
        at receiver depths).
    k : array
        Complex-valued vertical wavenumber.
    r : array
        A point or vector of ranges.

    Returns
    -------
    p : array
        Complex pressure field with dimension (depth x range).

    Notes
    -----
    This function implements equation 5.13 from [1]. NOTE: This implementation
    is in contrast to the KRAKEN MATLAB implementation, which normalizes the
    output by a factor of (1 / (4 * pi)).

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    if r_offsets is not None:
        M = phi_rec.shape[0]
        N = len(r)
        p = np.zeros((M, N), dtype=complex)
        for zz in range(M):
            hankel = hankel1(0, -k * (r + r_offsets[zz]))
            p[zz] = (phi_src * phi_rec[zz]).dot(hankel)
    else:
        p = (phi_src * phi_rec).dot(hankel1(0, -k * r))
    p = (1j / 4) * p

    # hankel = np.exp(-1j * k * r) / np.sqrt(k.real * r)
    # p = (phi_src * phi_rec).dot(hankel)
    # p *= 1j * np.exp(-1j * np.pi / 4)
    # p /= np.sqrt(8 * np.pi * r)

    # p = (phi_src * phi_rec).dot(hankel1(0, -k * r))
    # p = (phi_src * phi_rec).dot(hankel1(0, k.conj() * r))
    # TODO: Replace hankel1 with asymptotic form

    # print(k)
    # p = np.conj(1j / (4 * 1.0) * p)
    return p
