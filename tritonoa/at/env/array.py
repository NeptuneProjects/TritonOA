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
    azimuth : float, default=0.0
        Array azimuth [deg].
    z_pivot : float, default=None
        Pivot depth [m] for array tilt.
    r_offsets : array, default=0
        Vector of receiver range offsets [m] to account for array tilt.
    """

    r: np.ndarray
    tilt: Optional[float] = None
    azimuth: float = 0.0
    z_pivot: Optional[float] = None
    r_offsets: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.format_range()
        if self.tilt or self.r_offsets is not None:
            self.apply_array_tilt()

    def apply_array_tilt(self) -> None:
        if self.tilt is None:
            self.r_offsets = self.r_offsets
        else:
            # self.r_offsets = self.simple_array_tilt(
            #     self.z, self.tilt, self.z_pivot, unit="deg"
            # )
            self.r_offsets, self.coords = compute_range_offsets(
                self.r, self.z, self.tilt, self.azimuth, self.z_pivot
            )
            self.z = self.coords[:, -1]

    def format_range(self) -> None:
        self.r = np.atleast_1d(self.r)
        if self.r[0] == 0:
            self.r = self.r[1:]
        self.r_min = np.min(self.r)
        self.r_max = np.max(self.r)
        self.nr = len(self.r)

    @staticmethod
    def simple_array_tilt(
        z: np.ndarray, tilt: float, z_pivot: Optional[float] = None, unit: str = "deg"
    ) -> np.ndarray:
        """Computes range offsets for a tilted array. Does NOT take into
        account depression of array elements due to tilt.

        Parameters
        ----------
        z : np.ndarray
            Vector of receiver depths [m].
        tilt : float
            Array tilt in "deg" or "rad".
        z_pivot : float, default=None
            Pivot depth [m] for array tilt. If None, defaults to maximum
            depth of receiver array.
        unit : str, default="deg"
            Unit of angle ("deg" or "rad")

        Returns
        -------
        range_offsets : np.ndarray
            Vector of range offsets [m] for each receiver element.
        """
        if unit == "deg":
            tilt = np.deg2rad(tilt)
        if z_pivot is None:
            z_pivot = np.max(z)
        return np.abs(z_pivot - z) * np.tan(-tilt)

    @staticmethod
    def array_tilt(
        z: np.ndarray,
        tilt: float,
        azimuth: float = 0.0,
        z_pivot: Optional[float] = None,
        unit: str = "deg",
    ) -> np.ndarray:
        """Computes the 3-D coordinates of a tilted array.

        Parameters
        ----------
        z : np.ndarray
            Vector of receiver depths [m].
        tilt : float
            Array tilt in "deg" or "rad".
        azimuth : float, default=0.0
            Array azimuth in "deg" or "rad".
        z_pivot : float, default=None
            Pivot depth [m] for array tilt. If None, defaults to maximum
            depth of receiver array.
        unit : str, default="deg"
            Unit of angle ("deg" or "rad")

        Returns
        -------
        np.ndarray
            An (Nx3) array specifying a tilted array in 3-D cartesian coordinates.
        """
        if azimuth is None:
            azimuth = 0.0
        if z_pivot is None:
            z_pivot = np.max(z)

        if unit == "deg":
            tilt = np.deg2rad(tilt)
            azimuth = np.deg2rad(azimuth)

        hyp = np.abs(z_pivot - z)
        x_t = hyp * np.sin(tilt) * np.sin(azimuth)
        y_t = hyp * np.sin(tilt) * np.cos(azimuth)
        z_t = z_pivot - hyp * np.cos(tilt)

        return np.array([x_t, y_t, z_t]).T


def compute_range_offsets(
    rec_r: np.ndarray,
    z: np.ndarray,
    tilt: float,
    azimuth: float = 0.0,
    z_pivot: float = None,
    unit: str = "deg",
) -> np.ndarray:
    """Computes range offsets for a tilted array. Takes into account
    depression of array elements due to tilt, as well as horizontal
    displacement.

    Parameters
    ----------
    rec_r : np.ndarray
        Vector of receiver ranges [km].
    z : np.ndarray
        Vector of receiver depths [m].
    tilt : float
        Array tilt in "deg" or "rad".
    azimuth : float, default=0.0
        Array azimuth in "deg" or "rad".
    z_pivot : float, default=None
        Pivot depth [m] for array tilt. If None, defaults to maximum
        depth of receiver array.
    unit : str, default="deg"
        Unit of angle ("deg" or "rad")

    Returns
    -------
    range_offsets : np.ndarray
        Vector of range offsets [m] for each receiver element.
    tilted_array : np.ndarray
        An (Nx3) array specifying a tilted array in 3-D cartesian coordinates.
    """

    if z_pivot is None:
        z_pivot = np.max(z)

    rec_r_m = rec_r * 1000  # Convert from km to m
    rec_r_vec = np.array(
        [np.zeros_like(rec_r_m), rec_r_m]
    ).squeeze()  # Convert to 2D vector
    N = len(np.atleast_1d(rec_r_m))

    tilted_array = Receiver.array_tilt(z, tilt, azimuth, z_pivot, unit)
    tilted_array_slice = tilted_array[:, :2]  # Slice off z-axis
    M = len(tilted_array)

    # Vectorize for broadcasting
    tilted_array_slice = tilted_array_slice[:, :, np.newaxis]
    tilted_array_slice = np.tile(tilted_array_slice, (1, 1, N)).squeeze()
    rec_r_vec = rec_r_vec[np.newaxis, :]
    rec_r_vec = np.tile(rec_r_vec, (M, 1, 1)).squeeze()

    # Compute range offsets
    total_range = np.linalg.norm(tilted_array_slice - rec_r_vec, axis=1)
    range_offsets = total_range - np.tile(rec_r_m, (M, 1)).squeeze()

    return range_offsets, tilted_array


def rotate_array_3D(theta: float, array: np.ndarray, unit: str = "deg") -> np.ndarray:
    """Rotates a 3-D array about the z-axis.

    Parameters
    ----------
    theta : float
        Rotation angle [deg or rad].
    array : np.ndarray
        An (Nx3) array specifying a tilted array in 3-D coordinates.
    unit : str, default="deg"
        Unit of angle ("deg" or "rad")

    Returns
    -------
    np.ndarray
        An (Nx3) array specifying a rotated array in 3-D cartesian coordinates.
    """
    rot = rotation_matrix_3D(theta, unit)
    return np.tensordot(array, rot, axes=1)


def rotation_matrix_3D(theta: float, unit: str = "deg") -> np.ndarray:
    """Returns a 3-D rotation matrix about the z-axis.

    Parameters
    ----------
    theta : float
        Rotation angle [deg or rad].
    unit : str, default="deg"
        Unit of angle ("deg" or "rad")

    Returns
    -------
    np.ndarray
        A (3x3) rotation matrix.
    """
    if unit == "deg":
        theta = np.deg2rad(theta)

    return np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )
