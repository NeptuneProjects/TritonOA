#!/usr/bin/env python3

"""This module contains objects common to the various ocean acoustics
models in Acoustics Toolbox software.

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
"""

from configparser import ConfigParser
import contextlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np


class Array:
    """Specifies attributes of an acoustic array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    """

    def __init__(self, z: float):
        self.z = np.atleast_1d(z)
        self.nz = len(np.atleast_1d(z))

    def equally_spaced(self):
        n = len(self.z)
        ztemp = np.linspace(self.z[0], self.z[-1], n)
        delta = abs(self.z[:] - ztemp[:])
        if np.max(delta) < 1e-9:
            return True
        else:
            return False


class Source(Array):
    """Specifies attributes of acoustic source array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    """

    def __init__(self, z: float):
        super().__init__(z)


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
    r_offsets : array, default=0
        Vector of receiver range offsets [m] to account for array tilt.
    n_offsets : int, default=1
        Length of vector of range offsets (r_offsets).
    """

    def __init__(
        self,
        z: float,
        # r_max: float,
        r: float,
        # nr: int=None,
        # dr: float=None,
        # r_min: float=1e-3,
        r_offsets: float = 0,
    ):
        super().__init__(z)
        self.r = np.atleast_1d(r)
        if self.r[0] == 0:
            self.r = self.r[1:]
        self.r_min = np.min(self.r)
        self.r_max = np.max(self.r)
        self.nr = len(self.r)
        # self.r_min = r_min
        # self.r_max = r_max
        # if r is not None:
        #     self.r = r
        #     self.nr = len(r)
        #     self.r_max =
        # elif (nr is None) and (dr is not None):
        #     self.dr = dr / 1e3
        #     self.r = np.arange(self.r_min, self.r_max, self.dr)
        #     self.nr = len(self.r)
        # elif (nr is not None) and (dr is None):
        #     self.nr = nr
        #     self.r = np.linspace(self.r_min, self.r_max, self.nr)
        #     self.dr = 1e3 * (self.r[1] - self.r[0])
        # elif (nr is None) and (dr is None):
        #     # raise ValueError("Range resolution undefined.")
        #     self.r = self.r_max
        self.r_offsets = r_offsets
        self.n_offsets = len(np.atleast_1d(r_offsets))


class SoundSpeedProfile:
    def __init__(self, z, c_p, rho=1.0, c_s=0.0, a_p=0.0, a_s=0.0):
        self.z = np.atleast_1d(z)
        n = len(self.z)
        self.c_p = np.atleast_1d(c_p)
        self.c_s = np.atleast_1d(c_s)
        self.rho = np.atleast_1d(rho)
        self.a_p = np.atleast_1d(a_p)
        self.a_s = np.atleast_1d(a_s)

        if (
            (n < len(self.c_p))
            or (n < len(self.c_s))
            or (n < len(self.rho))
            or (n < len(self.a_p))
            or (n < len(self.a_s))
        ):
            raise ValueError("Number of data points exceeds depth points.")

        if (n > 1) and (len(self.c_p) == 1):
            self.c_p = np.tile(self.c_p, n)
        if (n > 1) and (len(self.c_s) == 1):
            self.c_s = np.tile(self.c_s, n)
        if (n > 1) and (len(self.rho) == 1):
            self.rho = np.tile(self.rho, n)
        if (n > 1) and (len(self.a_p) == 1):
            self.a_p = np.tile(self.a_p, n)
        if (n > 1) and (len(self.a_s) == 1):
            self.a_s = np.tile(self.a_s, n)


class Layer:
    def __init__(self, ssp, nmesh=0, sigma=0):
        self.ssp = ssp
        self.nmesh = nmesh
        self.sigma = sigma
        self.z_max = self.ssp.z.max()


class Halfspace:
    def __init__(self, opt, z, c_p, c_s, rho, a_p, a_s):
        self.opt = opt
        self.z = z
        self.c_p = c_p
        self.c_s = c_s
        self.rho = rho
        self.a_p = a_p
        self.a_s = a_s


class Top(Halfspace):
    def __init__(
        self, opt="CVF    ", z=None, c_p=None, c_s=0.0, rho=None, a_p=0.0, a_s=0.0
    ):
        super().__init__(opt, z, c_p, c_s, rho, a_p, a_s)
        if self.opt[1] == "A":
            if (z is None) or (c_p is None) or (rho is None):
                raise ValueError("Top halfspace properties undefined.")


class Bottom(Halfspace):
    def __init__(
        self,
        opt="R",
        sigma=0.0,
        z=None,
        c_p=None,
        c_s=0.0,
        rho=None,
        a_p=0.0,
        a_s=0.0,
        mz=None,
    ):
        super().__init__(opt, z, c_p, c_s, rho, a_p, a_s)
        self.sigma = (
            sigma  # <-- Which sigma is this?  From one of the layers or its own?
        )

        if self.opt[0] == "A":
            if (z is None) or (c_p is None) or (rho is None):
                raise ValueError("Bottom halfspace properties undefined.")

        elif self.opt[0] == "G":
            self.mz = mz
            if (z is None) or (mz is None):
                raise ValueError("Bottom halfspace properties undefined.")


class BioLayers:
    def __init__(self, n, z1, z2, f0, Q, a0):
        self.n = n
        self.z1 = z1
        self.z2 = z2
        self.f0 = f0
        self.Q = Q
        self.a0 = a0


class ModelConfiguration:
    def __init__(
        self, title, freq, layers, top, bottom, biolayers=None, tmpdir=Path.cwd()
    ):
        self.title = title
        self.freq = freq
        self.layers = layers
        self.nmedia = len(layers)
        self.top = top
        self.bottom = bottom
        self.biolayers = biolayers
        self.tmpdir = enforce_path_type(tmpdir)

    def run_model(self, model):
        with self._working_directory(self.tmpdir):
            retcode = subprocess.call(
                f"{model}.exe {self.title}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return retcode

    def _check_tmpdir(self):
        self.tmpdir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    @contextlib.contextmanager
    def _working_directory(path):
        prev_cwd = Path.cwd()
        os.chdir(path)
        print(path)
        try:
            yield
        finally:
            os.chdir(prev_cwd)
            print(prev_cwd)

    def _write_envfil(self):
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
            # Block 4b - Biologic Layers (not implemented)
            if self.biolayers is not None:
                pass
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
                    + "  \t ! Upper halfspace \r\n"
                )
            # Block 6b - Bottom Halfspace from Grain Size
            elif self.bottom.opt[0] == "G":
                f.write(f"   {self.bottom.z:6.2f} {self.bottom.mz:6.2f} ! zb mz\r\n")

        return envfil


class Parameterization:
    def __init__(self, parameters=None, path=None):
        if (parameters is not None) and (path is None):
            self.parameters = parameters
            self.parse_parameters()
        elif (parameters is None) and (path is not None):
            self._load_config(path)
            self.parse_parameters()
        elif (parameters is None) and (path is None):
            self.parameters = parameters
        else:
            raise ValueError(
                "Variables 'parameters' and 'path' both set; only one accepted."
            )

    def _load_config(self, path):
        config = dict()
        if not isinstance(path, list):
            path = [path]
        [config.update(self._read_config(enforce_path_type(p))) for p in path]
        self.parameters = config

    @staticmethod
    def _read_config(path):
        with open(path, "r") as f:
            config = json.load(f)
        return config

    def parse_parameters(self):
        self._parse_misc_parameters()
        self._parse_top_parameters()
        self._parse_layer_parameters()
        self._parse_bottom_parameters()
        self._parse_source_parameters()
        self._parse_receiver_parameters()
        self._parse_freq_parameters()

    def write_config(self, path=None, fname="config"):
        if path is None:
            path = self.tmpdir
        else:
            self._check_path(path)
        self._write_json(path, fname)
        self._write_conf(path, fname)

    @staticmethod
    def _check_path(path):
        p = Path(path)
        if not p.is_dir():
            p.mkdir(parents=True, exist_ok=True)

    def _parse_bottom_parameters(self):
        self.bottom = Bottom(
            opt=self.parameters.get("bot_opt", "A"),
            sigma=self.parameters.get("bot_sigma", 0.0),
            z=self.parameters.get("bot_z", self.layers[-1].z_max + 1),
            c_p=self.parameters.get("bot_c_p"),
            c_s=self.parameters.get("bot_c_s", 0.0),
            rho=self.parameters.get("bot_rho"),
            a_p=self.parameters.get("bot_a_p", 0.0),
            a_s=self.parameters.get("bot_a_s", 0.0),
            mz=self.parameters.get("bot_mz"),
        )

    def _parse_freq_parameters(self):
        self.freq = self.parameters.get("freq", 100.0)

    def _parse_layer_parameters(self):
        self.layers = [
            Layer(SoundSpeedProfile(**kwargs))
            for kwargs in self.parameters.get("layerdata")
        ]

    def _parse_misc_parameters(self):
        self.title = self.parameters.get("title", "Default")
        self.tmpdir = self.parameters.get("tmpdir", "tmp")
        self.tmpdir = enforce_path_type(self.tmpdir)
        self.model = self.parameters.get("model")

    def _parse_receiver_parameters(self):
        self.receiver = Receiver(
            z=self.parameters.get("rec_z"),
            r=self.parameters.get("rec_r"),
            r_offsets=self.parameters.get("rec_r_offsets", 0.0),
        )

    def _parse_source_parameters(self):
        self.source = Source(z=self.parameters.get("src_z"))

    def _parse_top_parameters(self):
        self.top = Top(
            opt=self.parameters.get("top_opt", "CVF    "),
            z=self.parameters.get("top_z"),
            c_p=self.parameters.get("top_c_p"),
            c_s=self.parameters.get("top_c_s", 0.0),
            rho=self.parameters.get("top_rho"),
            a_p=self.parameters.get("top_a_p", 0.0),
            a_s=self.parameters.get("top_a_s", 0.0),
        )

    def _write_conf(self, path, fname):
        config = ConfigParser()
        config["PARAMETERS"] = self.parameters
        with open(path / f"{fname}.ini", "w+") as f:
            config.write(f)

    def _write_json(self, path, fname):
        with open(path / f"{fname}.json", "w+") as f:
            json.dump(self.parameters, f)


def enforce_path_type(path):
    if isinstance(path, str):
        path = Path(path)
    return path
