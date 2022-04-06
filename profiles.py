#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from core import SoundSpeedProfile

class MunkSSP(SoundSpeedProfile):
    def __init__(self, z_max, dz=1):
        z = np.arange(0, z_max+dz, dz)
        B = 1200.
        Z0 = 1200.
        C0 = 1492.
        EP = 0.006
        eta = 2 * (z - Z0) / B
        c_p = C0 * (1 + EP*(eta + np.exp(-eta) - 1))
        super().__init__(z, c_p)