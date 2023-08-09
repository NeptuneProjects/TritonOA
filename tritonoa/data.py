#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import os
from typing import Any, Optional, Protocol, Union

import numpy as np


class NoDataWarning(Warning):
    pass


@dataclass
class DataStream:
    """Contains acoustic data and time vector."""

    X: Optional[np.ndarray] = None
    t: Optional[np.ndarray] = None

    def __getitem__(self, index: Union[int, slice]) -> tuple[np.ndarray, np.ndarray]:
        """Returns data and time vector sliced by time index."""
        return self.X[index], self.t[index]

    def load(
        self, filename: Union[str, bytes, os.PathLike], exclude: Optional[str] = None
    ) -> None:
        """Loads data from numpy file."""
        data = np.load(filename)
        if exclude is None or "X" not in exclude:
            self.X = data.get("X", None)
        if exclude is None or "t" not in exclude:
            self.t = data.get("t", None)

    @property
    def num_channels(self) -> int:
        """Returns number of channels in data."""
        if self.X is None:
            return NoDataWarning("No data in variable 'X'.")
        return self.X.shape[1]

    @property
    def num_samples(self) -> int:
        """Returns number of samples in data."""
        if self.X is None:
            return NoDataWarning("No data in variable 'X'.")
        return self.X.shape[0]

    def save(self, filename: Union[str, bytes, os.PathLike]) -> None:
        """Saves data to numpy file."""
        if self.X is None:
            NoDataWarning("No data in variable 'X' to save.")
        if self.t is None:
            NoDataWarning("No data in variable 't' to save.")
        np.savez(filename, X=self.X, t=self.t)


class DataHandler(Protocol):
    def convert_to_numpy(self) -> Any:
        """Converts data to numpy arrays."""
        ...

    def load_merged(self) -> Any:
        """Loads merged numpy file."""
        ...

    def merge_numpy_files(self) -> Any:
        """Merges numpy files."""
        ...
