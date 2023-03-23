#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, Union


class UndefinedPropertyError(Exception):
    pass


@dataclass
class Halfspace:
    opt: str
    z: Optional[Union[float, None]] = None
    c_p: Optional[Union[float, None]] = None
    c_s: Optional[Union[float, None]] = 0.0
    rho: Optional[Union[float, None]] = None
    a_p: Optional[Union[float, None]] = 0.0
    a_s: Optional[Union[float, None]] = 0.0


@dataclass
class Top(Halfspace):
    opt: str = "CVF    "

    def __post_init__(self):
        self.validate_options()

    def validate_options(self) -> None:
        if self.opt[1] == "A":
            if (self.z is None) or (self.c_p is None) or (self.rho is None):
                raise UndefinedPropertyError(
                    "Top halfspace attributes `z` or `c_p` or `rho` undefined."
                )


@dataclass
class Bottom(Halfspace):
    opt: str = "R"
    sigma: Optional[Union[float, None]] = 0.0
    mz: Optional[Union[float, None]] = None

    def __post_init__(self):
        self.validate_options()

    def validate_options(self) -> None:
        if self.opt[0] == "A":
            if (self.z is None) or (self.c_p is None) or (self.rho is None):
                raise UndefinedPropertyError(
                    "Bottom halfspace attributes `z` or `c_p` or `rho` undefined."
                )

        elif self.opt[0] == "G":
            if (self.z is None) or (self.mz is None):
                raise UndefinedPropertyError(
                    "Bottom halfspace attributes `z` or `mz` undefined."
                )
