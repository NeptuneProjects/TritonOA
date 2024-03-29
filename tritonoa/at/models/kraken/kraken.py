# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from tritonoa.at.env.array import Receiver, Source
from tritonoa.at.env.env import AcousticsToolboxEnvironment
from tritonoa.at.models.kraken.modes import Modes
from tritonoa.at.models.model import AcousticsToolboxModel
from tritonoa.utils import clean_up_files


class KrakenModelExtensions(Enum):
    ENV = "env"
    MOD = "mod"
    PRT = "prt"


class KrakenModels(Enum):
    KRAKEN = "kraken"
    KRAKENC = "krakenc"


@dataclass(kw_only=True)
class KrakenEnvironment(AcousticsToolboxEnvironment):
    source: Source
    receiver: Receiver
    clow: float = 0
    chigh: Optional[float] = None

    def write_envfil(self) -> Path:
        envfil = self._write_envfil()
        with open(envfil, "a") as f:
            # Block 7 - Phase Speed Limits
            f.write(
                f"{self.clow:6.0f} {self.chigh:6.0f} " + "\t \t ! cLow cHigh (m/s) \r\n"
            )
            # Block 8 - Maximum Range
            f.write(f"{self.receiver.r_max:8.2f} \t \t \t ! RMax (km) \r\n")
            # Block 9 - Source/Receiver Depths
            # Number of Source Depths
            f.write(f"{self.source.nz:5d} \t \t \t \t ! NSD")
            # Source Depths
            if (self.source.nz > 1) and self.source.equally_spaced():
                f.write(f"\r\n    {self.source.z[0]:6f} {self.source.z[-1]:6f}")
            else:
                f.write(f"\r\n    ")
                for zz in self.source.z:
                    f.write(f"{zz:6f} ")
            f.write("/ \t ! SD(1)  ... (m) \r\n")
            # Number of Receiver Depths
            f.write(f"{self.receiver.nz:5d} \t \t \t \t ! NRD")
            # Receiver Depths
            if (self.receiver.nz > 1) and self.receiver.equally_spaced():
                f.write(f"\r\n    {self.receiver.z[0]:6f} {self.receiver.z[-1]:6f}")
            else:
                f.write(f"\r\n    ")
                for zz in self.receiver.z:
                    f.write(f"{zz:6f} ")
            f.write("/ \t ! RD(1)  ... (m) \r\n")

        return envfil


class KrakenModel(AcousticsToolboxModel):
    def __init__(self, environment: KrakenEnvironment) -> None:
        super().__init__(environment)

    def run(
        self,
        model_name: str,
        model_path: Optional[Path] = None,
        fldflag: bool = False,
        keep_files: bool = False,
    ) -> None:
        _ = self.environment.write_envfil()
        self.run_model(model_name=model_name, model_path=model_path)
        self.modes = Modes(
            self.environment.freq, self.environment.source, self.environment.receiver
        )
        self.modes.read_modes(self.environment.tmpdir / self.environment.title)
        if fldflag:
            _ = self.modes.field()
        if not keep_files:
            clean_up_files(
                self.environment.tmpdir,
                extensions=[i.value for i in KrakenModelExtensions],
                pattern=self.environment.title,
            )
