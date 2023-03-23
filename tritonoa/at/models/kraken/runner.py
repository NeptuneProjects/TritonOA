#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tritonoa.at.env.array import Receiver, Source
from tritonoa.at.env.halfspace import Top, Bottom
from tritonoa.at.env.ssp import SoundSpeedProfileAT, SSPLayer
from tritonoa.at.models.kraken.kraken import KrakenEnvironment, KrakenModel


def run_kraken(parameters):
    # Miscellaneous Parameters
    title = parameters.get("title", "Kraken")
    tmpdir = parameters.get("tmpdir", "tmp")
    model = parameters.get("model", "KRAKEN")

    # Top Parameters
    top = Top(
        opt=parameters.get("top_opt", "CVF    "),
        z=parameters.get("top_z"),
        c_p=parameters.get("top_c_p"),
        c_s=parameters.get("top_c_s", 0.0),
        rho=parameters.get("top_rho"),
        a_p=parameters.get("top_a_p", 0.0),
        a_s=parameters.get("top_a_s", 0.0),
    )

    # Layer Parameters
    layers = [
        SSPLayer(SoundSpeedProfileAT(**layer_kwargs))
        for layer_kwargs in parameters.get("layerdata")
    ]

    # Bottom Parameters
    bottom = Bottom(
        opt=parameters.get("bot_opt", "A"),
        sigma=parameters.get("bot_sigma", 0.0),
        z=parameters.get("bot_z", layers[-1].z_max + 1),
        c_p=parameters.get("bot_c_p"),
        c_s=parameters.get("bot_c_s", 0.0),
        rho=parameters.get("bot_rho"),
        a_p=parameters.get("bot_a_p", 0.0),
        a_s=parameters.get("bot_a_s", 0.0),
        mz=parameters.get("bot_mz"),
    )

    # Source Parameters
    source = Source(z=parameters.get("src_z"))

    # Receiver Parameters
    receiver = Receiver(
        z=parameters.get("rec_z"),
        r=parameters.get("rec_r"),
        tilt=parameters.get("tilt", None)
    )

    # Freq/Mode Parameters
    freq = parameters.get("freq", 100.0)
    clow = parameters.get("clow", 1500.0)
    chigh = parameters.get("chigh", 1600.0)

    # Instantiate Environment
    environment = KrakenEnvironment(
        title,
        freq,
        layers,
        top,
        bottom,
        tmpdir=tmpdir,
        source=source,
        receiver=receiver,
        clow=clow,
        chigh=chigh,
    )

    # Instantiate & Run Model
    kmodel = KrakenModel(environment)
    kmodel.run(model_name=model, fldflag=True)
    # Return Complex Pressure at Receiver
    return kmodel.modes.p
