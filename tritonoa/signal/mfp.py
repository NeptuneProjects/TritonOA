#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Callable, Iterable, Union

import numpy as np

from tritonoa.signal.sp import beamformer


class MatchedFieldProcessor:
    """Class for evaluating the matched field processor (MFP) ambiguity."""

    def __init__(
        self,
        runner: Callable,
        covariance_matrix: Union[np.ndarray, Iterable[np.ndarray]],
        freq: Union[float, Iterable[float]],
        parameters: dict,
        beamformer: Callable = beamformer
    ):
        self.runner = runner
        self.covariance_matrix = covariance_matrix
        self.freq = freq
        self.parameters = parameters
        self.beamformer = beamformer

    def __call__(self, parameters: dict) -> np.ndarray:
        return self.evaluate(parameters)

    def evaluate(self, parameters: dict) -> np.ndarray:
        bf_response = []
        for f, k in zip(self.freq, self.covariance_matrix):
            replica_pressure = self.runner(self.parameters | {"freq": f} | parameters)
            bf_response.append(self.beamformer(k, replica_pressure))
        
        return np.mean(np.array(bf_response), axis=0)


# class MatchedFieldProcessingRunner(ABC):
#     """Abstract base class for MFP runs."""

#     def __init__(self, processor: MatchedFieldProcessor, noise_db: float = np.Inf):

#         pass

#     @abstractmethod
#     def run():
#         pass

