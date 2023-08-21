#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy.fft import fft
from scipy.io import savemat
from tqdm import tqdm
from tritonoa.data import DataStream
from tritonoa.sp.beamforming import covariance
from tritonoa.sp.timefreq import frequency_vector

log = logging.getLogger(__name__)


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
    """Parameters for defining and finding frequency of a signal."""

    freq: Optional[float] = None
    fvec: Optional[np.ndarray] = None
    peak_params: Optional[FrequencyPeakFindingParameters] = None


class Processor:
    """Processor for computing complex pressure and covariance matrices
    for a given set of frequencies.

    Parameters
    ----------
    data : DataStream
        Data stream to process.
    fs : float
        Sampling frequency.
    freq : list[float]
        List of frequencies to process.
    fft_params : FFTParameters
        Parameters for performing an FFT.
    freq_finding_params : FrequencyPeakFindingParameters
        Parameters for finding the frequency of a signal.
    """

    def __init__(
        self,
        data: DataStream,
        fs: float,
        freq: list[float],
        fft_params: FFTParameters,
        freq_finding_params: FrequencyPeakFindingParameters,
    ):
        self.data = data
        self.fs = fs
        self.frequencies = list(freq) if isinstance(freq, float) else freq
        self.fft_params = fft_params
        self.freq_finding_params = freq_finding_params
        self.fvec = frequency_vector(fs=self.fs, nfft=self.fft_params.nfft)

    def process(
        self,
        samples_per_segment,
        segments_every_n=None,
        compute_covariance=True,
        destination=Path.cwd(),
        max_workers=8,
        normalize_covariance=True,
        covariance_averaging=None,
    ):
        log.info(f"Processing data for {self.frequencies} Hz.")
        log.info(
            f"{self.frequencies} Hz: Loaded data with shape "
            f"({self.data.num_samples} samples x {self.data.num_channels} channels)"
        )

        with tqdm(
            total=len(self.frequencies),
            desc="Processing frequencies",
            unit="freq",
            bar_format="{l_bar}{bar:20}{r_bar}{bar:-20b}",
        ) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._process_worker,
                        freq_params=FrequencyParameters(
                            freq=freq,
                            fvec=self.fvec,
                            peak_params=self.freq_finding_params,
                        ),
                        destination=destination,
                        samples_per_segment=samples_per_segment,
                        segments_every_n=segments_every_n,
                        compute_covariance=compute_covariance,
                        normalize_covariance=normalize_covariance,
                        covariance_averaging=covariance_averaging,
                    )
                    for freq in self.frequencies
                ]
                [pbar.update(1) for _ in as_completed(futures)]

        log.info(f"{self.frequencies} Hz: Processing complete.")

    def _process_worker(
        self,
        freq_params,
        destination: Path,
        samples_per_segment: int,
        segments_every_n=None,
        compute_covariance=True,
        normalize_covariance=True,
        covariance_averaging=None,
    ) -> None:
        def _save_data():
            savepath = destination / f"{freq_params.freq:.1f}Hz"
            savepath.mkdir(parents=True, exist_ok=True)
            np.save(savepath / "data.npy", p)
            np.save(savepath / "f_hist.npy", f_hist)
            savemat(
                savepath / f"data_{freq_params.freq}Hz.mat",
                {"p": p, "f": freq_params.freq},
            )
            if compute_covariance:
                np.save(savepath / "covariance.npy", K)
                savemat(savepath / "covariance.mat", {"K": K})

        log.info(f"{freq_params.freq} Hz: Computing complex pressure.")
        p, f_hist = get_complex_pressure(
            data=self.data.X,
            freq_params=freq_params,
            fft_params=self.fft_params,
            samples_per_segment=samples_per_segment,
            segments_every_n=segments_every_n,
        )
        log.info(f"{freq_params.freq} Hz: Completed computing complex pressure.")
        log.info(f"{freq_params.freq} Hz: Computing covariance matrices.")
        if compute_covariance:
            K = get_covariance(p, normalize=normalize_covariance)
            if covariance_averaging is not None:
                K = average_covariance(K, covariance_averaging=covariance_averaging)
        log.info(f"{freq_params.freq} Hz: Completed computing covariance matrices.")
        log.info(f"{freq_params.freq} Hz: Saving data.")
        _save_data()
        log.info(f"{freq_params.freq} Hz: Data saved.")


def average_covariance(K: np.ndarray, covariance_averaging: int) -> np.ndarray:
    """Given a covariance matrix, averages the covariance matrix over
    segments of the time series.

    Parameters
    ----------
    K : np.ndarray
        Covariance matrix with shape (time samples, channels, channels).
    covariance_averaging : int
        Number of segments to average over.

    Returns
    -------
    np.ndarray
        Averaged covariance matrix with shape (time samples, channels, channels).
    """
    num_avg_segments = np.ceil(K.shape[0] // covariance_averaging).astype(int)
    K_split = np.array_split(K, num_avg_segments, axis=0)

    K_avg = np.zeros((num_avg_segments, K.shape[1], K.shape[2]), dtype=complex)
    for i, K_sub in enumerate(K_split):
        K_avg[i] = np.mean(K_sub, axis=0)

    return K_avg


def find_freq_bin(
    X: np.ndarray,
    freq_params: FrequencyParameters,
) -> int:
    """Given a frequency vector, complex data, a target frequency, and
    upper/lower bandwidths, returns the index of the frequency bin that
    contains the maximum energy.

    Parameters
    ----------
    X : np.ndarray
        Complex data with shape (frequency bins, channels).
    freq_params : FrequencyParameters
        Parameters for finding the frequency of a signal.

    Returns
    -------
    int
        Index of the frequency bin that contains the maximum energy.
    """
    f_lower = freq_params.freq - freq_params.peak_params.lower_bw
    f_upper = freq_params.freq + freq_params.peak_params.upper_bw
    ind = (freq_params.fvec >= f_lower) & (freq_params.fvec < f_upper)
    data = np.abs(X).sum(axis=1) / X.shape[1]
    data[~ind] = -2009
    return np.argmax(data)


def get_complex_pressure(
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
    num_segments = data.shape[0] // segments_every_n
    nfft = fft_params.nfft
    window = fft_params.window

    complex_pressure = np.zeros((num_segments, data.shape[1]), dtype=complex)
    f_hist = np.zeros(num_segments)
    for i in range(num_segments):
        idx_start = i * segments_every_n
        idx_end = idx_start + samples_per_segment
        segment = data[idx_start:idx_end]

        if window is not None:
            segment = segment * np.tile(
                window(segment.shape[0])[:, np.newaxis], (1, segment.shape[1])
            )

        X = fft(segment, n=nfft, axis=0)
        fbin = find_freq_bin(X, freq_params)
        complex_pressure[i] = X[fbin]
        f_hist[i] = freq_params.fvec[fbin]

    return complex_pressure, f_hist


def get_covariance(data: np.ndarray, normalize: bool = True) -> np.ndarray:
    """Given a complex pressure time series, returns the covariance matrix
    for each time step.

    Parameters
    ----------
    data : np.ndarray
        Complex pressure time series with shape (time samples, channels).
    normalize : bool, optional
        If True, normalizes the complex pressure time series (default: True).

    Returns
    -------
    np.ndarray
        Covariance matrix with shape (time samples, channels, channels).
    """
    K = np.zeros((data.shape[0], data.shape[1], data.shape[1]), dtype=complex)
    for i in range(data.shape[0]):
        d = np.expand_dims(data[i], axis=1)
        if normalize:
            d /= np.linalg.norm(d)
        K[i] = covariance(d)
    return K
