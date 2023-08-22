#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import contextlib
import os
from pathlib import Path
import subprocess
from typing import Any, Optional, Union

from tritonoa.at.env.env import AcousticsToolboxEnvironment


class UnknownCommandError(Exception):
    pass


class AcousticsToolboxModel(ABC):
    def __init__(self, environment: AcousticsToolboxEnvironment) -> None:
        self.environment = environment

    @abstractmethod
    def run(
        self,
        model_name: str,
        model_path: Optional[Union[str, bytes, os.PathLike]] = None,
        *args,
        **kwargs,
    ) -> Any:
        pass

    def run_model(
        self,
        model_name: str,
        model_path: Optional[Union[str, bytes, os.PathLike]] = None,
    ) -> int:
        if model_path is None:
            command = f"{model_name.lower()}.exe {self.environment.title}"
        else:
            command = (
                f"{str(model_path)}/{model_name.lower()}.exe {self.environment.title}"
            )

        try:
            return subprocess.run(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.environment.tmpdir,
            )
        except:
            raise UnknownCommandError(
                f"Unknown command: {str(model_path)}/{model_name.lower()}.exe"
            )
