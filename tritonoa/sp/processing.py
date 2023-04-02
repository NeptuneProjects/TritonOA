#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Callable, Optional

import numpy as np
from scipy.fft import fft

from tritonoa.sp.timefreq import frequency_vector


class NotImplementedWarning(Warning):
    pass


def find_freq_bin(
    fvec: np.ndarray,
    X: np.ndarray,
    f0: float,
    lower_bw: float = 1.0,
    upper_bw: float = 1.0,
) -> int:
    """Given a frequency vector, complex data, a target frequency, and
    upper/lower bandwidths, returns the index of the frequency bin that
    contains the maximum energy.
    """
    f_lower = f0 - lower_bw
    f_upper = f0 + upper_bw
    ind = (fvec >= f_lower) & (fvec < f_upper)
    data = np.abs(X).sum(axis=1) / X.shape[1]
    data[~ind] = -2009
    return np.argmax(data)


def generate_complex_pressure(
    data: np.ndarray,
    fs: float,
    num_segments: int,
    nfft: int,
    f0: float,
    lower_bw: float = 1.0,
    upper_bw: float = 1.0,
    noverlap: Optional[int] = None,
    window: Optional[Callable] = None,
) -> tuple[np.ndarray, int]:
    if noverlap is not None:
        raise NotImplementedWarning("Overlapping segments is not implemented yet.")

    M = data.shape[1]
    samplers_per_segment = data.shape[0] // num_segments
    fvec = frequency_vector(fs, nfft)

    complex_pressure = np.zeros((num_segments, M), dtype=complex)
    for i in range(num_segments):
        idx_start = i * samplers_per_segment
        idx_end = idx_start + nfft
        segment = data[idx_start:idx_end]

        if window is not None:
            segment = segment * window(nfft)

        X = fft(segment, n=nfft, axis=0)
        fbin = find_freq_bin(fvec, complex_pressure, f0, lower_bw, upper_bw)
        complex_pressure[i] = X[fbin]

    return complex_pressure, fbin
