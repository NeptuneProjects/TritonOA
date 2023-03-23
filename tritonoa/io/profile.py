#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd


def read_ssp(fname, zcol, ccol, header=None):
    """Reads SSP from a delimited file.

    Parameters
    ----------
    fname : object (Path)
        Path to the file to be read.
    zcol : int
        Column index for depth data.
    ccol : int
        Column index for speed data.
    header : int
        Line number of header (default: None)

    Returns
    -------
    array
        Array of depth values.
    array
        Array of sound speed values.
    DataFrame
        DataFrame containing depth and sound speed values.
    """

    df = pd.read_csv(
        fname, sep=None, header=header, engine="python", skipinitialspace=True
    )
    df = df.drop(
        columns=df.columns[
            [i for i in list(range(len(df.columns))) if i not in (zcol, ccol)]
        ]
    )
    mapper = {k: v for k, v in zip(list(df.columns), ["depth", "speed"])}
    df = df.rename(columns=mapper)

    return df["depth"].values, df["speed"].values, df
