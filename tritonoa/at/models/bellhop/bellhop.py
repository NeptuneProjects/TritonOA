# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from tritonoa.at.env.array import Receiver, Source
from tritonoa.at.env.env import AcousticsToolboxEnvironment
from tritonoa.at.models.bellhop.beams import Beams
from tritonoa.at.models.model import AcousticsToolboxModel
from tritonoa.utils import clean_up_files


class BellhopModelExtensions(Enum):
    ENV = "env"
    PRT = "prt"
    RAY = "ray"


class BellhopRunType(Enum):
    R = "R"  #  Generates a ray file
    E = "E"  #  Generates an eigenray file
    A = "A"  #  Generates an amplitude-delay file (ascii)
    a = "a"  #  Generates an amplitude-delay file (binary)
    C = "C"  #  Coherent TL calculation
    I = "I"  #  Incoherent TL calculation
    S = "S"  #  Semicoherent TL calculation (Lloyd mirror source pattern)


class BellhopBeamType(Enum):
    G = "G"  #  Geometric hat beams in Cartesian coordinates (default)
    g = "g"  #  Geometric hat beams in ray-centered coordinates
    B = "B"  #  Geometric Gaussian beams


class BellhopPatternFileChoice(Enum):
    READ = "*"  # read in a source beam pattern file
    DONT_READ = "O"  # don't (default)


class BellhopSourceType(Enum):
    R = "R"  # point source (cylindrical coordinates) (default)
    X = "X"  # line source (cartesian coordinates)


class BellhopGridType(Enum):
    R = "R"  # rectilinear grid (default)
    I = "I"  # irregular grid


@dataclass
class BeamFan:
    alpha: list[float] = field(default_factory=lambda: [-11.0, 11.0])
    nbeams: int = 51
    isingle: Optional[int] = None


@dataclass
class BellhopOptions:
    run_type: str = BellhopRunType.R.value
    beam_type: str = BellhopBeamType.G.value
    pattern_file_choice: str = BellhopPatternFileChoice.DONT_READ.value
    source_type: str = BellhopSourceType.R.value
    grid_type: str = BellhopGridType.R.value

    def __post_init__(self):
        self._check_options()
        self.opt = ""
        for field in self.__dataclass_fields__.keys():
            self.opt += getattr(self, field)

    def _check_options(self):
        if self.run_type not in [i.value for i in BellhopRunType]:
            raise ValueError(f"Invalid run type: {self.run_type}")
        if self.beam_type not in [i.value for i in BellhopBeamType]:
            raise ValueError(f"Invalid beam type: {self.beam_type}")
        if self.pattern_file_choice not in [i.value for i in BellhopPatternFileChoice]:
            raise ValueError(f"Invalid pattern file choice: {self.pattern_file_choice}")
        if self.source_type not in [i.value for i in BellhopSourceType]:
            raise ValueError(f"Invalid source type: {self.source_type}")
        if self.grid_type not in [i.value for i in BellhopGridType]:
            raise ValueError(f"Invalid grid type: {self.grid_type}")


@dataclass
class NumericalIntegrator:
    zbox: float  # The maximum depth to trace a ray (m).
    rbox: float  # The maximum range to trace a ray (km).
    step: int = 0  # The step size used for tracing the rays (m). (Use 0 to let BELLHOP choose the step size.)


@dataclass(kw_only=True)
class BellhopEnvironment(AcousticsToolboxEnvironment):
    source: Source
    receiver: Receiver
    options: BellhopOptions = field(default_factory=BellhopOptions)
    fan: BeamFan = field(default_factory=BeamFan)
    integrator: NumericalIntegrator

    def write_envfil(self) -> Path:
        def _check_single_trace():
            if self.top.opt[5] == "I" and self.fan.isingle is None:
                raise ValueError(
                    "Single beam index must be specified for single trace."
                )
            if self.top.opt[5] == " " and self.fan.isingle is not None:
                raise ValueError(
                    "Top option single trace not set but single trace index specified."
                )

        opt = self.options.opt
        envfil = self._write_envfil()
        with open(envfil, "a") as f:
            # Block 7 - Source/Receiver Depths and Ranges
            # Number of Source Depths
            f.write(f"{self.source.nz:5d} \t \t \t \t ! NSD")
            # Source Depths [m]
            if (self.source.nz > 1) and self.source.equally_spaced():
                f.write(f"\r\n    {self.source.z[0]:6f} {self.source.z[-1]:6f}")
            else:
                f.write(f"\r\n    ")
                for zz in self.source.z:
                    f.write(f"{zz:6f} ")
            f.write("/ \t ! SD(1)  ... (m) \r\n")
            # Number of Receiver Depths
            f.write(f"{self.receiver.nz:5d} \t \t \t \t ! NRD")
            # Receiver Depths [m]
            if (self.receiver.nz > 1) and self.receiver.equally_spaced():
                f.write(f"\r\n    {self.receiver.z[0]:6f} {self.receiver.z[-1]:6f}")
            else:
                f.write(f"\r\n    ")
                for zz in self.receiver.z:
                    f.write(f"{zz:6f} ")
            f.write("/ \t ! RD(1)  ... (m) \r\n")
            # Number of Receiver Ranges
            f.write(f"{self.receiver.nr} \t \t \t \t ! NR")
            # Receiver Ranges [km]
            f.write(f"\r\n    ")
            for rr in self.receiver.r:
                f.write(f"{rr:6f} ")
            # Block 8 - Run Type
            f.write(f"\r\n'{opt}' \t \t \t ! Run Type")
            # Block 9 - Beam Fan
            _check_single_trace()
            if self.fan.isingle is not None:
                isingle = self.fan.isingle
            else:
                isingle = ""
            f.write(f"\r\n{self.fan.nbeams} {isingle} \t \t \t \t \t ! NBEAMS")
            if len(self.fan.alpha) == 2:
                f.write(
                    f"\r\n{self.fan.alpha[0]:6.2f} {self.fan.alpha[-1]:6.2f} / \t ! ALPHA(1:NBEAMS) (degrees)"
                )
            else:
                f.write(f"\r\n    ")
                for aa in self.fan.alpha:
                    f.write(f"{aa:6.2f} ")
                f.write(f"\t ! ALPHA(1:NBEAMS) (degrees)")
            # Block 10 - Numerical Integrator
            f.write(
                f"\r\n{self.integrator.step} {self.integrator.zbox} {self.integrator.rbox} \t \t \t \t ! STEP (m)  ZBOX (m)  RBOX (km)"
            )

        return envfil


class BellhopModel(AcousticsToolboxModel):
    model_name = "bellhop"

    def __init__(self, environment: BellhopEnvironment) -> None:
        super().__init__(environment)

    def run(
        self,
        model_path: Optional[Path] = None,
        keep_files: bool = False,
    ) -> None:
        """Returns modes, pressure field, rvec, zvec"""

        _ = self.environment.write_envfil()
        self.run_model(model_name=self.model_name, model_path=model_path)
        self.beams = Beams(self.environment.source, self.environment.receiver)
        self.beams.read_beams(self.environment.tmpdir / self.environment.title)
        if not keep_files:
            clean_up_files(
                self.environment.tmpdir,
                extensions=[i.value for i in BellhopModelExtensions],
                pattern=self.environment.title,
            )
