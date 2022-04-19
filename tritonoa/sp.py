#!/usr/bin/env python3

"""This module contains commonly used signal processing functions for
ocean acoustics workflows.

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
"""

import numpy as np
from scipy.special import hankel1


# TODO: Consider building an object for matched field processing
# workflows.
# class mfp:
#     def __init__(self, object1, object2, space=["r", "z"]):
#         self.object1 = object1
#         self.object2 = object2
#         self.space = space
#
#     def run(self):
#         for param in self.space:
#             pass
#         return


def normalize_pressure(p, log=False):
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


def pressure_field(phi_src, phi_rec, k, r):
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
    This function implements equation 5.13 from [1].

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    p = (phi_src * phi_rec) @ hankel1(0, -k * r)
    p = np.conj(np.pi * 1j / (1.0) * p)
    return p


def bartlett(K, r_hat):
    """Returns Bartlett processor (e.g., for beamforming or matched
    field processing).

    Parameters
    ----------
    K : array
        Covariance matrix of received complex pressure field.

    r_hat : array
        Vector containing replica complex pressure field.

    Returns
    -------
    B : array
        Output of the Bartlett processor.

    Notes
    -----
    This function implements equation 10.21 from [1], with K defined by
    equation 10.20 and w defined by equation 10.61.

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    w = r_hat / np.linalg.norm(r_hat)
    B = abs(w.conj().T @ K @ w)
    return B


# TODO: Build general purpose function for different beamformers.
def ambiguity_function(K, r_hat, atype="bartlett"):
    w = r_hat / np.linalg.norm(r_hat)

    if atype == "bartlett":
        B = w.conj().T @ K @ w
    elif atype == "MVDR":
        B = (w.conj().T @ np.linalg.inv(K) @ w) ** -1
    elif atype == "MCM":
        B = None
    elif atype == "WNC":
        B = None
    return abs(B)
