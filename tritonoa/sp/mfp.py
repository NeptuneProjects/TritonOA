#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Iterable, Union

import numpy as np

from tritonoa.sp.beamforming import beamformer


class MultiFrequencyMethods(Enum):
    """Enum for the different methods to combine the beamformer responses
    for multiple frequencies."""

    MEAN = "mean"
    SUM = "sum"
    PRODUCT = "product"


class MatchedFieldProcessor:
    """Class for evaluating the matched field processor (MFP) ambiguity."""

    def __init__(
        self,
        runner: callable,
        covariance_matrix: Union[np.ndarray, Iterable[np.ndarray]],
        freq: Union[float, Iterable[float]],
        parameters: Union[dict, list[dict]],
        beamformer: callable = beamformer,
        multifreq_method: str = "mean",
    ):
        self.runner = runner
        self.covariance_matrix = covariance_matrix
        self.freq = freq
        self.parameters = self._merge(parameters)
        self.beamformer = beamformer
        self.multifreq_method = MultiFrequencyMethods(multifreq_method)

    def __call__(self, parameters: dict) -> Union[np.ndarray, complex]:
        return self.evaluate(parameters)

    def evaluate(self, parameters: dict) -> np.ndarray:
        bf_response = []
        # TODO: Implement parallel processing for this loop
        for f, k in zip(self.freq, self.covariance_matrix):
            replica_pressure = self.runner(self.parameters | {"freq": f} | parameters)
            bf_response.append(self.beamformer(k, replica_pressure))

        if self.multifreq_method == MultiFrequencyMethods.MEAN:
            return np.mean(np.array(bf_response), axis=0)
        elif self.multifreq_method == MultiFrequencyMethods.SUM:
            return np.sum(np.array(bf_response), axis=0)
        elif self.multifreq_method == MultiFrequencyMethods.PRODUCT:
            return np.prod(np.array(bf_response), axis=0)

    @staticmethod
    def _merge(parameters: Union[dict, list[dict]]) -> dict:
        if isinstance(parameters, list):
            d = {}
            [[d.update({k: v}) for k, v in p.items()] for p in parameters]
            return d
        return parameters
