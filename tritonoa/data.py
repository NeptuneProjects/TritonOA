#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import os
from typing import Any, Optional, Protocol, Union

import numpy as np


@dataclass
class DataStream:
    """Contains acoustic data and time vector."""

    X: Optional[np.ndarray] = None
    t: Optional[np.ndarray] = None

    def __call__(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns data and time vector."""
        return self.X, self.t

    @staticmethod
    def load(
        filename: Union[str, bytes, os.PathLike], exclude: Optional[str] = None
    ) -> None:
        """Loads data from numpy file."""
        X, t = None, None
        data = np.load(filename)
        if exclude is None or "X" not in exclude:
            X = data.get("X", None)
        if exclude is None or "t" not in exclude:
            t = data.get("t", None)
        return X, t

    def save(self, filename: Union[str, bytes, os.PathLike]) -> None:
        """Saves data to numpy file."""
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
