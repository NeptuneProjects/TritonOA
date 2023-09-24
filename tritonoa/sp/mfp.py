#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from enum import Enum
from typing import Callable, Iterable, Protocol, Union

import numpy as np

from tritonoa.sp.beamforming import beamformer


class MultiFrequencyMethods(Enum):
    """Enum for the different methods to combine the beamformer responses
    for multiple frequencies."""

    MEAN = "mean"
    SUM = "sum"
    PRODUCT = "product"


class ParameterFormatter(Protocol):
    """Protocol for formatting matched field processor parameters.

    Args:
        freq: Frequency.
        title: Title.
        fixed_parameters: Fixed parameters.
        search_parameters: Search parameters.

    Returns:
        Dictionary with the formatted parameters.
    """

    def __call__(
        self,
        freq: float,
        title: str,
        fixed_parameters: dict,
        search_parameters: dict,
    ) -> dict:
        ...


class MatchedFieldProcessor:
    """Class for evaluating the matched field processor (MFP) ambiguity."""

    def __init__(
        self,
        runner: callable,
        covariance_matrix: Union[np.ndarray, Iterable[np.ndarray]],
        freq: Union[float, Iterable[float]],
        parameters: Union[dict, list[dict]] = {},
        parameter_formatter: ParameterFormatter = None,
        beamformer: callable = beamformer,
        multifreq_method: str = "mean",
        max_workers: int = None,
    ):
        self.runner = runner
        self.covariance_matrix = covariance_matrix
        self.freq = [freq] if not isinstance(freq, Iterable) else freq
        self.parameters = self._merge(parameters)
        self.format_parameters = (
            self._default_parameter_fmt
            if parameter_formatter is None
            else parameter_formatter
        )
        self.beamformer = beamformer
        self.multifreq_method = MultiFrequencyMethods(multifreq_method)
        if max_workers is None:
            self.max_workers = len(self.freq)
        else:
            self.max_workers = max_workers

    def __call__(self, parameters: dict) -> Union[np.ndarray, complex]:
        return self.evaluate(parameters)

    def evaluate(self, parameters: dict) -> np.ndarray:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            bf_response = [
                res
                for res in executor.map(
                    self._evaluate_frequency,
                    [
                        self.format_parameters(
                            freq=f,
                            title=f"{f:.0f}Hz",
                            fixed_parameters=self.parameters,
                            search_parameters=parameters,
                        )
                        for f in self.freq
                    ],
                    [self.runner] * len(self.freq),
                    [partial(self.beamformer, K=k) for k in self.covariance_matrix],
                )
            ]

        if self.multifreq_method == MultiFrequencyMethods.MEAN:
            return np.mean(np.array(bf_response), axis=0)
        elif self.multifreq_method == MultiFrequencyMethods.SUM:
            return np.sum(np.array(bf_response), axis=0)
        elif self.multifreq_method == MultiFrequencyMethods.PRODUCT:
            return np.prod(np.array(bf_response), axis=0)

    @staticmethod
    def _default_parameter_fmt(
        freq: float, title: str, fixed_parameters: dict, search_parameters: dict
    ) -> dict:
        return fixed_parameters | {"freq": freq, "title": title} | search_parameters

    @staticmethod
    def _evaluate_frequency(
        parameters: dict, runner: Callable, beamformer: Callable
    ) -> np.ndarray:
        return beamformer(r_hat=runner(parameters))

    @staticmethod
    def _merge(parameters: Union[dict, list[dict]]) -> dict:
        if isinstance(parameters, list):
            d = {}
            [[d.update({k: v}) for k, v in p.items()] for p in parameters]
            return d
        return parameters
