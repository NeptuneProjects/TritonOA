#!/usr/bin/env python3

'''This module contains objects common to the various ocean acoustics
models in Acoustics Toolbox software.

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
'''

from pathlib import Path
import subprocess

import numpy as np


class Array:
    '''Specifies attributes of an acoustic array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    '''

    def __init__(self, z: float):
        self.z = np.atleast_1d(z)
        self.nz = len(np.atleast_1d(z))
    

    # @staticmethod
    def equally_spaced(self):
        n = len(self.z)
        ztemp = np.linspace(self.z[0], self.z[-1], n)
        delta = abs(self.z[:] - ztemp[:])
        if np.max(delta) < 1e-9:
            return True
        else:
            return False


class Source(Array):
    '''Specifies attributes of acoustic source array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    '''

    def __init__(self, z: float):
        super().__init__(z)


class Receiver(Array):
    '''Specifies attributes of acoustic receiver array.

    Attributes
    ----------
    z : array
        Vector containing depths of the array elements.
    nz : int
        Number of array elements.
    r_max : float
        Maximum range of receiver range vector; alternatively, if
        specified without nr or dr, sets the range of the receiver.
    r_min : float, default=1e-3
        Minimum range of receiver range vector.
    nr : int, default=None
        Number of elements in receiver range vector.
    dr : float, default=None
        Range resolution of receiver range vector.
    r_offsets : array, default=0
        Vector of receiver range offsets to account for array tilt.
    n_offsets : int, default=1
        Length of vector of range offsets (r_offsets).
    '''

    def __init__(
            self,
            z: float,
            r_max: float,
            nr: int=None,
            dr: float=None,
            r_min: float=1e-3,
            r_offsets: float=0
        ):
        super().__init__(z)
        self.r_min = r_min
        self.r_max = r_max
        if (nr is None) and (dr is not None):
            self.dr = dr / 1e3
            self.r = np.arange(self.r_min, self.r_max, self.dr)
            self.nr = len(self.r)
        elif (nr is not None) and (dr is None):
            self.nr = nr
            self.r = np.linspace(self.r_min, self.r_max, self.nr)
            self.dr = 1e3 * (self.r[1] - self.r[0])
        elif (nr is None) and (dr is None):
            # raise ValueError("Range resolution undefined.")
            self.r = self.r_max
        self.r_offsets = r_offsets
        self.n_offsets = len(np.atleast_1d(r_offsets))


class SoundSpeedProfile:
    def __init__(self, z, c_p, rho=1.0, c_s=0., a_p=0., a_s=0.):
        self.z = np.atleast_1d(z)
        n = len(self.z)
        self.c_p = np.atleast_1d(c_p)
        self.c_s = np.atleast_1d(c_s)
        self.rho = np.atleast_1d(rho)
        self.a_p = np.atleast_1d(a_p)
        self.a_s = np.atleast_1d(a_s)

        if (n < len(self.c_p)) \
            or (n < len(self.c_s)) \
            or (n < len(self.rho)) \
            or (n < len(self.a_p)) \
            or (n < len(self.a_s)):
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
            self,
            opt="CVF    ",
            z=None,
            c_p=None,
            c_s=0.,
            rho=None,
            a_p=0.,
            a_s=0.
        ):
        super().__init__(opt, z, c_p, c_s, rho, a_p, a_s)
        if self.opt[1] == "A":
            if (z is None) or (c_p is None) or (rho is None):
                raise ValueError("Top halfspace properties undefined.")


class Bottom(Halfspace):
    def __init__(
            self,
            opt="R",
            sigma=0.,
            z=None,
            c_p=None,
            c_s=0.,
            rho=None,
            a_p=0.,
            a_s=0.,
            mz=None
        ):
        super().__init__(opt, z, c_p, c_s, rho, a_p, a_s)
        self.sigma = sigma # <-- Which sigma is this?  From one of the layers or its own?

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
            self,
            title,
            freq,
            layers,
            top,
            bottom,
            biolayers=None,
            tmpdir=Path.cwd()
        ):
        self.title = title
        self.freq = freq
        self.layers = layers
        self.nmedia = len(layers)
        self.top = top
        self.bottom = bottom
        self.biolayers = biolayers
        if isinstance(tmpdir, str):
            tmpdir = Path(tmpdir)
        self.tmpdir = tmpdir
        # if tmpdir is None:
            # self.tmpdir = Path.cwd()
    

    def run_model(self, model):
        retcode = subprocess.call(
            f"{model}.exe {self.tmpdir / self.title}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return retcode
    
    
    def _write_envfil(self):
        envfil = self.tmpdir / f'{self.title}.env'
        self.tmpdir.mkdir(parents=True, exist_ok=True)
        with open(envfil, 'w') as f:
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
                    f"     {self.layers[0].ssp.z[0]:6.2f}" + \
                    f" {self.top.c_p:6.2f}" + \
                    f" {self.top.c_s:6.2f}" + \
                    f" {self.top.rho:6.2f}" + \
                    f" {self.top.a_p:6.2f}" + \
                    f" {self.top.a_s:6.2f}" + \
                    "  \t ! Upper halfspace \r\n"
                )
            # Block 4b - Biologic Layers (not implemented)
            if self.biolayers is not None:
                pass
            # Block 5 - Sound Speed Profile
            for layer in self.layers:
                f.write(
                    f"{layer.nmesh:5d} " + \
                    f"{layer.sigma:4.2f} " + \
                    f"{layer.z_max:6.2f} " + \
                    "\t ! N sigma max_layer_depth \r\n"
                )
                for zz in range(len(layer.ssp.z)):
                    f.write(
                        f"\t {layer.ssp.z[zz]:6.2f} " + \
                        f"\t {layer.ssp.c_p[zz]:6.2f} " + \
                        f"\t {layer.ssp.c_s[zz]:6.2f} " + \
                        f"\t {layer.ssp.rho[zz]:6.2f} " + \
                        f"\t {layer.ssp.a_p[zz]:6.2f} " + \
                        f"\t {layer.ssp.a_s[zz]:6.2f} " + \
                        "/ \t ! z cp cs rho ap as \r\n"
                    )        
            # Block 6 - Bottom Option
            f.write(
                f"'{self.bottom.opt}' {self.bottom.sigma:6.2f}" + \
                "  \t \t ! Bottom Option, sigma\r\n"
            )
            # Block 6a - Bottom Halfspace from Geoacoustic Parameters
            if self.bottom.opt[0] == "A":
                f.write(
                    f"     {self.bottom.z:6.2f}" + \
                    f" {self.bottom.c_p:6.2f}" + \
                    f" {self.bottom.c_s:6.2f}" + \
                    f" {self.bottom.rho:6.2f}" + \
                    f" {self.bottom.a_p:6.2f}" + \
                    f" {self.bottom.a_s:6.2f}" + \
                    "  \t ! Upper halfspace \r\n"
                )
            # Block 6b - Bottom Halfspace from Grain Size
            elif self.bottom.opt[0] == "G":
                f.write(
                    f"   {self.bottom.z:6.2f} {self.bottom.mz:6.2f} ! zb mz\r\n"
                )
            
        return envfil