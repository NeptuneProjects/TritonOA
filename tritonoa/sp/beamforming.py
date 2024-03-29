#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


def bf_cbf(K: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Returns Bartlett processor (e.g., for beamforming or matched
    field processing).

    Parameters
    ----------
    K : np.ndarray (M x M)
        Covariance matrix of received complex pressure field measured at
        M points.

    w : np.ndarray (M (x N))
        Vector containing N replica complex pressure field simulated at
        M points.

    Returns
    -------
    np.ndarray (1 x N)
        Output of the Bartlett processor for N replicas.

    Notes
    -----
    This function implements equation 10.21 from [1], with K defined by
    equation 10.20 and w defined by equation 10.61.

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    return np.diag(w.conj().T.dot(K).dot(w))


def bf_cbf_ml(K: np.ndarray, w: np.ndarray):
    """Returns Bartlett processor (e.g., for beamforming or matched
    field processing).

    Parameters
    ----------
    K : np.ndarray (M x M)
        Covariance matrix of received complex pressure field measured at
        M points.

    w : np.ndarray (M (x N))
        Vector containing N replica complex pressure field simulated at
        M points.

    Returns
    -------
    np.ndarray (1 x N)
        Output of the Bartlett processor for N replicas.

    Notes
    -----
    This function implements equation 10.21 from [1], with K defined by
    equation 10.20 and w defined by equation 10.61.

    [1] Finn B. Jensen, William A. Kuperman, Michael B. Porter, and
    Henrik Schmidt. 2011. Computational Ocean Acoustics (2nd. ed.).
    Springer Publishing Company, Incorporated.
    """

    return np.diag(np.trace(K) - w.conj().T.dot(K).dot(w))


def _bf_cbf_ml(K: np.ndarray, w: np.ndarray):
    phi = bf_cbf_ml(K, w)
    n_h = K.shape[0]
    denom = np.e * np.pi * phi
    return (n_h / denom) ** n_h


def bf_mvdr(K: np.ndarray, w: np.ndarray) -> np.ndarray:
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
    return np.diag(1 / (w.conj().T.dot(np.linalg.inv(K)).dot(w)))


def bf_music(K: np.ndarray, w: np.ndarray, num_src: int = 1) -> np.ndarray:
    _, V = np.linalg.eig(K)
    V = V[:, 0:-num_src]
    return 1 / (w.conj().T.dot(V).dot(V.conj().T).dot(w))


def bf_eigen(K: np.ndarray, w: np.ndarray, num_src: int = 1) -> np.ndarray:
    d, V = np.linalg.eig(K)


def beamformer(
    K: np.ndarray,
    r_hat: np.ndarray,
    atype: str = "cbf",
    num_src: int = 1,
    abs_value: bool = True,
) -> np.ndarray:
    """Returns the output of a beamformer."""
    # K = enforce_hermitian(K)
    w = r_hat / np.linalg.norm(r_hat, axis=0)

    if atype == "cbf":
        B = bf_cbf(K, w)
    elif atype == "cbf_ml":
        B = bf_cbf_ml(K, w)
    elif atype == "cbf_ml2":
        B = _bf_cbf_ml(K, w)
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


def covariance(a: np.ndarray, b: np.ndarray = None) -> np.ndarray:
    """Returns the covariance matrix of a and b.

    Parameters
    ----------
    a : array
        Complex-valued pressure field.
    b : array
        Complex-valued pressure field.

    Returns
    -------
    array
        Covariance matrix of a and b.
    """
    if b is None:
        b = a
    return a.dot(b.conj().T)


def enforce_hermitian(A: np.ndarray) -> np.ndarray:
    """Returns the Hermitian of A.

    Parameters
    ----------
    A : array
        Complex-valued matrix.

    Returns
    -------
    array
        Hermitian of A.
    """
    return (A + A.conj().T) / 2
