#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Optional

import numpy as np


def create_time_vector(num_samples: int, fs: float) -> np.ndarray:
    return np.linspace(0, (num_samples - 1) / fs, num_samples)


def create_datetime_vector(
    time_vector: np.ndarray,
    start: datetime,
) -> np.ndarray:
    return np.array([start + timedelta(seconds=t) for t in time_vector])


def get_time_index(
    dt: np.ndarray,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> np.ndarray:
    if start is None:
        start = dt[0]
    if end is None:
        end = dt[-1]

    return (dt >= start) & (dt < end)
