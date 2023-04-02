#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from scipy.fft import fft

from tritonoa.sp.timefreq import frequency_vector


class NotImplementedWarning(Warning):
    pass


@dataclass
class FFTParameters:
    """Parameters for performing an FFT."""

    nfft: int
    noverlap: int = 0
    window: Optional[Callable] = None


@dataclass
class FrequencyParameters:
    """Parameters for finding the frequency of a signal."""

    freq: float
    fs: float
    lower_bw: float = 1.0
    upper_bw: float = 1.0


def find_freq_bin(
    X: np.ndarray,
    freq_params: FrequencyParameters,
) -> int:
    """Given a frequency vector, complex data, a target frequency, and
    upper/lower bandwidths, returns the index of the frequency bin that
    contains the maximum energy.
    """
    f_lower = freq_params.freq - freq_params.lower_bw
    f_upper = freq_params.freq + freq_params.upper_bw
    ind = (freq_params.fvec >= f_lower) & (freq_params.fvec < f_upper)
    data = np.abs(X).sum(axis=1) / X.shape[1]
    data[~ind] = -2009
    return np.argmax(data)


def generate_complex_pressure(
    data: np.ndarray,
    # fs: float,
    num_segments: int,
    freq_params: FrequencyParameters,
    fft_params: FFTParameters,
) -> tuple[np.ndarray, np.ndarray]:
    if fft_params.noverlap is not None:
        raise NotImplementedWarning("Overlapping segments is not implemented yet.")

    M = data.shape[1]
    nfft = fft_params.nfft
    window = fft_params.window
    fvec = freq_params.fvec

    samplers_per_segment = data.shape[0] // num_segments
    complex_pressure = np.zeros((num_segments, M), dtype=complex)
    f_hist = np.zeros(num_segments)
    for i in range(num_segments):
        idx_start = i * samplers_per_segment
        idx_end = idx_start + nfft
        segment = data[idx_start:idx_end]

        if window is not None:
            segment = segment * window(nfft)

        X = fft(segment, n=nfft, axis=0)
        fbin = find_freq_bin(fvec, complex_pressure, freq_params)
        complex_pressure[i] = X[fbin]
        f_hist[i] = fvec[fbin]

    return complex_pressure, f_hist