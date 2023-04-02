#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import datetime
import logging
from math import ceil, floor
import os
from pathlib import Path
from struct import unpack
from typing import Optional, Union

import numpy as np

from tritonoa.data import DataStream
from tritonoa.sp import timefreq as tf

log = logging.getLogger(__name__)


class SIOReadError(Exception):
    pass


class SIOReadWarning(Warning):
    pass


@dataclass
class SIODataHeader:
    ID: Optional[int] = None
    Nr: Optional[int] = None
    BpR: Optional[int] = None
    Nc: Optional[int] = None
    BpS: Optional[int] = None
    tfReal: Optional[int] = None
    SpC: Optional[int] = None
    RpC: Optional[int] = None
    SpR: Optional[int] = None
    fname: Optional[str] = None
    comment: Optional[str] = None
    bs: Optional[int] = None

    @property
    def Description(self) -> str:
        return """
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


class SIODataHandler:
    def __init__(self, files: list) -> None:
        self.files = sorted(files)

    def convert_to_numpy(
        self,
        channels_to_remove: Union[int, list[int]] = -1,
        destination: Optional[Union[str, bytes, os.PathLike]] = None,
        max_workers=8,
    ) -> None:
        """Converts .sio files to .npy files. If channels_to_remove is not
        None, then the specified channels will be removed from the data.
        """

        log.info(
            f"Starting process pool with {max_workers} workers for {len(self.files)} files."
        )
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            [
                executor.submit(load_sio_save_numpy, f, channels_to_remove, destination)
                for f in self.files
            ]

    @staticmethod
    def load_merged(fname: Union[str, bytes, os.PathLike]) -> DataStream:
        """Loads merged numpy data from file and returns data and time."""
        return DataStream().load(fname)

    # Merge data according to datetimes
    def merge_numpy_files(
        self,
        base_time: str,
        start: str,
        end: str,
        fs: float,
        channels_to_remove: Optional[Union[int, list[int]]] = None,
        savepath: Optional[Union[str, bytes, os.PathLike]] = None,
    ) -> DataStream:
        """Loads and merges numpy data from files and returns data and time."""
        # Load data from files
        data = []
        for f in self.files:
            data.append(np.load(f))

        data = np.concatenate(data)
        if channels_to_remove is not None:
            data = np.delete(data, np.s_[channels_to_remove], axis=1)

        # Define time vector [s]
        t = tf.create_time_vector(data.shape[0], fs)
        # Specify starting file datetime
        base_time = datetime.datetime.strptime(base_time, "%y%j %H:%M")
        # Specify analysis starting datetime
        start = datetime.datetime.strptime(start, "%y%j %H:%M")
        # Specify analysis ending datetime
        end = datetime.datetime.strptime(end, "%y%j %H:%M")
        # Create datetime vector referencing base_time
        dt = tf.create_datetime_vector(t, base_time)
        # Find indeces of analysis data
        idx = tf.get_time_index(dt, start, end)
        # Remove extraneous data
        stream = DataStream(data[idx], t[idx])

        # Save to file
        if savepath is not None:
            stream.save(savepath)

        return stream


def load_sio_save_numpy(
    f: os.PathLike,
    channels_to_remove: list[int] = None,
    destination: Union[str, bytes, os.PathLike] = None,
) -> None:
    data, header = sioread(f)

    if channels_to_remove is not None:
        data = np.delete(data, np.s_[channels_to_remove], axis=1)

    if destination is not None:
        f = Path(destination) / f.name

    np.save(f, data)
    np.save(f.parent / (f.name + "_header"), header)
    log.info(f"{str(f)} saved to disk.")


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
        header = SIODataHeader(
            ID=ID,
            Nr=Nr,
            BpR=BpR,
            Nc=Nc,
            BpS=BpS,
            tfReal=tfReal,
            SpC=SpC,
            RpC=RpC,
            SpR=SpR,
            fname=fname,
            comment=comment,
            bs=bs,
        )

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
