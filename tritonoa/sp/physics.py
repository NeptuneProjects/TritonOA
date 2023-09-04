#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, Union

import numpy as np


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

    # if r_offsets is not None:
    #     M = phi_rec.shape[0]
    #     N = len(r)
    #     p = np.zeros((M, N), dtype=complex)
    #     for zz in range(M):
    #         range_dep = np.outer(k, r + r_offsets[zz])
    #         hankel = (
    #             np.exp(1j * range_dep.conj()) / np.sqrt(np.real(range_dep))
    #         )
    #         phi_comb = (phi_src * phi_rec[zz])
    #         p[zz] = phi_comb.dot(hankel)

    # else:
    #     range_dep = np.outer(k, r)
    #     hankel = (np.exp(1j * range_dep.conj()) / np.sqrt(np.real(range_dep)))
    #     phi_comb = (phi_src * phi_rec)
    #     p = phi_comb.dot(hankel)
    # p *= -np.exp(1j * np.pi / 4)
    # p /= np.sqrt(8 * np.pi)
    # p = p.conj()
    # return p

    # Improved implementation

    r = np.atleast_2d(r)
    if r_offsets is None:
        r_offsets = np.zeros(phi_rec.shape[0])
    if r_offsets.ndim == 1:
        r_offsets = np.atleast_2d(r_offsets).T

    range_dep = np.einsum("kl,ij->kij", k, r + r_offsets)
    hankel = np.exp(1j * range_dep.conj()) / np.sqrt(np.real(range_dep))
    phi_comb = (phi_src * phi_rec)
    p = np.einsum("ik,kij->ij", phi_comb, hankel)
    p *= -np.exp(1j * np.pi / 4) / np.sqrt(8 * np.pi)
    p = p.conj()
    return p
