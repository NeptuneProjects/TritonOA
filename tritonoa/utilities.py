#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

def enforce_path_type(path):
    if isinstance(path, str):
        path = Path(path)
    return path
