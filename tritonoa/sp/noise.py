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
