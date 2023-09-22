# -*- coding: utf-8 -*-

import numpy as np

from tritonoa.at.env.array import Receiver, Source
from tritonoa.at.env.halfspace import Bottom, Top
from tritonoa.at.env.ssp import SoundSpeedProfileAT, SSPLayer
from tritonoa.at.models.kraken.kraken import KrakenEnvironment, KrakenModel
from tritonoa.at.models.kraken.modes import format_adiabatic_modes
from tritonoa.sp.physics import pressure_field


def build_kraken_environment(parameters: dict) -> KrakenEnvironment:
    """Helper function to generate a KrakenEnvironment from a dictionary.

    Args:
        parameters: Dictionary with the parameters for the KrakenEnvironment.

    Returns:
        KrakenEnvironment object.
    """
    layers = [
        SSPLayer(SoundSpeedProfileAT(**layer_kwargs))
        for layer_kwargs in parameters.get("layerdata")
    ]

    return KrakenEnvironment(
        title=parameters.get("title", "Kraken"),
        freq=parameters.get("freq", 100.0),
        layers=layers,
        top=Top(
            opt=parameters.get("top_opt", "CVF    "),
            z=parameters.get("top_z"),
            c_p=parameters.get("top_c_p"),
            c_s=parameters.get("top_c_s", 0.0),
            rho=parameters.get("top_rho"),
            a_p=parameters.get("top_a_p", 0.0),
            a_s=parameters.get("top_a_s", 0.0),
        ),
        bottom=Bottom(
            opt=parameters.get("bot_opt", "A"),
            sigma=parameters.get("bot_sigma", 0.0),
            z=parameters.get("bot_z", layers[-1].z_max + 1),
            c_p=parameters.get("bot_c_p"),
            c_s=parameters.get("bot_c_s", 0.0),
            rho=parameters.get("bot_rho"),
            a_p=parameters.get("bot_a_p", 0.0),
            a_s=parameters.get("bot_a_s", 0.0),
            mz=parameters.get("bot_mz"),
        ),
        tmpdir=parameters.get("tmpdir", "tmp"),
        source=Source(z=parameters.get("src_z", 1.0)),
        receiver=Receiver(
            z=parameters.get("rec_z", 1.0),
            r=parameters.get("rec_r", 1.0),
            tilt=parameters.get("tilt", None),
            azimuth=parameters.get("azimuth", None),
            z_pivot=parameters.get("z_pivot", None),
        ),
        clow=parameters.get("clow", 1500.0),
        chigh=parameters.get("chigh", 1600.0),
    )


def run_kraken(parameters: dict) -> np.ndarray:
    """Range-independent Kraken model.

    Args:
        parameters: Dictionary with the parameters for the KrakenEnvironment.

    Returns:
        Complex pressure field with dimension (depth x range).
    """
    environment = build_kraken_environment(parameters)
    # Instantiate & Run Model
    kmodel = KrakenModel(environment)
    kmodel.run(model_name=parameters.get("model", "KRAKEN"), fldflag=True)
    # Return Complex Pressure at Receiver
    return kmodel.modes.p


def run_kraken_adiabatic(parameters: dict) -> np.ndarray:
    """Range-dependent Kraken model using adiabatic approximation.

    Args:
        parameters: Dictionary with the parameters for the KrakenEnvironment.

    Returns:
        Complex pressure field with dimension (depth x range).
    """

    # Instantiate & Run Source Model
    parameters_src = parameters.get("src")
    environment_src = build_kraken_environment(parameters_src)
    kmodel_src = KrakenModel(environment_src)
    kmodel_src.run(model_name=parameters_src.get("model", "KRAKEN"), fldflag=False)

    # Instantiate & Run Receiver Model
    parameters_rec = parameters.get("rec")
    environment_rec = build_kraken_environment(parameters_rec)
    kmodel_rec = KrakenModel(environment_rec)
    kmodel_rec.run(model_name=parameters_rec.get("model", "KRAKEN"), fldflag=False)

    # Format Adiabatic Modes
    phi_src, phi_rec, k = format_adiabatic_modes(kmodel_src.modes, kmodel_rec.modes)

    # Return Complex Pressure at Receiver
    return pressure_field(
        phi_src,
        phi_rec,
        k,
        kmodel_rec.modes.receiver.r * 1000,
        kmodel_rec.modes.receiver.r_offsets,
    )
