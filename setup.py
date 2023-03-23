#!/usr/bin/env python3

from setuptools import setup


def setup_package():
    setup(
        name="TritonOA",
        url="https://github.com/NeptuneProjects/TritonOA",
        author="William F. Jenkins II",
        author_email="wjenkins@ucsd.edu",
        packages=["tritonoa"],
        install_requires=[
            "cmocean",
            "feather-format",
            "jupyterlab",
            "matplotlib",
            "numpy",
            "pandas",
            "scipy",
        ],
        version="0.0.2",
        license="MIT",
        description="Package provides interface to ocean acoustic modeling and \
            analysis tools.",
    )


if __name__ == "__main__":
    setup_package()
