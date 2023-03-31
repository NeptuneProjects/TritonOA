#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Union


def enforce_path_type(path: Union[str, bytes, os.PathLike]) -> os.PathLike:
    if isinstance(path, str):
        path = Path(path)
    return path
