# -*- coding: utf-8 -*-

from tritonoa.at.env.array import Receiver, Source
from tritonoa.at.env.halfspace import Bottom, Top
from tritonoa.at.env.ssp import SoundSpeedProfileAT, SSPLayer
from tritonoa.at.models.bellhop.bellhop import (
    BeamFan,
    BellhopEnvironment,
    BellhopModel,
    BellhopOptions,
    NumericalIntegrator,
)


def build_bellhop_environment(parameters: dict) -> BellhopEnvironment:
    """Helper function to generate a `BellhopEnvironment` from a dictionary.

    Args:
        parameters: Dictionary with the parameters for the `BellhopEnvironment`.

    Returns:
        `BellhopEnvironment` object.
    """
    layers = [
        SSPLayer(SoundSpeedProfileAT(**layer_kwargs))
        for layer_kwargs in parameters.get("layerdata")
    ]
    return BellhopEnvironment(
        title=parameters.get("title", "Bellhop"),
        freq=parameters.get("freq", 400.0),
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
            z=parameters.get("bot_z", layers[-1].z_max),
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
        options=BellhopOptions(
            run_type=parameters.get("run_type", "R"),
            beam_type=parameters.get("beam_type", "G"),
            pattern_file_choice=parameters.get("pattern_file_choice", "O"),
            source_type=parameters.get("source_type", "R"),
            grid_type=parameters.get("grid_type", "R"),
        ),
        fan=BeamFan(
            alpha=parameters.get("alpha", [-11.0, 11.0]),
            nbeams=parameters.get("nbeams", 51),
            isingle=parameters.get("isingle", None),
        ),
        integrator=NumericalIntegrator(
            zbox=parameters.get("zbox", 1000.0),
            rbox=parameters.get("rbox", 100.0),
            step=parameters.get("step", 0),
        ),
    )


def run_bellhop(parameters: dict, keep_files=False) -> BellhopModel:
    """Run Bellhop propagation model.

    Args:
        parameters: Dictionary with the parameters for the BellhopEnvironment.

    Returns:
        `BellhopModel` object containing ray trace results.
    """
    environment = build_bellhop_environment(parameters)
    model = BellhopModel(environment)
    model.run(keep_files=keep_files)
    return model
