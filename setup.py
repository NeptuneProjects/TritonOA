#!/usr/bin/env python3

from setuptools import find_packages, setup


def setup_package():
    setup(
        name="TritonOA",
        url="https://github.com/NeptuneProjects/TritonOA",
        author="William F. Jenkins II",
        author_email="wjenkins@ucsd.edu",
        packages=find_packages(),
        install_requires=[
            "cmocean",
            "feather-format",
            "jupyterlab",
            "matplotlib",
            "numpy",
            "pandas",
            "scipy",
            "tqdm",
        ],
        version="0.0.5",
        license="MIT",
        description="Package provides interface to ocean acoustic modeling and \
            analysis tools.",
    )


if __name__ == "__main__":
    setup_package()
