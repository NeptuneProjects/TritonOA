#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


class ProfileArrayLengthError(Exception):
    pass


@dataclass
class SoundSpeedProfile(ABC):
    z: np.ndarray
    c_p: np.ndarray

    @abstractmethod
    def __post_init__(self):
        """Post-initialization hook."""

    def format_data(self) -> None:
        self.enforce_ndarrays()
        self.check_dimensions()
        self.form_ndarrays()

    def check_dimensions(self) -> None:
        for k, v in vars(self).items():
            if (len(v) > len(self.z)) or ((len(v) != 1) and (len(v) != len(self.z))):
                raise ProfileArrayLengthError(
                    f"Mismatch in number of elements in attribute `{k}` and `z`."
                )

    def enforce_ndarrays(self) -> None:
        [
            setattr(self, k, np.atleast_1d(np.array(v, dtype=np.float64)))
            for k, v in vars(self).items()
        ]

    def form_ndarrays(self) -> None:
        n = len(self.z)
        [
            setattr(self, k, np.array([v[i] if len(v) > 1 else v[0] for i in range(n)]))
            for k, v in vars(self).items()
            if k != "z"
        ]


def munk_ssp(z_max: float, dz: float = 1.0) -> dict:
    z = np.arange(0, z_max + dz, dz)
    B = 1200.0
    Z0 = 1200.0
    C0 = 1492.0
    EP = 0.006
    eta = 2 * (z - Z0) / B
    c_p = C0 * (1 + EP * (eta + np.exp(-eta) - 1))
    return {"z": z, "c_p": c_p}
