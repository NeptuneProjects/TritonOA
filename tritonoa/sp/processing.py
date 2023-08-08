#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from scipy.fft import fft


class NotImplementedWarning(Warning):
    pass


@dataclass
class FFTParameters:
    """Parameters for performing an FFT."""

    nfft: int
    noverlap: Optional[int] = None
    window: Optional[Callable] = None


@dataclass
class FrequencyPeakFindingParameters:
    """Parameters for finding the frequency of a signal."""

    lower_bw: float = 1.0
    upper_bw: float = 1.0


@dataclass
class FrequencyParameters:
    freq: Optional[float] = None
    # fs: Optional[float] = None
    fvec: Optional[np.ndarray] = None
    peak_params: Optional[FrequencyPeakFindingParameters] = None


def find_freq_bin(
    X: np.ndarray,
    freq_params: FrequencyParameters,
) -> int:
    """Given a frequency vector, complex data, a target frequency, and
    upper/lower bandwidths, returns the index of the frequency bin that
    contains the maximum energy.
    """
    f_lower = freq_params.freq - freq_params.peak_params.lower_bw
    f_upper = freq_params.freq + freq_params.peak_params.upper_bw
    ind = (freq_params.fvec >= f_lower) & (freq_params.fvec < f_upper)
    data = np.abs(X).sum(axis=1) / X.shape[1]
    data[~ind] = -2009
    return np.argmax(data)


def generate_complex_pressure(
    data: np.ndarray,
    freq_params: FrequencyParameters,
    fft_params: FFTParameters,
    samples_per_segment: int,
    segments_every_n: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Given a time series, returns the complex pressure and frequency
    vector.

    Parameters
    ----------
    data : np.ndarray
        Time series data with shape (time samples, channels).
    freq_params : FrequencyParameters
        Parameters for finding the frequency of a signal.
    fft_params : FFTParameters
        Parameters for performing an FFT.
    samples_per_segment : int
        Number of samples per segment.
    segments_every_n : int, optional
        Number of samples between segments (default: None). If None, will
        default to samples_per_segment.

    Returns
    -------
    np.ndarray
        Complex pressure at each time step.
    np.ndarray
        Array of precise frequency bins used to generate complex pressure.
    """

    if segments_every_n is None:
        segments_every_n = samples_per_segment

    M = data.shape[1]
    nfft = fft_params.nfft
    window = fft_params.window
    num_segments = data.shape[0] // segments_every_n

    complex_pressure = np.zeros((num_segments, M), dtype=complex)
    f_hist = np.zeros(num_segments)
    for i in range(num_segments):
        idx_start = i * samples_per_segment
        idx_end = idx_start + nfft
        segment = data[idx_start:idx_end]

        if window is not None:
            segment = segment * window(nfft)[:, np.newaxis]

        X = fft(segment, n=nfft, axis=0)
        fbin = find_freq_bin(X, freq_params)
        complex_pressure[i] = X[fbin]
        f_hist[i] = freq_params.fvec[fbin]

    return complex_pressure, f_hist
