#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from math import ceil, floor
import os
from pathlib import Path
from struct import unpack
from typing import Optional, Union

import numpy as np


class SIOReadError(Exception):
    pass


class SIOReadWarning(Warning):
    pass


class SIODataHandler:
    def __init__(self, files: list) -> None:
        self.files = sorted(files)

    @staticmethod
    def load_merged(
        fname: Union[str, bytes, os.PathLike]
    ) -> tuple[np.ndarray, np.ndarray]:
        data = np.load(fname)
        return data["X"], data["t"]

    def to_numpy(
        self,
        channels_to_remove: Union[int, list[int]] = -1,
        destination: Optional[Union[str, bytes, os.PathLike]] = None,
    ) -> None:
        for f in self.files:
            data, header = sioread(f)
            if channels_to_remove is not None:
                data = np.delete(data, np.s_[channels_to_remove], axis=1)

            if destination is not None:
                if isinstance(destination, str):
                    destination = Path(destination)
                f = destination / f.name

            np.save(f, data)
            np.save(f.parent / (f.name + "_header"), header)

    # Merge data according to datetimes
    def merge(
        self,
        base_time: str,
        start: str,
        end: str,
        fs: float,
        channels_to_remove: Optional[Union[int, list[int]]] = None,
        destination: Union[str, bytes, os.PathLike] = "merged.npz",
    ) -> tuple[np.ndarray, np.ndarray]:
        # Load data from files
        data = []
        for f in self.files:
            data.append(np.load(f))

        data = np.concatenate(data)
        if channels_to_remove is not None:
            data = np.delete(data, np.s_[channels_to_remove], axis=1)

        # Define time vector [s]
        t = np.linspace(0, (data.shape[0] - 1) / fs, data.shape[0])
        # Specify starting file datetime
        base_time = datetime.datetime.strptime(base_time, "%y%j %H:%M")
        # Specify analysis starting datetime
        start = datetime.datetime.strptime(start, "%y%j %H:%M")
        # Specify analysis ending datetime
        end = datetime.datetime.strptime(end, "%y%j %H:%M")
        # Create datetime vector
        dt = np.array([base_time + datetime.timedelta(seconds=i) for i in t])
        # Find indeces of analysis data
        idx = (dt >= start) & (dt < end)
        # Remove extraneous data
        data = data[idx]
        t = t[idx]
        # Save to file
        np.savez(destination, X=data, t=t)

        return data, t


def convert_sio_to_npy(source: os.PathLike, destination: os.PathLike) -> None:
    for f in source:
        X, header = sioread(f)
        np.savez(destination / f.name, X, header)


def sioread(
    fname: Union[str, bytes, os.PathLike],
    s_start: int = 1,
    Ns: int = -1,
    channels: list[int] = [],
    inMem: bool = True,
) -> tuple[np.ndarray, dict]:
    """Translation of Jit Sarkar's sioread.m to Python (which was a
    modification of Aaron Thode's with contributions from Geoff Edelman,
    James Murray, and Dave Ensberg).
    Translated by Hunter Akins, 4 June 2019
    Modified by William Jenkins, 6 April 2022

    Parameters
    ----------
    fname : str
        Name/path to .sio data file to be read.
    s_start : int, default=1
        Sample number from which to begin reading. Must be an integer
        multiple of the record number. To get the record number you can
        run the script with s_start = 1 and then check the header for
        the info.
    Ns : int, default=-1
        Total samples to read
    channels : list (int), default=[]
        Which channels to read (default all) (indexes at 0).
        Channel -1 returns header only, X is empty.=
    inMem : bool, default=True
        Perform data parsing in ram (default true).
        False: Disk intensive, memory efficient. Blocks read
        sequentially, keeping only requested channels. Not yet
        implemented
        True: Disk efficient, memory intensive. All blocks read at once,
        requested channels are selected afterwards.

    Returns
    -------
    X : array (Ns, Nc)
        Data output matrix.
    header : dict
        Descriptors found in file header.
    """

    def endian_check(f: os.PathLike) -> str:
        endian = ">"
        f.seek(28)
        bs = unpack(endian + "I", f.read(4))[0]  # should be 32677
        if bs != 32677:
            endian = "<"
            f.seek(28)
            bs = unpack(endian + "I", f.read(4))[0]  # should be 32677
            if bs != 32677:
                raise SIOReadError("Problem with byte swap constant:" + str(bs))
        return endian

    def validate_channels(channels: list[int], Nc: int) -> list[int]:
        if len(channels) == 0:
            channels = list(range(Nc))  # 	fetch all channels
        if len([x for x in channels if (x < 0) or (x > (Nc - 1))]) != 0:
            raise SIOReadError("Channel #s must be within range 0 to " + str(Nc - 1))
        return channels

    with open(fname, "rb") as f:
        endian = endian_check(f)
        f.seek(0)
        ID = int(unpack(endian + "I", f.read(4))[0])  # ID Number
        Nr = int(unpack(endian + "I", f.read(4))[0])  # # of Records in File
        BpR = int(unpack(endian + "I", f.read(4))[0])  # # of Bytes per Record
        Nc = int(unpack(endian + "I", f.read(4))[0])  # # of channels in File
        BpS = int(unpack(endian + "I", f.read(4))[0])  # # of Bytes per Sample
        if BpS == 2:
            dtype = "h"
        else:
            dtype = "f"
        tfReal = unpack(endian + "I", f.read(4))[0]  # 0 = integer, 1 = real
        SpC = unpack(endian + "I", f.read(4))[0]  # # of Samples per Channel
        bs = unpack(endian + "I", f.read(4))[0]  # should be 32677
        fname = unpack("24s", f.read(24))  # File name
        comment = unpack("72s", f.read(72))  # Comment String

        RpC = ceil(Nr / Nc)  # # of Records per Channel
        SpR = int(BpR / BpS)  # # of Samples per Record

        # Header object, for output
        header = {}
        header["ID"] = ID
        header["Nr"] = Nr
        header["BpR"] = BpR
        header["Nc"] = Nc
        header["BpS"] = BpS
        header["tfReal"] = tfReal
        header["SpC"] = SpC
        header["RpC"] = RpC
        header["SpR"] = SpR
        header["fname"] = fname
        header["comment"] = comment
        header["bs"] = bs
        header[
            "Description"
        ] = """
                    ID = ID Number
                    Nr = # of Records in File
                    BpR = # of Bytes per Record
                    Nc = # of channels in File
                    BpS = # of Bytes per Sample
                    tfReal = 0 - integer, 1 - real
                    SpC = # of Samples per Channel
                    fname = File name
                    comment = Comment String
                    bs = Endian check value, should be 32677
                    """

        # If either channel or # of samples is 0, then return just header
        if (Ns == 0) or ((len(channels) == 1) and (channels[0] == -1)):
            X = []
            return X, header

        # Recheck parameters against header info
        Ns_max = SpC - s_start + 1
        if Ns == -1:
            Ns = Ns_max  # 	fetch all samples from start point
        if Ns > Ns_max:
            SIOReadWarning(
                f"More samples requested than present in data file. Returning max num samples: {Ns_max}"
            )
            Ns = Ns_max

        # Check validity of channel list
        channels = validate_channels(channels, Nc)

        ## Read in file according to specified method
        # Calculate file offsets
        # Header is size of 1 Record at beginning of file
        r_hoffset = 1
        # Starting and total records needed from file
        r_start = int(floor((s_start - 1) / SpR) * Nc + r_hoffset)
        r_total = int(ceil(Ns / SpR) * Nc)

        # Aggregate loading
        if inMem:
            # Move to starting location
            f.seek(r_start * BpR)

            # Read in all records into single column
            if dtype == "f":
                Data = unpack(endian + "f" * r_total * SpR, f.read(r_total * SpR * 4))
            else:
                Data = unpack(endian + "h" * r_total * SpR, f.read(r_total * SpR * 2))
            count = len(Data)
            Data = np.array(Data)  # cast to numpy array
            if count != r_total * SpR:
                raise SIOReadError("Not enough samples read from file")

            # Reshape data into a matrix of records
            Data = np.reshape(Data, (r_total, SpR)).T

            # 	Select each requested channel and stack associated records
            m = int(r_total / Nc * SpR)
            n = len(channels)
            X = np.zeros((m, n))
            for i in range(len(channels)):
                chan = channels[i]
                blocks = np.arange(chan, r_total, Nc, dtype="int")
                tmp = Data[:, blocks]
                X[:, i] = tmp.T.reshape(m, 1)[:, 0]

            # Trim unneeded samples from start and end of matrix
            trim_start = int((s_start - 1) % SpR)
            if trim_start != 0:
                X = X[trim_start:, :]
            [m, tmp] = np.shape(X)
            if m > Ns:
                X = X[: int(Ns), :]
            if m < Ns:
                raise SIOReadError(
                    f"Requested # of samples not returned. Check that s_start ({s_start}) is multiple of rec_num: {SpR}"
                )

    return X, header

    # class SioStream_:


#     """
#     Written by Hunter Akins, 4 June 2019
#     data object implementing indexing and return sequential data
#     Indexing starts out 0, but sioread indexes at 1, so I need to add 1 to all keys
#     """

#     def __init__(self, fname):
#         s_start, Ns = 1, 1
#         inp = {"fname": fname, "s_start": s_start, "Ns": Ns}
#         [tmp, hdr] = sioread(**inp)
#         # use header to get Nc and samples per channel
#         self.Nc = hdr["Nc"]
#         self.SpC = hdr["SpC"]
#         self.SpR = hdr["SpR"]
#         self.inp = inp

#     def __getitem__(self, key):
#         if isinstance(key, slice):
#             if key.step is None:
#                 step = 1
#             else:
#                 step = key.step
#             start = key.start
#             resid = start % self.SpR
#             if resid != 0:
#                 start -= resid
#                 self.inp["s_start"] = start + 1
#                 if key.stop is None:
#                     self.inp["Ns"] = 1
#                 else:
#                     self.inp["Ns"] = key.stop - key.start + resid
#                 [tmp, hdr] = sioread(**self.inp)
#                 tmp = tmp[resid:]  # truncate the unnecessary read at beg.
#                 return tmp
#         self.inp["s_start"] = key.start + 1
#         if key.stop is None:
#             self.inp["Ns"] = 1
#         else:
#             self.inp["Ns"] = key.stop - key.start
#         [tmp, hdr] = sioread(**self.inp)
#         return tmp
