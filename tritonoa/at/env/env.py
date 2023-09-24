# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from pathlib import Path
import secrets
from typing import Any, List, Union

from tritonoa.at.env.halfspace import Bottom, Top
from tritonoa.at.env.ssp import SSPLayer


@dataclass
class AcousticsToolboxEnvironment(ABC):
    title: str
    freq: float
    layers: List[SSPLayer]
    top: Top
    bottom: Bottom
    tmpdir: Union[str, bytes, os.PathLike] = "."

    def __post_init__(self):
        self.nmedia = len(self.layers)
        self.tmpdir = Path(self.tmpdir)
        self.title += str(secrets.token_hex(4))

    @abstractmethod
    def write_envfil(self) -> Any:
        pass

    def _check_tmpdir(self) -> None:
        self.tmpdir.mkdir(parents=True, exist_ok=True)

    def _write_envfil(self) -> os.PathLike:
        self._check_tmpdir()
        envfil = self.tmpdir / f"{self.title}.env"
        with open(envfil, "w") as f:
            # Block 1 - Title
            f.write(f"'{self.title}' ! Title \r\n")
            # Block 2 - Frequency
            f.write(f"{self.freq:8.2f} \t \t \t ! Frequency (Hz) \r\n")
            # Block 3 - Number of Layers
            f.write(f"{self.nmedia:8d} \t \t \t ! NMEDIA \r\n")
            # Block 4 - Top Option
            f.write(f"'{self.top.opt}' \t \t \t ! Top Option \r\n")
            # Block 4a - Top Halfspace Properties
            if self.top.opt[1] == "A":
                f.write(
                    f"     {self.layers[0].ssp.z[0]:6.2f}"
                    + f" {self.top.c_p:6.2f}"
                    + f" {self.top.c_s:6.2f}"
                    + f" {self.top.rho:6.2f}"
                    + f" {self.top.a_p:6.2f}"
                    + f" {self.top.a_s:6.2f}"
                    + "  \t ! Upper halfspace \r\n"
                )
            # Block 5 - Sound Speed Profile
            for layer in self.layers:
                f.write(
                    f"{layer.nmesh:5d} "
                    + f"{layer.sigma:4.2f} "
                    + f"{layer.z_max:6.2f} "
                    + "\t ! N sigma max_layer_depth \r\n"
                )
                for zz in range(len(layer.ssp.z)):
                    f.write(
                        f"\t {layer.ssp.z[zz]:6.2f} "
                        + f"\t {layer.ssp.c_p[zz]:6.2f} "
                        + f"\t {layer.ssp.c_s[zz]:6.2f} "
                        + f"\t {layer.ssp.rho[zz]:6.2f} "
                        + f"\t {layer.ssp.a_p[zz]:6.2f} "
                        + f"\t {layer.ssp.a_s[zz]:6.2f} "
                        + "/ \t ! z cp cs rho ap as \r\n"
                    )
            # Block 6 - Bottom Option
            f.write(
                f"'{self.bottom.opt}' {self.bottom.sigma:6.2f}"
                + "  \t \t ! Bottom Option, sigma\r\n"
            )
            # Block 6a - Bottom Halfspace from Geoacoustic Parameters
            if self.bottom.opt[0] == "A":
                f.write(
                    f"     {self.bottom.z:6.2f}"
                    + f" {self.bottom.c_p:6.2f}"
                    + f" {self.bottom.c_s:6.2f}"
                    + f" {self.bottom.rho:6.2f}"
                    + f" {self.bottom.a_p:6.2f}"
                    + f" {self.bottom.a_s:6.2f}"
                    + "  \t ! Lower halfspace \r\n"
                )
            # Block 6b - Bottom Halfspace from Grain Size
            elif self.bottom.opt[0] == "G":
                f.write(f"   {self.bottom.z:6.2f} {self.bottom.mz:6.2f} ! zb mz\r\n")

        return envfil
