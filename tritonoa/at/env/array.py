#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, Union

import numpy as np


@dataclass
class Array:
    """Specifies attributes of acoustic source array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    """

    z: np.ndarray

    def __post_init__(self) -> None:
        self.z = np.atleast_1d(np.around(self.z, 3))
        self.nz = len(self.z)

    def equally_spaced(self) -> bool:
        return np.allclose(np.diff(self.z), np.diff(self.z)[0]) if self.nz > 1 else True


@dataclass
class Source(Array):
    """Specifies attributes of acoustic source array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    """

    pass


@dataclass(kw_only=True)
class Receiver(Array):
    """Specifies attributes of acoustic receiver array.

    Attributes
    ----------
    z : array
        Vector containing depths [m] of the array elements.
    nz : int
        Number of array elements.
    r : float
        Vector of ranges [km] at which field will be calculated.
    r_max : float
        Maximum range [km] of receiver range vector.
    r_min : float, default=1e-3
        Minimum range [km] of receiver range vector.
    nr : int, default=None
        Number of elements in receiver range vector.
    tilt : float, default=None
        Array tilt [deg].
    r_offsets : array, default=0
        Vector of receiver range offsets [m] to account for array tilt.
    """

    r: np.ndarray
    tilt: Optional[Union[float, None]] = None
    r_offsets: Optional[Union[np.ndarray, None]] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.format_range()
        if self.tilt or self.r_offsets is not None:
            self.apply_array_tilt()

    def apply_array_tilt(self) -> None:
        self.r_offsets = (
            self.r_offsets
            if self.tilt is None
            else np.atleast_2d(self.array_tilt(self.z, self.tilt)).T
        )

    def format_range(self) -> None:
        self.r = np.atleast_1d(self.r)
        if self.r[0] == 0:
            self.r = self.r[1:]
        self.r_min = np.min(self.r)
        self.r_max = np.max(self.r)
        self.nr = len(self.r)

    @staticmethod
    def array_tilt(z, tilt):
        return (z.max() - z) * np.sin(tilt * np.pi / 180)
