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
    This function implements equation 5.13 from [1]. NOTE: This implementation
    is in contrast to the KRAKEN MATLAB implementation, which normalizes the 
    output by a factor of (1 / (4 * pi)).

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """
    p = (phi_src * phi_rec).dot(hankel1(0, -k * r))
    p = np.conj(1j / (4 * 1.0) * p)
    return p


def bf_cbf(K, w):
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
    array
        Output of the Bartlett processor.

    Notes
    -----
    This function implements equation 10.21 from [1], with K defined by
    equation 10.20 and w defined by equation 10.61.

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    return w.conj().T.dot(K).dot(w)


def bf_mvdr(K, w):
    """Returns MVDR processor (e.g., for beamforming or matched
    field processing).

    Parameters
    ----------
    K : array
        Covariance matrix of received complex pressure field.

    r_hat : array
        Vector containing replica complex pressure field.

    Returns
    -------
    array
        Output of the Bartlett processor.

    Notes
    -----
    This function implements equation 10.21 from [1], with K defined by
    equation 10.20 and w defined by equation 10.61.

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """
    return 1 / (w.conj().T.dot(np.linalg.inv(K)).dot(w))


def bf_music(K, w, num_src=1):
    _, V = np.linalg.eig(K)
    V = V[:, 0:-num_src]
    return 1 / (w.conj().T.dot(V).dot(V.conj().T).dot(w))


def bf_eigen(K, w, num_src=1):
    d, V = np.linalg.eig(K)


def beamformer(K, r_hat, atype="cbf", num_src=1, abs_value=True):
    K = (K + K.conj().T) / 2  # Enforce Hermitian
    w = r_hat / np.linalg.norm(r_hat)

    if atype == "cbf":
        B = bf_cbf(K, w)
    elif atype == "mvdr":
        B = bf_mvdr(K, w)
    elif atype == "music":
        B = bf_music(K, w, num_src)
    elif atype == "eigen":
        B = bf_eigen(K, w, num_src)
    else:
        raise TypeError("Beamformer 'atype' not implemented.")

    if abs_value:
        return abs(B)
    else:
        return B


def snrdb_to_sigma(snrdb, sig_ampl=1.0):
    """Returns the standard deviation of white Gaussian noise given SNR (dB) and
    number of elements in an array.

    Parameters
    ----------
    snrdb : float
        SNR level [dB]
    sig_ampl : float
        Amplitude of the signal of interest.

    Returns
    -------
    float
        Standard deviation (sigma) of the noise.
    """
    return 10 ** (-snrdb / 20) * sig_ampl


def added_wng(size, sigma=1.0, cmplx=False, seed=None):
    if seed is None:
        rng = np.random
    else:
        rng = np.random.default_rng(seed)

    if cmplx:
        return np.vectorize(complex)(
            rng.normal(0, sigma, size) / np.sqrt(2),
            rng.normal(0, sigma, size) / np.sqrt(2),
        )
    else:
        return rng.normal(0, sigma, size)
