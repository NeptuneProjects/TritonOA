#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

import numpy as np

from tritonoa.ssp import SoundSpeedProfile


class ProfileArrayLengthError(Exception):
    pass


@dataclass
class SoundSpeedProfileAT(SoundSpeedProfile):
    rho: np.ndarray = field(default=np.array([1.0], dtype=np.float64))
    c_s: np.ndarray = field(default=np.array([0.0], dtype=np.float64))
    a_p: np.ndarray = field(default=np.array([0.0], dtype=np.float64))
    a_s: np.ndarray = field(default=np.array([0.0], dtype=np.float64))

    def __post_init__(self):
        self.enforce_ndarray()
        self.check_dimensions()
        self.form_arrays()

    def check_dimensions(self) -> None:
        for k, v in vars(self).items():
            if (len(v) > len(self.z)) or ((len(v) != 1) and (len(v) != len(self.z))):
                raise ProfileArrayLengthError(
                    f"Mismatch in number of elements in attribute `{k}` and `z`."
                )

    def enforce_ndarray(self) -> None:
        [
            setattr(self, k, np.atleast_1d(np.array(v, dtype=np.float64)))
            for k, v in vars(self).items()
        ]

    def form_arrays(self) -> None:
        n = len(self.z)
        [
            setattr(self, k, np.array([v[i] if len(v) > 1 else v[0] for i in range(n)]))
            for k, v in vars(self).items()
            if k != "z"
        ]


@dataclass
class SSPLayer:
    ssp: SoundSpeedProfileAT
    nmesh: int = 0
    sigma: float = 0

    def __post_init__(self):
        self.z_max = self.ssp.z.max()
