#!/usr/bin/env python3

'''This module contains classes and functions required to interact with
the KRAKEN ocean acoustic modeling software.

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
'''

from pathlib import Path
from struct import unpack

import numpy as np

from tritonoa.core import ModelConfiguration, Layer, Source, SoundSpeedProfile, Receiver, Bottom, Top
from tritonoa.sp import pressure_field

class KRAKENModelConfiguration(ModelConfiguration):
    def __init__(
            self,
            title,
            freq,
            layers: list,
            top,
            bottom,
            source,
            receiver,
            clow=0,
            chigh=None,
            nprof=1,
            rprof=0.,
            biolayers=None,
            tmpdir=Path.cwd()
        ):
        super().__init__(title, freq, layers, top, bottom, biolayers, tmpdir)
        self.source = source
        self.receiver = receiver
        self.clow = clow
        if chigh is None:
            self.chigh = self.bottom.c_p
        else:
            self.chigh =  chigh
        self.nprof = nprof
        self.rprof = rprof
    
    
    def _write_envfil_KRAKEN(self):
        envfil = self._write_envfil()
        with open(envfil, 'a') as f:
            # Block 7 - Phase Speed Limits
            f.write(
                f"{self.clow:6.0f} {self.chigh:6.0f} " + \
                "\t \t ! cLow cHigh (m/s) \r\n"
            )
            # Block 8 - Maximum Range
            f.write(f"{self.receiver.r_max:8.2f} \t \t \t ! RMax (km \r\n")
            # Block 9 - Source/Receiver Depths
            # Number of Source Depths
            f.write(f"{self.source.nz:5d} \t \t \t \t ! NSD")
            # Source Depths
            # if (self.source.nz > 1) and self._equally_spaced(self.source.z):
            if (self.source.nz > 1) and self.source.equally_spaced():
                f.write(f"\r\n    {self.source.z[0]:6f} {self.source.z[-1]:6f}")
            else:
                f.write(f"\r\n    ")
                for zz in np.atleast_1d(self.source.z):
                    f.write(f"{zz:6f} ")
            f.write('/ \t ! SD(1)  ... (m) \r\n' )
            # Number of Receiver Depths
            f.write(f"{self.receiver.nz:5d} \t \t \t \t ! NRD")
            # Receiver Depths
            # if (self.receiver.nz > 1) and self._equally_spaced(self.receiver.z):
            if (self.receiver.nz > 1) and self.receiver.equally_spaced():
                f.write(
                    f"\r\n    {self.receiver.z[0]:6f} {self.receiver.z[-1]:6f}"
                )
            else:
                f.write(f"\r\n    ")
                for zz in np.atleast_1d(self.receiver.z):
                    f.write(f"{zz:6f} ")
            f.write('/ \t ! RD(1)  ... (m) \r\n' )
        
        return envfil


    def run(self, model="krakenc", fldflag=False, verbose=False):
        '''Returns modes, pressure field, rvec, zvec'''
        if verbose:
            print(f"Running {model.upper()}")
        _ = self._write_envfil_KRAKEN()
        self.run_model(model=model)
        self.modes = Modes(self.freq, self.source, self.receiver)
        self.modes.read_modes(self.tmpdir / self.title)
        if fldflag:
            _ = self.modes.field()
        

    # @staticmethod
    # def _equally_spaced(x):
    #     n = len(x)
    #     xtemp = np.linspace(x[0], x[-1], n)
    #     delta = abs(x[:] - xtemp[:])
    #     if np.max(delta) < 1e-9:
    #         return True
    #     else:
    #         return False


class Modes:
    def __init__(self, freq, source, receiver):
        self.freq = freq
        self.source = source
        self.receiver = receiver

    
    def read_modes(self, modfil, modes=None):
        '''
        Read the modes produced by KRAKEN
        usage:
        keys are 'fname', 'freq', 'modes'
        'fname' and 'freq' are mandatory, 'modes' is if you only want a subset of modes
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
        Modes.freqVec    vector of frequencies for which the modes were calculated
        '''

        self.modfil = f"{modfil}.mod"

        with open(self.modfil, 'rb') as f:
            iRecProfile = 1; # (first time only)
            lrecl = 4 * unpack('<I', f.read(4))[0]; # Record length in bytes
            rec = iRecProfile - 1;

            f.seek(rec * lrecl + 4) # do I need to do this ?

            title = unpack('80s', f.read(80))
            nfreq = unpack('<I', f.read(4))[0]
            nmedia = unpack('<I', f.read(4))[0]
            ntot = unpack('<l', f.read(4))[0]
            nmat = unpack('<l', f.read(4))[0]
            N = []
            material = []

            if ntot < 0:
                print("No modes available to read.")
                return

            # N and material
            rec   = iRecProfile
            f.seek(rec * lrecl) # reposition to next level
            for _ in range(nmedia):
                # print(unpack('<I', f.read(4))[0])
                N.append(unpack('<I', f.read(4))[0])
                material.append(unpack('8s', f.read(8))[0])
            
            # depth and density
            rec = iRecProfile + 1
            f.seek(rec * lrecl)
            bulk = unpack('f' * 2 * nmedia, f.read(4 * 2 * nmedia))
            layer_depth = [bulk[i] for i in range(0, 2 * nmedia, 2)]
            layer_rho = [bulk[i + 1] for i in range(0, 2 * nmedia, 2)]

            # frequencies
            rec = iRecProfile + 2;
            f.seek(rec * lrecl);
            freqVec = unpack('d', f.read(8))[0]
            freqVec = np.array(freqVec)

            # z
            rec = iRecProfile + 3
            f.seek(rec * lrecl)
            z = unpack('f' * ntot, f.read(ntot * 4))

            # read in the modes

            # identify the index of the frequency closest to the user-specified value
            freqdiff = abs(freqVec - self.freq);
            freq_index = np.argmin(freqdiff)

            # number of modes, m
            iRecProfile = iRecProfile + 4;
            rec = iRecProfile;

            # skip through the mode file to get to the chosen frequency
            for ifreq in range(freq_index+1):
                f.seek(rec * lrecl);
                M = unpack('l', f.read(8))[0]
            
            # advance to the next frequency
                if ifreq < freq_index:
                    iRecProfile = iRecProfile + 2 + M + 1 + \
                        np.floor((2 * M - 1) / lrecl);   # advance to next profile
                    rec = iRecProfile;
                    f.seek(rec * lrecl)

            if modes is None:
                modes = np.linspace(0, M - 1, M, dtype=int);    # read all modes if the user didn't specify

            # Top and bottom halfspace info

            # Top
            rec = iRecProfile + 1
            f.seek(rec * lrecl)
            top_bc = unpack('c', f.read(1))[0]
            cp = unpack('ff', f.read(8))
            top_cp = complex(cp[0], cp[1])
            cs = unpack('ff', f.read(8))
            top_cs = complex(cs[1], cs[1])
            top_rho = unpack('f', f.read(4))[0]
            top_depth = unpack('f', f.read(4))[0]

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
            bot_bc = unpack('c', f.read(1))[0]
            cp = unpack('ff', f.read(8))
            bot_cp = complex(cp[0], cp[1])
            cs = unpack('ff', f.read(8))
            bot_cs = complex(cs[1], cs[1])
            bot_rho = unpack('f', f.read(4))[0]
            bot_depth = unpack('f', f.read(4))[0]

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
                modes_k   = []
            else:
                modes_phi = np.zeros((nmat, len(modes)), dtype=np.complex64) # number of modes

                for ii in range(len(modes)):
                    rec = iRecProfile + 2 + int(modes[ii])
                    f.seek(rec * lrecl)
                    phi = unpack('f' * 2 * nmat, f.read(2 * nmat * 4)) # Data is read columwise
                    phir = np.array([phi[i] for i in range(0, 2 * nmat, 2)])
                    phii = np.array([phi[i+1] for i in range(0, 2 * nmat, 2)])
                    modes_phi[:, ii] = phir + complex(0, 1) * phii

                rec = iRecProfile + 2 + M;
                f.seek(rec * lrecl)
                k = unpack('f' * 2 * M, f.read(4 * 2 * M))
                kr = np.array([k[i] for i in range(0, 2 * M, 2)])
                ki = np.array([k[i+1] for i in range(0, 2 * M, 2)])
                modes_k = kr + complex(0, 1) * ki
                modes_k = np.array(
                    [modes_k[i] for i in modes], dtype=np.complex64
                ) # take the subset that the user specified

        self.title = title
        self.M = M
        self.z = z
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
    

    def _format_modes(self):
        self.k = np.expand_dims(self.k, 1)
        phi = self.phi
        mask = np.isclose(self.source.z, self.z)
        phi_src = phi[mask, :]
        if self.source.z in self.receiver.z:
            phi_rec = phi
        else:
            phi_rec = phi[np.invert(mask), :]
        self.phi_src = phi_src
        self.phi_rec = phi_rec
    

    def field(self):
        self.p = pressure_field(
            self.phi_src,
            self.phi_rec,
            self.k,
            self.receiver.r * 1000
        )
        return self.p


class ModesHalfspace:
    def __init__(
            self,
            bc=None,
            z=np.array([]),
            alphaR=np.array([]),
            betaR=np.array([]),
            alphaI=np.array([]),
            betaI=np.array([]),
            rho=np.array([]),
        ):
        self.bc = bc
        self.z = z
        self.alphaR = alphaR
        self.betaR = betaR
        self.alphaI = alphaI
        self.betaI = betaI
        self.rho = rho


def run_kraken(parameters):
    
    # Miscellaneous Parameters
    title = parameters.get("title", "Kraken")
    tmpdir = parameters.get("tmpdir", "tmp")
    model = parameters.get("model", "KRAKENC")

    # Top Parameters
    top = Top(
        opt=parameters.get("top_opt", "CVF    "),
        z=parameters.get("top_z"),
        c_p=parameters.get("top_c_p"),
        c_s=parameters.get("top_c_s", 0.),
        rho=parameters.get("top_rho"),
        a_p=parameters.get("top_a_p", 0.),
        a_s=parameters.get("top_a_s", 0.)
    )

    # Layer Parameters
    layers = [Layer(SoundSpeedProfile(**kwargs)) for kwargs in parameters.get("layerdata")]

    # Bottom Parameters
    bottom = Bottom(
        opt=parameters.get("bot_opt", "A"),
        sigma=parameters.get("bot_sigma", 0.),
        z=parameters.get("bot_z", layers[-1].z_max+1),
        c_p=parameters.get("bot_c_p"),
        c_s=parameters.get("bot_c_s", 0.),
        rho=parameters.get("bot_rho"),
        a_p=parameters.get("bot_a_p", 0.),
        a_s=parameters.get("bot_a_s", 0.),
        mz=parameters.get("bot_mz")
    )

    # Source Parameters
    source = Source(z=parameters.get("src_z"))

    # Receiver Parameters
    receiver = Receiver(
        z=parameters.get("rec_z"),
        r_max=parameters.get("rec_r_max"),
        nr=parameters.get("rec_nr"),
        dr=parameters.get("rec_dr"),
        r_min=parameters.get("rec_r_min", 1.e-3),
        r_offsets=parameters.get("rec_r_offsets", 0.)
    )

    # Freq/Mode Parameters
    freq = parameters.get("freq", 100.)
    clow = parameters.get("clow", 1500.)
    chigh = parameters.get("chigh", 1600.)

    # Instantiate Model
    kmodel = KRAKENModelConfiguration(
        title,
        freq,
        layers,
        top,
        bottom,
        source,
        receiver,
        clow=clow,
        chigh=chigh,
        tmpdir=tmpdir
    )

    # Run Model
    kmodel.run(fldflag=True, model=model)

    # Return Complex Pressure at Receiver
    return kmodel.modes.p