#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass

import numpy as np

@dataclass
class SoundSpeedProfile:
    z: np.ndarray
    c_p: np.ndarray


def munk_ssp(z_max: float, dz: float = 1.0) -> dict:
    z = np.arange(0, z_max + dz, dz)
    B = 1200.0
    Z0 = 1200.0
    C0 = 1492.0
    EP = 0.006
    eta = 2 * (z - Z0) / B
    c_p = C0 * (1 + EP * (eta + np.exp(-eta) - 1))
    return {"z": z, "c_p": c_p}
