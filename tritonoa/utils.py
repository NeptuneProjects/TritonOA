# -*- coding: utf-8 -*-

from pathlib import Path


def clean_up_files(path: Path, extensions: list[str], pattern: str = "*") -> None:
    [[f.unlink() for f in Path(path).glob(f"{pattern}.{ext}")] for ext in extensions]
