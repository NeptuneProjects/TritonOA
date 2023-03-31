#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from struct import unpack
from typing import Any, Optional, Union

import numpy as np

from tritonoa.at.env.array import Receiver, Source
from tritonoa.signal.sp import pressure_field


class Modes:
    def __init__(self, freq: float, source: Source, receiver: Receiver):
        self.freq = freq
        self.source = source
        self.receiver = receiver

    def read_modes(self, modfil: str, modes: Optional[Union[np.ndarray, list]] = None):
        """Read the modes produced by KRAKEN usage:
        keys are 'fname', 'freq', 'modes'
        'fname' and 'freq' are mandatory, 'modes' is if you only want a
        subset of modes
            [ Modes ] = read_modes_bin( filename, modes )
        filename is without the extension, which is assumed to be '.moA'
        freq is the frequency (involved for broadband runs)
        (you can use freq=0 if there is only one frequency)
        modes is an optional vector of mode indices

        derived from readKRAKEN.m    Feb 12, 1996 Aaron Thode

        Translated to python by Hunter Akins 2019

        Modes.M          number of modes
        Modes.k          wavenumbers
        Modes.z          sample depths for modes
        Modes.phi        modes

        Modes.Top.bc
        Modes.Top.cp
        Modes.Top.cs
        Modes.Top.rho
        Modes.Top.depth

        Modes.Bot.bc
        Modes.Bot.cp
        Modes.Bot.cs
        Modes.Bot.rho
        Modes.Bot.depth

        Modes.N          Number of depth points in each medium
        Modes.Mater      Material type of each medium (acoustic or elastic)
        Modes.Nfreq      Number of frequencies
        Modes.Nmedia     Number of media
        Modes.depth      depths of interfaces
        Modes.rho        densities in each medium
        Modes.freqVec    vector of frequencies for which the modes were
                         calculated
        """

        self.modfil = f"{modfil}.mod"

        with open(self.modfil, "rb") as f:
            iRecProfile = 1
            # (first time only)
            lrecl = 4 * unpack("<I", f.read(4))[0]
            # Record length in bytes
            rec = iRecProfile - 1

            f.seek(rec * lrecl + 4)  # do I need to do this ?

            title = unpack("80s", f.read(80))
            nfreq = unpack("<I", f.read(4))[0]
            nmedia = unpack("<I", f.read(4))[0]
            ntot = unpack("<l", f.read(4))[0]
            nmat = unpack("<l", f.read(4))[0]
            N = []
            material = []

            if ntot < 0:
                print("No modes available to read.")
                return

            # N and material
            rec = iRecProfile
            f.seek(rec * lrecl)  # reposition to next level
            for _ in range(nmedia):
                # print(unpack('<I', f.read(4))[0])
                N.append(unpack("<I", f.read(4))[0])
                material.append(unpack("8s", f.read(8))[0])

            # depth and density
            rec = iRecProfile + 1
            f.seek(rec * lrecl)
            bulk = unpack("f" * 2 * nmedia, f.read(4 * 2 * nmedia))
            layer_depth = [bulk[i] for i in range(0, 2 * nmedia, 2)]
            layer_rho = [bulk[i + 1] for i in range(0, 2 * nmedia, 2)]

            # frequencies
            rec = iRecProfile + 2
            f.seek(rec * lrecl)
            freqVec = unpack("d", f.read(8))[0]
            freqVec = np.array(freqVec)

            # z
            rec = iRecProfile + 3
            f.seek(rec * lrecl)
            z = unpack("f" * ntot, f.read(ntot * 4))

            # read in the modes

            # identify the index of the frequency closest to the user-specified value
            freqdiff = abs(freqVec - self.freq)
            freq_index = np.argmin(freqdiff)

            # number of modes, m
            iRecProfile = iRecProfile + 4
            rec = iRecProfile

            # skip through the mode file to get to the chosen frequency
            for ifreq in range(freq_index + 1):
                f.seek(rec * lrecl)
                M = unpack("l", f.read(8))[0]

                # advance to the next frequency
                if ifreq < freq_index:
                    iRecProfile = (
                        iRecProfile + 2 + M + 1 + np.floor((2 * M - 1) / lrecl)
                    )
                    # advance to next profile
                    rec = iRecProfile
                    f.seek(rec * lrecl)

            if modes is None:
                modes = np.linspace(0, M - 1, M, dtype=int)
                # read all modes if the user didn't specify

            # Top and bottom halfspace info

            # Top
            rec = iRecProfile + 1
            f.seek(rec * lrecl)
            top_bc = unpack("c", f.read(1))[0]
            cp = unpack("ff", f.read(8))
            top_cp = complex(cp[0], cp[1])
            cs = unpack("ff", f.read(8))
            top_cs = complex(cs[1], cs[1])
            top_rho = unpack("f", f.read(4))[0]
            top_depth = unpack("f", f.read(4))[0]

            top = ModesHalfspace(
                bc=top_bc,
                z=top_depth,
                alphaR=top_cp.real,
                betaR=top_cs.real,
                alphaI=top_cp.imag,
                betaI=top_cs.imag,
                rho=top_rho,
            )

            # Bottom
            bot_bc = unpack("c", f.read(1))[0]
            cp = unpack("ff", f.read(8))
            bot_cp = complex(cp[0], cp[1])
            cs = unpack("ff", f.read(8))
            bot_cs = complex(cs[1], cs[1])
            bot_rho = unpack("f", f.read(4))[0]
            bot_depth = unpack("f", f.read(4))[0]

            bottom = ModesHalfspace(
                bc=bot_bc,
                z=bot_depth,
                alphaR=bot_cp.real,
                betaR=bot_cs.real,
                alphaI=bot_cp.imag,
                betaI=bot_cs.imag,
                rho=bot_rho,
            )

            rec = iRecProfile
            f.seek(rec * lrecl)
            # if there are modes, read them
            if M == 0:
                modes_phi = []
                modes_k = []
            else:
                modes_phi = np.zeros(
                    (nmat, len(modes)), dtype=np.complex64
                )  # number of modes

                for ii in range(len(modes)):
                    rec = iRecProfile + 2 + int(modes[ii])
                    f.seek(rec * lrecl)
                    phi = unpack(
                        "f" * 2 * nmat, f.read(2 * nmat * 4)
                    )  # Data is read columwise
                    phir = np.array([phi[i] for i in range(0, 2 * nmat, 2)])
                    phii = np.array([phi[i + 1] for i in range(0, 2 * nmat, 2)])
                    modes_phi[:, ii] = phir + complex(0, 1) * phii

                rec = iRecProfile + 2 + M
                f.seek(rec * lrecl)
                k = unpack("f" * 2 * M, f.read(4 * 2 * M))
                kr = np.array([k[i] for i in range(0, 2 * M, 2)])
                ki = np.array([k[i + 1] for i in range(0, 2 * M, 2)])
                modes_k = kr + complex(0, 1) * ki
                modes_k = np.array(
                    [modes_k[i] for i in modes], dtype=np.complex64
                )  # take the subset that the user specified

        self.title = title
        self.M = M
        self.z = np.array(z)
        self.k = modes_k
        self.phi = modes_phi
        self.top = top
        self.bottom = bottom
        self.N = N
        self.material = material
        self.nfreq = nfreq
        self.nmedia = nmedia
        self.layer_depth = layer_depth
        self.layer_rho = layer_rho
        self.freqVec = freqVec
        self._format_modes()
        return self.modfil

    def _format_modes(self) -> None:
        self.k = np.expand_dims(self.k, 1)
        phi = self.phi
        ind = np.argmin(abs(self.source.z - self.z))
        mask = np.zeros_like(self.z, dtype=bool)
        mask[ind] = True
        phi_src = phi[mask, :]
        if self.source.z in self.receiver.z:
            phi_rec = phi
        else:
            phi_rec = phi[np.invert(mask), :]
        self.phi_src = phi_src
        self.phi_rec = phi_rec

    def field(self) -> np.ndarray:
        self.p = pressure_field(
            self.phi_src,
            self.phi_rec,
            self.k,
            self.receiver.r * 1000,
            self.receiver.r_offsets,
        )
        return self.p


@dataclass
class ModesHalfspace:
    bc: Optional[Any] = None  # TODO: Clarify type
    z: np.ndarray = field(default_factory=np.array([]))
    alphaR: np.ndarray = field(default_factory=np.array([]))
    betaR: np.ndarray = field(default_factory=np.array([]))
    alphaI: np.ndarray = field(default_factory=np.array([]))
    betaI: np.ndarray = field(default_factory=np.array([]))
    rho: np.ndarray = field(default_factory=np.array([]))
