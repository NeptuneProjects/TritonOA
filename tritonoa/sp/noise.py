#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains commonly used signal processing functions for
ocean acoustics workflows.

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
"""

from typing import Optional

import numpy as np


def added_wng(
    size: int, sigma: float = 1.0, cmplx: bool = False, seed: Optional[int] = None
) -> np.ndarray:
    """Returns an array of white Gaussian noise with specified standard
    deviation.

    Parameters
    ----------
    size : int
        Number of elements in the array.
    sigma : float, default=1.0
        Standard deviation of the noise.
    cmplx : bool, default=False
        Return complex-valued noise.
    seed : int, default=None
        Seed for the random number generator.

    Returns
    -------
    np.ndarray
        Array of white Gaussian noise.

    Notes
    -----
    This function uses numpy.random.default_rng() for random number
    generation. If seed is not specified, the default random number
    generator is used. If seed is specified, a new random number
    generator is created with the specified seed.

    Examples
    --------
    >>> import numpy as np
    >>> from tritonoa.sp.noise import added_wng
    >>> added_wng(5, 1.0, False, 0)
    array([ 1.76405235,  0.40015721,  0.97873798,  2.2408932 ,  1.86755799])
    """
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


def snrdb_to_sigma(snrdb: float, sig_ampl: float = 1.0) -> float:
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
