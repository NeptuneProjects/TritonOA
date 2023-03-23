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
        with self._working_directory(self.environment.tmpdir):
            print(f"{model_name.lower()}.exe {self.environment.title}")
            if model_path is None:
                try:
                    retcode = subprocess.call(
                        f"{model_name.lower()}.exe {self.environment.title}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except:
                    raise UnknownCommandError(
                        f"Unknown command: {model_name.lower()}.exe",
                    )
            else:
                try:
                    retcode = subprocess.call(
                        f"{str(model_path)}/{model_name.lower()}.exe {self.environment.title}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except:
                    raise UnknownCommandError(
                        f"Unknown command: {str(model_path)}/{model_name.lower()}.exe"
                    )
        return retcode

    @staticmethod
    @contextlib.contextmanager
    def _working_directory(path):
        prev_cwd = Path.cwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(prev_cwd)
