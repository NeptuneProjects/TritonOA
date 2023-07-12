#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

import numpy as np

from tritonoa.ssp import SoundSpeedProfile


@dataclass
class SoundSpeedProfileAT(SoundSpeedProfile):
    # TODO: Change `default` to `default_factory`
    rho: np.ndarray = field(default=np.array([1.0], dtype=np.float64))
    c_s: np.ndarray = field(default=np.array([0.0], dtype=np.float64))
    a_p: np.ndarray = field(default=np.array([0.0], dtype=np.float64))
    a_s: np.ndarray = field(default=np.array([0.0], dtype=np.float64))

    def __post_init__(self):
        super().format_data()


@dataclass
class SSPLayer:
    ssp: SoundSpeedProfileAT
    nmesh: int = 0
    sigma: float = 0

    def __post_init__(self):
        self.z_max = self.ssp.z.max()
